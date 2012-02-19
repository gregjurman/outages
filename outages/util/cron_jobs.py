from outages.model import Outage, LocationNode, Utility, DBSession
import transaction
from urllib import quote_plus as _q
import urllib2
import json
from datetime import datetime
from sqlalchemy import and_

import re

from outages.util.scraper import OmniScraper

LOCATION_QUALIFIERS = {
    'state' : r'state',
    'town' : r'town([^\w]|$)',
    'county' : r'county',
    'street': r'street'}

LOCATION_CHAIN = ['street', 'town', 'state']


def get_lat_long(raw):
    query_string = _q(raw)
    uri = "http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false" % query_string
    obj = urllib2.urlopen(uri)
    json_data = json.load(obj)
    try:
        lat_long = json_data['results'][0]['geometry']['location']
    except:
        return None, None

    return lat_long['lat'], lat_long['lng']

def scrape_outages():
    omni_services = [
            {'key': 'nyseg',
            'name':'Test NYSEG',
            'state' : 'NY',
            'base':'http://gregjurman.github.com', 
            'start':'NYSEG.html'},
            {'key': 'rge',
            'name':'Rochester Gas & Electric',
            'state': 'NY',
            'base':'http://gregjurman.github.com', 
            'start':'RGE.html'},
            #{'key': 'nyseg',
            #'name': 'New York State Electric & Gas',
            #'base': 'http://www3.nyseg.com/OutageReports/',
            #'start':'NYSEG.html'}
        ]

    for omni_utility in omni_services:
        scrape_omni_outages_url(omni_utility)

    update_geo_locations()

def get_location_qualifier(raw):
    raw = raw.lower()
    for qualifier, test in LOCATION_QUALIFIERS.iteritems():
        if re.search(test, raw):
            return qualifier

    # Bah, no qualifier found, just use the lower-case
    return raw.lower()

def build_geo_chain(loc_node):
    i = 1
    chain = []
    chain.append(loc_node.name)
    p = loc_node.parent
    while p and i < len(LOCATION_CHAIN):
        if p.location_level == LOCATION_CHAIN[i]:
            chain.append(p.name)
            i = i + 1
        p = p.parent

    return chain

def update_geo_locations():
    # Process the Location
    for obj in LocationNode.query.filter(LocationNode.location_level==LOCATION_CHAIN[0]):
        if obj.lat is None and obj.lng is None:
            chain = build_geo_chain(obj)
            # Get a lat/lng from Google
            lat, lng = get_lat_long(', '.join(chain))

            # Update object
            if lat is not None and lng is not None:
                obj.lat = str(lat)
                obj.lng = str(lng)

    DBSession.flush()
    transaction.commit()

def scrape_omni_outages_url(service):
    #TODO: Pull this out to generic it
    # Get the utility entry, else create one if it's missing
    utility = None
    utility_query = Utility.query.filter(Utility.key==service['key'])
    if utility_query.count():
        utility = utility_query.one()
    else:
        # Doesn't exist, add new utility
        utility = Utility()
        utility.key = service['key']
        utility.name = service['name']
        DBSession.add(utility)
        DBSession.flush()


    # Clear all outages
    for o_obj in Outage.query.all():
        if o_obj.utility is utility:
            DBSession.delete(o_obj)

    # Get data from Omni
    scraper = OmniScraper(service['base'], service['start'])

    outage_data = scraper.start()
    
    # Setup the root Location as the State
    outage_data.name = service['state']
    outage_data.location_level = 'state'
    
    tot_custs = 0
    for child in outage_data.locations:
        if not outage_data.update_time:
            outage_data.update_time = child.update_time
        tot_custs = tot_custs + child.total_customers
    
    outage_data.total_customers = tot_custs

    populate_database(outage_data, utility)


def populate_database(data, utility):
    root_obj = LocationNode.query.filter(LocationNode.id==0).one()
    populate(data, root_obj, utility)


def populate(data, parent, utility):
    loc_qual = get_location_qualifier(data.location_level)
    loc_filter = LocationNode.query.filter(and_(
        LocationNode.name==data.name,
        LocationNode.location_level==loc_qual))

    if loc_filter.count():
        #Object exists, lets grab it
        loc = loc_filter.one()
    else:
        loc = LocationNode()
        loc.name = data.name
        loc.parent = parent
        loc.location_level = loc_qual
        loc.total_customers = data.total_customers
        loc.update_time = data.update_time
        DBSession.add(loc)
        DBSession.flush()

    for child_loc in data.locations:
        populate(child_loc, loc, utility)

    if data.outage:
        if not loc.outages:
            outage = Outage()
            outage.location = loc
            outage.utility = utility
            outage.affected_customers = data.outage.affected_customers
            outage.proposed_end_time = data.outage.proposed_end_time
            DBSession.add(outage)
            DBSession.flush()

    transaction.commit()
