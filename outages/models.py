from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    String,
    DateTime,
    Boolean
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relation
    )

from sqlalchemy.orm.exc import (
    NoResultFound
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class UtilityConfig(Base):
    __tablename__ = "utility_configs"
    id = Column(Integer, primary_key=True)

    utility_id = Column(Integer, ForeignKey('utilities.id'))
    utility = relation('Utility', backref='config')

    #location_id = Column(Integer, ForeignKey('locations.id'))
    #location = relation('Location', backref='config')

    key = Column(String)
    value = Column(String)

class Utility(Base):
    __tablename__ = 'utilities'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    scraper_cls = Column(String)
    virtual = Column(Boolean, default=False)

    def get_config(self):
        config = {}
        for conf in self.config:
            config[conf.key] = conf.value

        return config

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    town = Column(String)
    county = Column(String)
    state = Column(String)
    stabbr = Column(String(2))

    utilityid = Column(Integer, ForeignKey('utilities.id'))
    utility = relation('Utility', backref='locations')

    @classmethod
    def add_location(cls, name, utility=None, town="", county="", state="", stabbr=""):
        try:
            existing = cls.query.filter(cls.name == name).one()
            return existing
        except NoResultFound:
            pass

        print "Adding new location: '%s'" % name
        print "\tbelongs to: %s" % utility

        l = cls()
        l.utility = utility
        l.name = name
        l.town = town
        l.county = county
        l.state = state
        l.stabbr = stabbr
        DBSession.add(l)

        return l


class Metric(Base):
    __tablename__ = 'metrics'

    id = Column(Integer, primary_key=True)
    shortname = Column(String(36))
    name = Column(String)

    @classmethod
    def add_metric(cls, name, long_name=""):
        try:
            existing = cls.query.filter(cls.shortname == name).one()
            return existing
        except NoResultFound:
            pass

        m = cls()
        m.shortname = name
        m.name = long_name
        DBSession.add(m)

        return m

    @classmethod
    def get_metric(cls, name):
        return cls.query.filter(cls.shortname == name).one()

class MetricValue(Base):
    __tablename__ = 'metric_values'
    id = Column(Integer, primary_key=True)

    metricid = Column(Integer, ForeignKey('metrics.id'))
    metric = relation('Metric', backref='values')

    locationid = Column(Integer, ForeignKey('locations.id'))
    location = relation('Location', backref='values')

    datetime = Column(DateTime)
    value = Column(Integer)

class MetricMetadata(Base):
    __tablename__ = 'metric_valuedatum'
    id = Column(Integer, primary_key=True)
    metricvalueid = Column(Integer, ForeignKey('metric_values.id'))
    metricvalue = relation('MetricValue', backref='metadata')

    key = Column(String)
    value = Column(String)
