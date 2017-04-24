"""

 traj tracker - a set of tools for psychological experiments under expyriment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import expyriment as xpy

#-- Log levels (each level will also print the higher log levels)
log_trace = 1
log_debug = 2
log_info = 3
log_warn = 4
log_error = 5
log_none = 6


#-- When set to True, this will print all log messages to the console (on top of printing them
#-- to the log file)
log_to_console = False

#-- The default logging level for all trajtracker objects.
#-- If you change this, only objects created from now on will be affected.
default_log_level = log_warn


def version():
    return "0.0.1"


#============================================================================
#   Exception classes
#============================================================================

class TrajTrackerError(StandardError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "{:}: {:}".format(type(self).__name__, self.message)

class InvalidStateError(TrajTrackerError):
    """ A method was called when the object is an inappropriate state """
    pass

class BadFormatError(TrajTrackerError):
    """ Data was provided in an invalid format (e.g., in a file) """
    pass

class ValueError(TrajTrackerError):
    """ An invalid value was encountered """
    pass

class TypeError(TrajTrackerError):
    """ a value of invalid type was encountered """
    pass


from _ttrk_funcs import log_write

#============================================================================
#   Import the TrajTracker modules
#============================================================================

from _TTrkObject import TTrkObject

import trajtracker._utils as _utils

from . import misc
from . import data
from . import events
from . import stimuli
from . import movement
from . import validators
