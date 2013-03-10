import json

class ScraperMeta(type):
    registered_scrapers = {}

    def __new__(mcs, name, bases, dct):
        if name is "Scraper":
            return type.__new__(mcs, name, bases, dct)

        ins = type.__new__(mcs, name, bases, dct)
        mcs.register(ins, name)

        return ins

    @classmethod
    def register(mcs, cls, name):
        print "Registering Scraper: %s" % name
        mcs.registered_scrapers[name.lower()] = cls

    @classmethod
    def get_scraper_by_name(mcs, name):
        return mcs.registered_scrapers[name.lower()]

class Scraper(object):
    __metaclass__ = ScraperMeta

    def __init__(self, utility=None, **config):
        self.utility = utility
        self.config = config

    def initialize_db(self):
        pass

    def start(self):
        print "Starting %s, %s" % (self.utility, self.config)
        return self.scrape()

    def scrape(self):
        raise NotImplemented("scrape function not defined!")

    def geofix(self):
        raise NotImplemented("no geofix function defined")

# Put Scraper libraries here
from outages.scrapers.omni import OmniScraper # RGE/NYSEG
