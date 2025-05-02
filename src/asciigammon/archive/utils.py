"""
utils.py
    Various helper functions
"""

import importlib

from ..core.logger import logger as LOGGER


def str_to_class(module_name: str, class_name: str):
    """
    Return a class instance from a string reference

    :param module_name: The name of the module containing the class.
    :type module_name: str
    :param class_name: The name of the class.
    :type class_name: str
    :return: An instance of a class
    :rtype: Any
    """
    class_ = None
    try:
        module_ = importlib.import_module(module_name)
        try:
            class_ = getattr(module_, class_name)
        except AttributeError:
            LOGGER.error(f"Class <{class_name}> does not exist")
    except ImportError:
        LOGGER.error(f"Module <{module_name}> does not exist")
    return class_
