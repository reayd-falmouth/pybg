"""logger.py"""

import logging
from os import getenv

logger = logging.getLogger(__name__)
logger.propagate = True
logger.setLevel(level=getenv("LOG_LEVEL", "DEBUG"))
