from BeautifulSoup import BeautifulSoup
import urllib2
from datetime import datetime
from urlparse import urljoin
import json

from outages.scrapers import Scraper, Location, Outage

class OmniScraper(Scraper):
    def scrape(self, url, parent=None):
        print "Getting:", url
        soup = self.get_soup(url)
        table = self.extract_table(soup)

        update_time, location_level = self.get_metadata(table)

        if location_level is None:
            return
    
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
                try:
                    outage.proposed_end_time = datetime.strptime(cells[3].string, "%b %d, %Y %I:%M %p")
                except:
                    # no proposed time
                    pass

                loc.outage = outage

    def get_metadata(self, table):
        # Start extracting data
        update_time = self.get_update_time(table)
        location_level = self.get_location_level(table)
        
        return update_time, location_level


    def get_soup(self, url):
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
        if first_data_row is None:
            return None

        header_row = first_data_row.findPreviousSiblings('tr', limit=1)[0]

        loc_level = header_row.contents[0].string

        if not loc_level:
            loc_level = header_row.contents[0].contents[0].string

        return loc_level

if __name__ == "__main__":
    # Test function
    from outages.scrapers import JSONFuncEncoder

    ngs = OmniScraper('http://gregjurman.github.com')
    objs = ngs.start('http://gregjurman.github.com/RGE.html')

    print JSONFuncEncoder().encode(objs)
