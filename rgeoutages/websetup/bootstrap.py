# -*- coding: utf-8 -*-
"""Setup the rgeoutages application"""

import logging
from tg import config
from rgeoutages import model
import transaction

def bootstrap(command, conf, vars):
    """Place any commands to setup rgeoutages here"""

    # <websetup.bootstrap.before.auth

    # <websetup.bootstrap.after.auth>
