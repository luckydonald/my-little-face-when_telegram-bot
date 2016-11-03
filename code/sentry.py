# -*- coding: utf-8 -*-
from sys import path

import raven
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
from luckydonaldUtils.logger import logging


__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


def add_error_reporting(app):
    sentry = Sentry(app)  # set SENTRY_DSN env!
    handler = SentryHandler(sentry, level=logging.WARNING)
    raven.conf.setup_logging(handler)
    app.add_url_rule('/sentry', 'is_sentry', is_sentry(sentry))
    return sentry
# end def


def is_sentry(sentry):
    def view():
        return "{}".format(sentry)
    # end if
# end if