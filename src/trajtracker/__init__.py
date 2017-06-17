#
# TrajTracker - a set of tools for psychological experiments under expyriment
#
# author: Dror Dotan
# Copyright (c) 2017, Dror Dotan

import expyriment as xpy

#-- Log levels (each level will also print the higher log levels)
log_trace = 1
log_debug = 2
log_info = 3
log_warn = 4
log_error = 5
log_none = 6

from ._Environment import Environment

#: :class:`~trajtracker.Environment` parameters
env = Environment()

#: When set to True, this will print all log messages to the console (on top of printing them
#: to the log file)
log_to_console = False


#----------------------------------------------------------
def version():
    """
    Return trajtracker version number ("major.minor.build")
    
    :return: str
    """
    return "0.1.01"


#----------------------------------------------------------
# TrajTracker types
TYPE_SIZE = "size"
TYPE_COORD = "coord"
TYPE_RGB = "RGB"
TYPE_CALLABLE = "callable"


#============================================================================
#   Exception classes
#============================================================================

class TrajTrackerError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{:}: {:}".format(type(self).__name__, self.message)


class InvalidStateError(TrajTrackerError):
    """ Exception indicating that a method was called when the object is an inappropriate state """
    pass


class BadFormatError(TrajTrackerError):
    """ Exception indicating that data was provided in an invalid format (e.g., in a file) """
    pass


# noinspection PyShadowingBuiltins
class ValueError(TrajTrackerError):
    """ Exception indicating that an invalid value was encountered """
    pass


# noinspection PyShadowingBuiltins
class TypeError(TrajTrackerError):
    """ Exception indicating that a value of invalid type was encountered """
    pass


# noinspection PyProtectedMember
from trajtracker._ttrk_funcs import log_write, initialize

#============================================================================
#   Import the TrajTracker modules
#============================================================================

# noinspection PyProtectedMember
from trajtracker._TTrkObject import TTrkObject

# noinspection PyProtectedMember
from . import _utils
from . import utils

from . import misc
from . import io
from . import events
from . import stimuli
from . import movement
from . import validators
from . import paradigms
