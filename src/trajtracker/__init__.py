"""

 traj tracker - a set of tools for psychological experiments under expyriment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

log_to_console = False


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



import expyriment as xpy


class _TTrkObject(object):

    def __init__(self):
        self.log_level = self.log_warn


    #-- Log levels (each level will also print the higher log levels)
    log_trace = 1
    log_debug = 2
    log_info = 3
    log_warn = 4
    log_error = 5
    log_none = 6

    @property
    def log_level(self):
        """
        Logging level of this object: log_none, log_error (default), log_warn, log_info, log_debug, log_trace
        """
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        if level is None or not isinstance(level, int) or level < _TTrkObject.log_trace or level > _TTrkObject.log_none:
            raise trajtracker.ValueError("invalid log_level({:})".format(level))

        self._set_log_level(level)


    def _set_log_level(self, level):
        self._log_level = level


    #--------------------------------------------
    # Check if the object should log a message of the given level
    #
    def _should_log(self, message_level):
        return message_level >= self._log_level


    #-------------------------------------------------
    # Write to log after a property was set
    #
    def _log_property_changed(self, attr_name, value=None):

        if not self._should_log(self.log_trace):
            return

        if value is None:
            value = str(self.__getattribute__(attr_name))

        if len(value) > 100:
            value = value[:100]

        self._log_write("set_obj_attr,{:}.{:},{:}".format(type(self).__name__, attr_name, value))


    #-------------------------------------------------
    def _log_write_if(self, log_level, msg, prepend_self=False, print_to_console=False):
        if not self._should_log(log_level):
            return
        if prepend_self:
            msg = type(self).__name__ + "," + msg
        xpy._internals.active_exp._event_file_log(msg, 1)
        if log_to_console or print_to_console:
            print(msg)

    #-------------------------------------------------
    def _log_write(self, msg, prepend_self=False, print_to_console=False):
        if prepend_self:
            msg = type(self).__name__ + "," + msg
        xpy._internals.active_exp._event_file_log(msg, 1)
        if log_to_console or print_to_console:
            print(msg)

    #-------------------------------------------------
    # Write to log when entering a function
    #
    def _log_func_enters(self, func_name, args=()):
        if self._should_log(self.log_trace):
            args = ",".join([str(a) for a in args])
            self._log_write("enter_func,{:}({:})".format(func_name, args), prepend_self=True)


    #-------------------------------------------------
    # Write to log when function returns a value
    #
    def _log_func_returns(self, func_name, retval=None):
        if self._should_log(self.log_trace):
            self._log_write("func_returns,{:},{:}".format(func_name, retval), prepend_self=True)




import trajtracker._utils as _utils

import trajtracker.misc as misc
import trajtracker.data as data
import trajtracker.events as events
import trajtracker.stimuli as stimuli
import trajtracker.movement as movement
import trajtracker.validators as validators
