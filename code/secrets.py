# -*- coding: utf-8 -*-
from luckydonaldUtils.logger import logging
import os

__author__ = 'luckydonald'
logger = logging.getLogger(__name__)


API_KEY = os.getenv('TG_API_KEY', None)
assert(API_KEY is not None)  # TG_API_KEY environment variable

HOSTNAME = os.getenv('TG_HOSTNAME', None)
# can be None

