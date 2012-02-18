from BeautifulSoup import BeautifulSoup
import urllib2
from datetime import datetime
from urlparse import urljoin
import json

#from rgeoutages.models import LocationNode, Outage, Utility, DBSession
#import transaction

class Outage(object):
    affected_customers = None
    proposed_end_time = None

    def __init__(self):
        pass

    def __str__(self):
        return "Outage: affected_customers=%s, proposed_end_time=%s" % (
            self.affected_customers, self.proposed_end_time)

    def __json__(self):
        return dict(
            affected_customers=self.affected_customers,
            proposed_end_time=self.proposed_end_time)

class Location(object):
    location_level = None
    locations = None
    outages = None
    update_time = None
    total_customers = None
    name = None

    def __init__(self):
        self.locations = []
        self.outages = []
        self.location_level = None

    def __str__(self):
        return "Location: name=%s, level=%s, total_outages=%s, total_children=%s, last_updated=%s" % (
            self.name, self.location_level, len(self.outages), len(self.locations), self.update_time)

    def __repr__(self):
        return str(self)

    def __json__(self):
        me = dict(
            name=self.name,
            total_customers=self.total_customers,
            update_time=self.update_time,
            location_level=self.location_level)

        if self.locations:
            me['locations'] = self.locations
        if self.outages:
            me['outages'] = self.outages

        return me

class OmniScraper(object):
    def __init__(self, base_url, start_page):
        self.base_url = base_url
        self.start_page = start_page

    def start(self):
        root_loc = Location()
        root_loc.location_level = 'Root'

        start_url = "%s/%s" % (self.base_url, self.start_page)

        self.scrape(start_url, root_loc)

        return root_loc

    def scrape(self, url, parent=None):
        soup = self.get_soup(url)
        table = self.extract_table(soup)

        update_time, location_level = self.get_metadata(table)

        first_data_row = None        
        # get all rows that have no attributes on them
        for row in table.findAll(lambda tag : tag.name == 'tr' and not tag.attrs):
            if not row.findAll('td'):
                continue

            first_data_row = row
            break

        # Get data-rows then prepend the first
        rows = first_data_row.findNextSiblings('tr')
        rows.insert(0, first_data_row)
        # The last row is junk we don't need
        rows.pop()

        locations = []

        for row in rows:
            loc = Location()
            loc.update_time = update_time
            loc.location_level = location_level
            if parent:
                parent.locations.append(loc)

            cells = row.findAll('td')

            loc.total_customers = int(cells[1].string.replace(',',''))
            out_customers = int(cells[2].string.replace(',',''))

            if cells[0].findAll('a'):
                # Theres more data here, recurse
                child_url = urljoin(url, cells[0].contents[0]['href'])
                loc.name = cells[0].contents[0].contents[0].string

                self.scrape(child_url, loc)
            else:
                # This is drilled-down as far as we can go, make an outage object
                loc.name = cells[0].string
                outage = Outage()
                outage.affected_customers = out_customers
                outage.proposed_end_time = datetime.strptime(cells[3].string, "%b %d, %Y %I:%M %p")

                loc.outages.append(outage)

    def get_metadata(self, table):
        # Start extracting data
        update_time = self.get_update_time(table)
        location_level = self.get_location_level(table)
        
        return update_time, location_level


    def get_soup(self, url):
        print "Getting URL:", url

        data = urllib2.urlopen(url)
        return BeautifulSoup(data)


    def extract_table(self, page_soup):
        # There should be one table
        return page_soup.findAll('table', limit=1)[0]


    def get_update_time(self, table_soup):
        # get the 'firstRow'
        row = table_soup.findAll('tr', attrs={'class':'firstRow'}, limit=1)[0]

        # Find the Update time cell
        cell = row.findAll('td', attrs={'align': 'right'}, limit=1)[0]

        # Parse out to datetime object
        return datetime.strptime(cell.string, "Update: %b %d, %Y %I:%M %p")


    def get_location_level(self, table_soup):
        first_data_row = None
        
        # get all rows that have no attributes on them
        for row in table_soup.findAll(lambda tag : tag.name == 'tr' and not tag.attrs):
            if not row.findAll('td'):
                continue

            first_data_row = row
            break

        # Get one row previous to that, which is the header row
        header_row = first_data_row.findPreviousSiblings('tr', limit=1)[0]

        loc_level = header_row.contents[0].string

        return loc_level


def serializer(obj):
    if isinstance(obj, Location) or isinstance(obj, Outage):
        return obj.__json__()
    else:
        return str(obj)

if __name__ == "__main__":
    test_scraper = OmniScraper('http://gregjurman.github.com', 'NYSEG.html')
    root_obj = test_scraper.start()

    print json.dumps(root_obj, default=serializer)
