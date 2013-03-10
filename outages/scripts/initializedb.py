#!/usr/bin/python
import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from outages.models import (
    DBSession,
    Utility,
    UtilityConfig,
    Location,
    Metric,
    MetricValue,
    Base,
    )

from outages.scrapers import (
    ScraperMeta
    )

natgrid_services = [
            {'key': 'natgrid',
            'name': "National Grid (NY)",
            'state': 'NY',
            'base':'https://www1.nationalgridus.com/StormCenterData/data/data_ny.xml'},
        ]

utilities = [
    {
        'name' : 'Rochester Gas & Electric',
        'scraper_cls' : 'OmniScraper',
        'config' : {
            'base_url' : 'http://www3.rge.com/OutageReports/',
            'start_file' : 'RGE.html',
            'state' : 'NY',
            }
        },
    {
        'name' : 'New York State Electric & Gas',
        'scraper_cls' : 'OmniScraper',
        'config' : {
            'base_url' : 'http://www3.nyseg.com/OutageReports/',
            'start_file' : 'NYSEG.html',
            'state' : 'NY'
            },
        },
    ]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    Base.query = DBSession.query_property()

    with transaction.manager:
        for utility in utilities:
            u = Utility()
            u.name = utility['name']
            u.scraper_cls = utility['scraper_cls']
            DBSession.add(u)
            DBSession.flush()

            for k, v in utility['config'].iteritems():
                uc = UtilityConfig()
                uc.utility = u
                uc.key = k
                uc.value = v
                DBSession.add(uc)
                DBSession.flush()

        for k, v in ScraperMeta.registered_scrapers.iteritems():
            print "Adding metrics for scraper %s" % k
            v().initialize_db()

if __name__ == "__main__":
    main()

