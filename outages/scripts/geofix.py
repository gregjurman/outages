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
    Base.metadata.bind = engine
    Base.query = DBSession.query_property()

    with transaction.manager:
        utilities = DBSession.query(Utility).all()
        for utility in utilities:
            print "Running geofix for '%s'" % utility.name
            cls = ScraperMeta.get_scraper_by_name(utility.scraper_cls)
            config = utility.get_config()

            scraper = cls(utility, **config)

            try:
                print "Fixing geo-location information..."
                scraper.geofix()
            except NotImplemented:
                print "No geofix function, skipping..."
                pass

    print "Done"

if __name__ == "__main__":
    main()

