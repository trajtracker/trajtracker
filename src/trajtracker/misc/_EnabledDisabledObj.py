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

from trajtracker import deprecated
from trajtracker.events import Event


class EnabledDisabledObj(object):
    """
    An object that can be enabled or disabled
    """

    #-------------------------------------------
    def __init__(self, enabled=False):
        self._registered = False
        self.enabled = enabled
        self.enable_events = ()
        self.disable_events = ()

    #-------------------------------------------
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
        self._log_property_changed("enabled")

    #-------------------------------------------
    @property
    @deprecated
    def enable_event(self):
        """
        The event on which the object should be enabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        **Note:** This property is deprecated, use *enable_events* instead

        :type: Event
        """
        return None if len(self._enable_events) == 0 else self._enable_events[0]

    @enable_event.setter
    @deprecated
    def enable_event(self, value):
        self.enable_events = () if value is None else (value,)

    #-------------------------------------------
    @property
    def enable_events(self):
        """
        The events on which the object should be enabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        :type: collection of Event objects
        """
        return self._enable_events

    @enable_events.setter
    def enable_events(self, value):
        value = _u.validate_attr_is_collection(self, "enable_events", value, none_allowed=True)
        for v in value:
            _u.validate_attr_type(self, "enable_events", v, Event)
        if self._registered:
            raise trajtracker.InvalidStateError("{:}.enable_events cannot be set after the object was registered to the event manager".format(
                _u.get_type_name(self)))
        self._enable_events = tuple(value)
        self._log_property_changed("enable_events")

    #-------------------------------------------
    @property
    def disable_event(self):
        """
        The event on which the object should be disabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        **Note:** This property is deprecated, use *disable_events* instead

        :type: Event
        """
        return None if len(self._disable_events) == 0 else self._disable_events[0]

    @disable_event.setter
    def disable_event(self, value):
        self.disable_events = () if value is None else (value,)

    #-------------------------------------------
    @property
    def disable_events(self):
        """
        The events on which the object should be disabled. This will work only when the object is registered
        to an :class:`~trajtracker.events.EventManager`

        :type: collection of Event objects
        """
        return self._disable_events

    @disable_events.setter
    def disable_events(self, value):
        value = _u.validate_attr_is_collection(self, "disable_events", value, none_allowed=True)
        for v in value:
            _u.validate_attr_type(self, "disable_events", v, Event)
        if self._registered:
            raise trajtracker.InvalidStateError("{:}.disable_events cannot be set after the object was registered to the event manager".format(
                _u.get_type_name(self)))
        self._disable_events = tuple(value)
        self._log_property_changed("disable_events")

    #-------------------------------------------
    # Register enable/disable operations on the event manager
    #
    def on_registered(self, event_manager):

        self._registered = True

        for event in self._enable_events:
            event_manager.register_operation(event, EnableDisableOp(self, True), recurring=True)

        for event in self._disable_events:
            event_manager.register_operation(event, EnableDisableOp(self, False), recurring=True)


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
