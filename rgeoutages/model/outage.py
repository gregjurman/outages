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

__all__ = ['Outage', 'LocationNode', 'Utility']

class Utility(DeclarativeBase):
    __tablename__ = 'utilities'
    
    id = Column(Integer, primary_key=True)

    key = Column(String, nullable=False, unique=True)

    name = Column(Unicode, nullable=False)


class Outage(DeclarativeBase):
    __tablename__ = 'outages'

    id = Column(Integer, primary_key=True)

    location_id = Column(Integer, ForeignKey('locations.id'))
    location = relation('LocationNode', backref='outages')

    start_time = Column(DateTime, default=(lambda: datetime.now()))
    proposed_end_time = Column(DateTime)
    end_time = Column(DateTime)
    
    affected_customers = Column(Integer, nullable=False)

    utility_id = Column(Integer, ForeignKey('utilities.id'))
    utility = relation('Utility', backref='outages')


class LocationNode(DeclarativeBase):
    __tablename__ = 'locations'
    __mp_manager__ = 'mp'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('locations.id'))
    parent = relation("LocationNode", remote_side=[id])
    name = Column(String, nullable=False)
    total_customers = Column(Integer)

    location_level = Column(String, nullable=False)

    update_time = Column(DateTime)

    lat = Column(String)
    lng = Column(String)

    def __repr__(self):
        return '<Location %r>' % self.name
