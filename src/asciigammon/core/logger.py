"""logger.py"""

from os import getenv

import logging

logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(level=getenv("LOG_LEVEL", "DEBUG"))
