from rgeoutages.lib import rge_scraper
from rgeoutages.model import Outage, Street, Town, County, DBSession
import transaction
from urllib import quote_plus as _q
import urllib2
import json
from datetime import datetime

def get_lat_long(state='NY', town=None, street=None):
    query_string = _q("%s, %s, %s" % (street, town, state))
    uri = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % query_string
    obj = urllib2.urlopen(uri)
    json_data = json.load(obj)
    lat_long = json_data['results'][0]['geometry']['location']

    return lat_long['lat'], lat_long['lng']

def scrape_outages():
    outages = rge_scraper.update_outages()

    # Clear old outages
    for o_obj in Outage.query.all():
        DBSession.delete(o_obj)

    transaction.commit()

    # Crawl counties
    for c_name, c_data in outages.iteritems():
        county = None
        tot_cust = int(c_data['TotalCustomers'].replace(',', ''))
        county_query = County.query.filter(County.county_name==c_name)
        if county_query.count():
            # Already exists just update the key
            county_query.update({County.total_customers : tot_cust})
            transaction.commit()
            
            county = county_query.one()
        else:
            # Doesn't exist, add new county
            county = County()
            county.county_name = c_name
            county.total_customers = tot_cust
            DBSession.add(county)
            DBSession.flush()
            transaction.commit()

        # Do towns
        for t_name, t_data in c_data['Towns'].iteritems():
            town = None
            town_cust = int(t_data['TotalCustomers'].replace(',', ''))
            town_query = Town.query.filter(Town.town_name==t_name)
            if town_query.count():
                # Already exists just update the key
                town_query.update({Town.total_customers : town_cust})
                transaction.commit()

                town = town_query.one()
            else:
                # Doesn't exist, add new town
                town = Town()
                town.town_name = t_name
                town.total_customers = town_cust
                town.county = county
                DBSession.add(town)
                DBSession.flush()
                transaction.commit()

            # Do streets
            for s_name, s_data in t_data['Streets'].iteritems():
                street = None
                street_cust = int(s_data['TotalCustomers'].replace(',', ''))
                street_query = Street.query.filter(Street.street_name==s_name)
                if street_query.count():
                    # Already exists just update the key
                    street_query.update({Street.total_customers : street_cust})
                    transaction.commit()

                    street = street_query.one()
                else:
                    # Doesn't exist, add new street
                    street = Street()
                    street.street_name = s_name
                    street.total_customers = street_cust
                    street.town = town
                    # get the lat, long
                    lat, lng = get_lat_long('NY', t_name, s_name)
                    street.lat = lat
                    street.long = lng
                    DBSession.add(street)
                    DBSession.flush()
                    transaction.commit()

                # Create new outage
                outage = Outage()
                outage.street = street
                outage.proposed_end_time = datetime.strptime(s_data['EstimatedRestoration'], "%b %d, %Y %I:%M %p")
                outage.affected_customers = int(s_data['CustomersWithoutPower'].replace(',', ''))
                DBSession.add(outage)
                DBSession.flush()
                
                transaction.commit()
