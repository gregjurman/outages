# -*- coding: utf-8 -*-
"""Setup the rgeoutages application"""

import logging
from tg import config
from rgeoutages import model
import transaction
import tgscheduler

from rgeoutages.model import LocationNode, DBSession

def bootstrap(command, conf, vars):
    """Place any commands to setup rgeoutages here"""

    #Kill the scheduler
    tgscheduler.stop_scheduler()

    root_node = LocationNode(id=0, name="RootNode", location_level="ROOTNODE")

    DBSession.add(root_node)
    DBSession.flush()

    transaction.commit()
