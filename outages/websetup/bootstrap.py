# -*- coding: utf-8 -*-
"""Setup the outages application"""

import logging
from tg import config
from outages import model
import transaction
import tgscheduler

from outages.model import LocationNode, DBSession

def bootstrap(command, conf, vars):
    """Place any commands to setup outages here"""

    #Kill the scheduler
    tgscheduler.stop_scheduler()

    root_node = LocationNode(id=0, name="RootNode", location_level="ROOTNODE")

    DBSession.add(root_node)
    DBSession.flush()

    transaction.commit()
