from lxml import etree
import urllib2
from datetime import datetime
from urlparse import urljoin
import json

import pprint

from posixpath import join, dirname

from outages.scrapers import Scraper, Location, Outage

import re

class NationalGridScraper(Scraper):

    def __init__(self):
        pass

    def scrape(self, url, parent=None):
        """
        Get the interval generation file and parse out the data directory.
        Take the data directory and get the JSON file with the outage report.

        url : URL for the main metadata file.asename
        """
        base_url = dirname(url)
        metadata_soup = self.get_xml_soup(url)
        meta_path = self.get_metadata_path(metadata_soup)

        report_url = join(base_url, meta_path, "report.js")

        report_json = self.get_report_json(report_url)

        return self.scrape_recurse(
                report_json['file_data']['curr_custs_aff'], parent)

    def scrape_recurse(self, data, parent=None):
        me = Location()
        if 'area_name' in data.keys():
            me.name = data['area_name'].strip()

        if 'total_custs' in data.keys():
            custs = data['total_custs']
            me.total_customers = custs

        if 'custs_out' in data.keys():
            out = data['custs_out']
            etr = data['etrmillis']
            if out > 0:
                outage = Outage()
                outage.affected_customers = out
                if etr >= 0:
                    outage.proposed_end_time = datetime.fromtimestamp(etr/1000.0)

                me.outage = outage

        if 'areas' in data.keys():
            for area in data['areas']:
                self.scrape_recurse(area, me)

        if parent:
            parent.locations.append(me)

    def get_report_json(self, url):
        print url
        c = urllib2.urlopen(url)
        return json.loads(c.read())

    def get_xml_soup(self, url):
        c = urllib2.urlopen(url)
        return etree.parse(c)

    def get_metadata_path(self, metadata_soup):
        raw = metadata_soup.xpath("//root/directory/text()")
        return raw.pop()


    def get_etr(self, soup, xpath):
        d = None
        raw = soup.xpath(join(xpath, "etr", "text()"))

        if raw:
            try:
                d = datetime.strptime(raw[0], "%b %d, %I:%M %p")
                # We don't get the year, so replace the year with the proper year
                d = d.replace(datetime.now().year)
            except:
                pass

        return d

if __name__ == "__main__":
    # Test function
    from outages.scrapers import JSONFuncEncoder

    ngs = NationalGridScraper()
    objs = ngs.start('https://s3.amazonaws.com/stormcenter.nationalgridus.com/data/interval_generation_data/metadataNY.xml')

    print JSONFuncEncoder().encode(objs)
