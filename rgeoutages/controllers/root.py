# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from rgeoutages.model import DBSession, metadata

from rgeoutages.lib.base import BaseController
from rgeoutages.controllers.error import ErrorController

from tw2.polymaps import PolyMap, PollingPolyMap
from tw2.polymaps.geojsonify import geojsonify

from tw2.protovis.custom import SparkBar

import math
import random

__all__ = ['RootController']

class RGEOutageChart(SparkBar):
    id = "outage_chart"
    p_width = 125
    p_left = 0    
    p_right = 0
    p_top = 0
    p_bottom = 0
    p_height = 25
    p_data = [1.0, 0.3, 0.6, 0.1, 0.9, 0.8, 0.23, 0.77, 0.63, 0.43, 0.59, 0.11,
            1.0, 0.3, 0.6, 0.1, 0.9, 0.8, 0.23, 0.77, 0.63, 0.43, 0.59, 0.11]

class RGEOutageMap(PollingPolyMap):
    """
    This is the polymap object that displays the current outages in the 
    RG&E Service Area
    """
    id = "outage_map"
    interval = 60000
    layer_lifetime = 60100
    interact = True
    cloudmade_api_key = "1a1b06b230af4efdbb989ea99e9841af"
    center_latlon = {'lat': 43.165556, 'lon' : -77.611389}
    css_class = "outage_map"
    zoom = 11

    data_url = "/outages.json"

class RootController(BaseController):
    """
    The root controller for the rgeoutages application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    error = ErrorController()

    @expose('rgeoutages.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index',
            outage_map=RGEOutageMap(),
            outage_chart=RGEOutageChart())

    @expose()
    def outages(self):
        """Handle the current outages and return a JSON feed"""
        import geojson

        n = 40
        lat, lon = 43.165556, -77.611389
        mod = lambda x : x + random.random() * 0.05 - 0.025

        json = geojson.FeatureCollection(
            features=[
                geojson.Feature(
                    geometry=geojson.Point([mod(lon), mod(lat)]),
                    properties={'ATTR': "%s, %s" % (mod(lon), mod(lat))},
                ) for i in range(n)

            ]
        )
        return geojson.dumps(json)

