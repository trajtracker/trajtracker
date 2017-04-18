"""

 traj tracker - a set of tools for psychological experiments under expyriment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import expyriment as xpy



#-- When set to True, this will print all log messages to the console (on top of printing them
#-- to the log file)
log_to_console = False


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


#============================================================================
#   Import the TrajTracker modules
#============================================================================

from __TTrkObject import TTrkObject

import trajtracker._utils as _utils

import trajtracker.misc as misc
import trajtracker.data as data
import trajtracker.events as events
import trajtracker.stimuli as stimuli
import trajtracker.movement as movement
import trajtracker.validators as validators
