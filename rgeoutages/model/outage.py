# -*- coding: utf-8 -*-
"""Outage model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, DateTime, Numeric, Boolean
#from sqlalchemy.orm import relation, backref

from rgeoutages.model import DeclarativeBase, metadata, DBSession


class Outage(DeclarativeBase):
    __tablename__ = 'outages'
    
    #{ Columns
    
    id = Column(Integer, primary_key=True)
    
    street_name = Column(Unicode)
    town_name = Column(Unicode)
    lat = Column(Numeric)
    long = Column(Numeric)
    
 
