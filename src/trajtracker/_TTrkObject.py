"""

Base class for all TrajTracker objects

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

This file is part of TrajTracker.

TrajTracker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TrajTracker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TrajTracker.  If not, see <http://www.gnu.org/licenses/>.
"""


import time

import expyriment as xpy

import trajtracker as ttrk


class TTrkObject(object):

    #--------------------------------------------
    def __init__(self):
        self.log_level = ttrk.env.default_log_level


    #--------------------------------------------
    @property
    def log_level(self):
        """
        Logging level of this object: trajtracker.log_none, log_error (default), log_warn,
        log_info, log_debug, log_trace
        """
        return self._log_level

    @log_level.setter
    def log_level(self, level):
        if level is None or not isinstance(level, int) or level < ttrk.log_trace or level > ttrk.log_none:
            raise ttrk.ValueError("invalid log_level({:})".format(level))

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

        if not self._should_log(ttrk.log_debug):
            return

        if value is None:
            value = str(self.__getattribute__(attr_name))

        if len(value) > 100:
            value = value[:100]

        self._log_write("Set {:}.{:} = {:}".format(type(self).__name__, attr_name, value))


    #-------------------------------------------------
    def _log_write_if(self, log_level, msg, prepend_self=False, print_to_console=False):
        if self._should_log(log_level):
            self._log_write(msg, prepend_self, print_to_console)


    #-------------------------------------------------
    def _log_write(self, msg, prepend_self=False, print_to_console=False):

        if prepend_self:
            msg = type(self).__name__ + "," + msg

        ttrk.log_write(msg)


    #-------------------------------------------------
    # Write to log when entering a function
    #
    def _log_func_enters(self, func_name, args=(), log_level=ttrk.log_trace):
        if self._should_log(log_level):
            args = ",".join([str(a) for a in args])
            self._log_write("enter_func,{:}({:})".format(func_name, args), prepend_self=True)


    #-------------------------------------------------
    # Write to log when function returns a value
    #
    def _log_func_returns(self, func_name, retval=None, self_name=None):
        if self._should_log(ttrk.log_trace):
            if self_name is None:
                self_name = type(self).__name__
            self._log_write("{:}.{:} returning {:}".format(self_name, func_name, retval))

