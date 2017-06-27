"""

Base class for objects that can be enabled/disabled

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


import trajtracker
import trajtracker._utils as _u

from trajtracker.events import Event


class EnabledDisabledObj(object):
    """
    An object that can be enabled or disabled
    """

    #-------------------------------------------
    def __init__(self, enabled=False):
        self._registered = False
        self.enabled = enabled
        self.enable_event = None
        self.disable_event = None

    # -------------------------------------------
    @property
    def enabled(self):
        """
        Whether the object is currently functioning or disabled

        :type: bool
        """
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        _u.validate_attr_type(self, "enabled", value, bool)
        self._enabled = value

    #-------------------------------------------
    @property
    def enable_event(self):
        """
        The event on which the object should be enabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        :type: Event
        """
        return self._enable_event

    @enable_event.setter
    def enable_event(self, value):
        _u.validate_attr_type(self, "enable_event", value, Event, none_allowed=True)
        if self._registered:
            raise trajtracker.InvalidStateError("{:}.enable_event cannot be set after the object was registered to the event manager".format(
                _u.get_type_name(self)))
        self._enable_event = value

    #-------------------------------------------
    @property
    def disable_event(self):
        """
        The event on which the object should be disabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        :type: Event
        """
        return self._disable_event

    @disable_event.setter
    def disable_event(self, value):
        _u.validate_attr_type(self, "disable_event", value, Event, none_allowed=True)
        if self._registered:
            raise trajtracker.InvalidStateError("{:}.disable_event cannot be set after the object was registered to the event manager".format(
                _u.get_type_name(self)))
        self._disable_event = value

    #-------------------------------------------
    # Register enable/disable operations on the event manager
    #
    def on_registered(self, event_manager):

        self._registered = True

        if self.enable_event is not None:
            event_manager.register_operation(self.enable_event, EnableDisableOp(self, True), recurring=True)

        if self.disable_event is not None:
            event_manager.register_operation(self.disable_event, EnableDisableOp(self, False), recurring=True)



#------------------------------------------------------------------------
#  An operation that can be registered to the event manager
#
class EnableDisableOp(object):

    def __init__(self, obj, enabled):
        self._obj = obj
        self._enabled = enabled

    def __call__(self, *args, **kwargs):
        self._obj.enabled = self._enabled

    def __str__(self):
        return "{:} {:}".format("enable" if self._enabled else "disable", _u.get_type_name(self._obj))
