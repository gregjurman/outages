# -*- coding: utf-8 -*-
"""Outage model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import String, Integer, Unicode, DateTime, Boolean
#from sqlalchemy.orm import relation, backref

from rgeoutages.model import DeclarativeBase, metadata, DBSession
from datetime import datetime

__all__ = ['Outage', 'Street', 'County', 'Town', 'Utility']

class Utility(DeclarativeBase):
    __tablename__ = 'utilities'
    
    id = Column(Integer, primary_key=True)

    key = Column(String, nullable=False, unique=True)

    name = Column(Unicode, nullable=False)


class Outage(DeclarativeBase):
    __tablename__ = 'outages'

    id = Column(Integer, primary_key=True)

    street_id = Column(Integer, ForeignKey('streets.id'))
    street = relation('Street', backref='outages')

    start_time = Column(DateTime, default=(lambda: datetime.now()))
    proposed_end_time = Column(DateTime)
    end_time = Column(DateTime)
    
    affected_customers = Column(Integer, nullable=False)

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
