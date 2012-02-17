# -*- coding: utf-8 -*-
import tgscheduler
from rgeoutages.util import cron_jobs
"""The application's Globals object"""

__all__ = ['Globals']


class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        """Start the TG Scheduler and add the scraper cron jobs"""

        # Start scheduler
        tgscheduler.start_scheduler()

        # Add scraper cron job, every 10 minutes
        # tgscheduler.scheduler.add_interval_task(self.sch_update_feeds, 600)
