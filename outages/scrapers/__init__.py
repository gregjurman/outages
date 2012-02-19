import json

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
            proposed_end_time=str(self.proposed_end_time))

class Location(object):
    location_level = None
    locations = None
    outage = None
    update_time = None
    total_customers = None
    name = None

    def __init__(self):
        self.locations = []
        self.location_level = None

    def __str__(self):
        return "Location: name=%s, level=%s, outage=%s, total_children=%s, last_updated=%s" % (
            self.name, self.location_level, self.outage, len(self.locations), self.update_time)

    def __repr__(self):
        return str(self)

    def __json__(self):
        me = dict(
            name=self.name,
            total_customers=self.total_customers,
            update_time=str(self.update_time),
            location_level=self.location_level)

        if self.locations:
            me['locations'] = self.locations
        if self.outage:
            me['outage'] = self.outage

        return me

class JSONFuncEncoder(json.JSONEncoder):
    def default(self, obj):
        return getattr(obj, '__json__', (lambda: json.JSONEncoder.default(self, obj)))()

class Scraper(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def start(self, start_url):
        root_loc = Location()

        self.scrape(start_url, root_loc)

        return root_loc

    def scrape(self, url, parent=None):
        pass

# Put Scraper libraries here
from outages.scrapers.omni import OmniScraper # RGE/NYSEG
