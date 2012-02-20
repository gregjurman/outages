from lxml import etree
import urllib2
from datetime import datetime
from urlparse import urljoin
import json

from posixpath import join

from outages.scrapers import Scraper, Location, Outage

import re

LOCATION_LEVELS = ['state', 'county', 'town']

class NationalGridScraper(Scraper):
    update_time = None
    name_regex = re.compile(r'([\w\s\d]+)(?:\([\w]+\)){0,1}')
    extranous_name_regex = re.compile(r'([\w\s]+) (?:Town|City|Village)$')
    etr = None

    def __init__(self):
        pass

    def scrape(self, url, parent=None):
        soup = self.get_xml_soup(url)

        root = soup.getroot()

        if not self.update_time:
            self.update_time = self.get_update_time(root)
            self.etr = self.get_etr(root, "//curr_custs_aff/areas/area")

        loc_tree = self.scrape_recurse(root, "//curr_custs_aff/areas/area", parent)


    def scrape_recurse(self, soup, xpath, parent, level=0):
        loc_name = self.get_area_name(soup, xpath)
        loc_total_custs = self.get_total_customers(soup, xpath)

        loc = Location()
        loc.name = loc_name
        loc.location_level = LOCATION_LEVELS[level]
        loc.update_time = self.update_time
        loc.total_customers = loc_total_custs

        if parent:
            parent.locations.append(loc)

        if len(soup.xpath(join(xpath, 'areas'))):
            # This is a location with more children
            for i in xrange(1, len(soup.xpath(join(xpath, 'areas', 'area'))) + 1):
                self.scrape_recurse(soup, join(xpath, 'areas', 'area[%s]' % i),
                    loc, level + 1)

        else:
            # This is a area that may have an outage
            out_custs = self.get_out_customers(soup, xpath)
            if out_custs:
                outage = Outage()
                outage.affected_customers = out_custs
                etr = self.get_etr(soup, xpath)
                if etr:
                    outage.proposed_end_time = etr
                else:
                    outage.proposed_end_time = self.etr

                loc.outage = outage

        return loc

    def get_xml_soup(self, url):
        c = urllib2.urlopen(url)
        return etree.parse(c)

    def get_area_name(self, soup, xpath):
        raw_name = soup.xpath(join(xpath, 'area_name', "text()"))[0]
        stripped_name = self.name_regex.match(raw_name).groups()[0].strip()
        
        # Need to strip the extranous Town, Village, City from the name though
        res = self.extranous_name_regex.match(stripped_name)

        if res:
            return res.groups()[0].strip()
        else:
            return stripped_name


    def get_total_customers(self, soup, xpath):
        return int(soup.xpath(join(xpath, 'total_custs', 'text()'))[0].replace(',',''))

    def get_out_customers(self, soup, xpath):
        return int(soup.xpath(join(xpath, 'custs_out', 'text()'))[0].replace(',',''))

    def get_update_time(self, soup):
        raw_date = soup.xpath(join("/root/date_generated", "text()"))

        if len(raw_date) is 1:
            d = datetime.strptime(raw_date[0], "%b %d, %I:%M %p")
            # We don't get the year, so replace the year with the proper year
            d = d.replace(datetime.now().year)
        else:
            d = datetime.now()

        return d

    def get_etr(self, soup, xpath):
        d = None
        raw = soup.xpath(join(xpath, "etr", "text()"))

        if raw:
            d = datetime.strptime(raw[0], "%b %d, %I:%M %p")
            # We don't get the year, so replace the year with the proper year
            d = d.replace(datetime.now().year)

        return d


if __name__ == "__main__":
    # Test function
    from outages.scrapers import JSONFuncEncoder

    ngs = NationalGridScraper()
    objs = ngs.start('http://gregjurman.github.com/data_ny.xml')

    print JSONFuncEncoder().encode(objs)
