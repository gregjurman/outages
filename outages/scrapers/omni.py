from BeautifulSoup import BeautifulSoup
import urllib2
from datetime import datetime
from urlparse import urljoin
import json
from itertools import izip

from outages.models import Location, Metric, MetricValue, MetricMetadata, DBSession
from outages.scrapers import Scraper

import transaction

class OmniScraper(Scraper):
    metrics = {
            'affected' : 'Affected Customers',
            'total' : 'Total Customers'
            }

    def geofix(self):
        # Get all Locations that have missing town names
        properties = list(reversed([None, 'town', None, 'county', 'stabbr']))
        fixables = Location.query.filter(Location.utility == self.utility).filter(
                Location.stabbr == "").all()

        # For each record, fill in missing data
        for loc in fixables:
            print "Fixing '%s'" % loc.name
            sections = reversed([x.strip() for x in loc.name.split(',')])
            for section, prop in zip(sections, properties):
                if prop:
                    print "updating '%s': '%s' with %s" % (loc.name, prop, section)
                    setattr(loc, str(prop), section)

    def initialize_db(self):
        for k,v in self.metrics.iteritems():
            m = Metric.add_metric(k, v)
        DBSession.flush()

    def scrape(self):
        base_url = self.config['base_url']
        url = urljoin(base_url, self.config['start_file'])
        state_abbr = self.config['state']

        # Declare our commit time
        self.commit_time = datetime.now()

        # Start scraping, Always append the state suffix
        self.scrape_recurse(url, state_abbr)

    def scrape_recurse(self, url, suffix=""):
        print "Getting URL: %s\n\twith suffix: %s" % (url, suffix)

        soup = self.get_soup(url)
        location = self.get_metadata(soup)
        data_rows = self.get_rows(soup)
        if not data_rows:
            return

        for row in data_rows:
            name, total, out, found_page, end_time = self.extract_data(row)

            # Set our location if needed
            full_name = ", ".join([name, suffix])
            l = Location.add_location(full_name, self.utility)

            # log out customers
            # XXX: DRY this out
            mv_out = MetricValue()
            mv_out.metric = Metric.get_metric('affected')
            mv_out.location = l
            mv_out.value = out
            mv_out.datetime = self.commit_time
            DBSession.add(mv_out)

            if (end_time):
                out_md = MetricMetadata()
                out_md.metricvalue = mv_out
                out_md.key = 'end_time'
                out_md.value = end_time
                DBSession.add(out_md)

            # log total customers
            mv_tot = MetricValue()
            mv_tot.metric = Metric.get_metric('total')
            mv_tot.location = l
            mv_tot.value = total
            mv_tot.datetime = self.commit_time
            DBSession.add(mv_tot)

            DBSession.flush()

            # Take all found pages and recurse through them
            if found_page:
                new_page = urljoin(url, found_page)
                self.scrape_recurse(new_page, full_name)

    def get_soup(self, url):
        # Open the URL and start the soup
        data = urllib2.urlopen(url)
        return BeautifulSoup(data)

    def extract_table(self, soup):
        # There should be one table
        return soup.findAll('table', limit=1)[0]

    def find_first_data_row(self, soup):
        # get all rows that have no attributes on them
        # find the first row that has <td/> tags
        table = self.extract_table(soup)
        for row in table.findAll(lambda tag : tag.name == 'tr' and not tag.attrs):
            if not row.findAll('td'):
                continue

            return row

    def get_rows(self, soup):
        # Retrive all of the rows that contain data
        first_data_row = self.find_first_data_row(soup)
        try:
            rows = first_data_row.findNextSiblings('tr')
        except AttributeError:
            return None

        rows.insert(0, first_data_row)

        # The last row is always junk we don't need
        rows.pop()
        return rows

    def extract_data(self, row):
        # Extract all of the pertinent data
        end_time = None
        name = None
        found_page = None

        cells = row.findAll('td')

        total = int(cells[1].string.replace(',',''))
        out = int(cells[2].string.replace(',',''))

        if cells[0].findAll('a'):
            # Theres a link leading to more data, save it
            child_url = cells[0].contents[0]['href']
            name = cells[0].contents[0].contents[0].string

            found_page = child_url
        else:
            # This is drilled-down as far as we can go, make an outage object
            name = cells[0].string
            try:
                end_time = datetime.strptime(cells[3].string, "%b %d, %Y %I:%M %p")
            except:
                # no proposed time
                pass

        return (name, total, out, found_page, end_time)

    def get_metadata(self, soup):
        # Get the basic metadata off the pace
        table = self.extract_table(soup)
        location_level = self.get_location_level(table)
        return location_level


    def get_location_level(self, table):
        first_data_row = None

        # get all rows that have no attributes on them
        for row in table.findAll(lambda tag : tag.name == 'tr' and not tag.attrs):
            if not row.findAll('td'):
                continue

            first_data_row = row
            break

        # Get one row previous to that, which is the header row
        if first_data_row is None:
            return None

        header_row = first_data_row.findPreviousSiblings('tr', limit=1)[0]

        loc_level = header_row.contents[0].string

        if not loc_level:
            loc_level = header_row.contents[0].contents[0].string

        return loc_level

