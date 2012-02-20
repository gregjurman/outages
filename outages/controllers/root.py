# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_
from outages.model import DBSession, metadata, Outage

from outages.lib.base import BaseController
from outages.controllers.error import ErrorController

from outages.util.cron_jobs import build_geo_chain

from tw2.polymaps import PolyMap, PollingPolyMap
from tw2.polymaps.geojsonify import geojsonify

from tw2.protovis.custom import SparkBar

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
    center_latlon = {'lat': 43.105556, 'lon' : -76.611389}
    css_class = "outage_map"
    zoom = 4

    data_url = "/outages.json"
    properties_callback = """function (_layer) {
        _layer.on("load", org.polymaps.stylist().attr('class', function(d){return ""+d.properties.CLASS})
        .title(function(d) { return ""+d.properties.ATTR }));
        return _layer
    }"""

class RootController(BaseController):
    """
    The root controller for the outages application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    error = ErrorController()

    @expose('outages.templates.index')
    def index(self):
        """Handle the front-page."""
        # Get num of outages
        outage_count = Outage.query.count()

        # Get affected customer count
        affected_count = 0
        for out in Outage.query.all():
            affected_count = affected_count + out.affected_customers

        return dict(outage_count=outage_count,
            affected_count=affected_count,
            outage_map=RGEOutageMap(),
            outage_chart=RGEOutageChart())

    @expose()
    def outages(self):
        """Handle the current outages and return a JSON feed"""
        import geojson

        features = []
        for outage in Outage.query.all():
            if outage.location.lng is not None:
                features.append(geojson.Feature(
                        geometry=geojson.Point([float(outage.location.lng), float(outage.location.lat)]),
                        properties={'CLASS': str(outage.utility.key),
                            'ATTR': ", ".join(build_geo_chain(outage.location))}))

        json = geojson.FeatureCollection(features=features)

        return geojson.dumps(json)

