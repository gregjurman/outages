# -*- coding: utf-8 -*-
"""Outage model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Integer, Unicode, DateTime, Boolean
#from sqlalchemy.orm import relation, backref

from rgeoutages.model import DeclarativeBase, metadata, DBSession
from datetime import datetime

import sqlamp

__all__ = ['Outage', 'Street', 'County', 'Town', 'Utility']

class Utility(DeclarativeBase):
    __tablename__ = 'utilities'
    
    id = Column(Integer, primary_key=True)

    key = Column(String, nullable=False, unique=True)

    name = Column(Unicode, nullable=False)

__all__ = ['Outage', 'Street', 'County', 'Town']

class Outage(DeclarativeBase):
    __tablename__ = 'outages'

    id = Column(Integer, primary_key=True)

    location_id = Column(Integer, ForeignKey('locations.id'))
    location = relation('LocationNode', backref='outages')

    start_time = Column(DateTime, default=(lambda: datetime.now()))
    proposed_end_time = Column(DateTime)
    end_time = Column(DateTime)
    
    affected_customers = Column(Integer, nullable=False)

class LocationNode(DeclarativeBase):
    __tablename__ = 'locations'
    __mp_manager__ = 'mp'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('node.id'))
    parent = relation("Node", remote_side=[id])
    name = Column(String, nullable=False)
    total_customers = Column(Integer)

    lat = Column(String)
    lng = Column(String)

    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
    def __repr__(self):
        return '<Node %r>' % self.name


class Street(DeclarativeBase):
    __tablename__ = 'streets'
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    
    street_name = Column(Unicode, nullable=False)
    town_id = Column(Integer, ForeignKey('towns.id'))
    town = relation('Town', backref="streets")

    lat = Column(String)
    lng = Column(String)

    total_customers = Column(Integer)

class Town(DeclarativeBase):
    __tablename__ = 'towns'

    id = Column(Integer, primary_key=True)

    town_name = Column(Unicode, nullable=False)
    county_id = Column(Integer, ForeignKey('counties.id'))
    county = relation('County', backref="towns")

    utility_id = Column(Integer, ForeignKey('utilities.id'))
    utility = relation('Utility', backref='towns')

    total_customers = Column(Integer)

class County(DeclarativeBase):
    __tablename__ = 'counties'

    id = Column(Integer, primary_key=True)

    county_name = Column(Unicode, nullable=False)
    
    total_customers = Column(Integer)
