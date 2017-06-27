"""

An event during an experiment

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

import numbers, re

import trajtracker
import trajtracker._utils as _u


# noinspection PyProtectedMember
class Event(trajtracker.TTrkObject):

    #----------------------------------------------------
    def __init__(self, event_id, extends=None):
        """
        Constructor - invoked when you create a new object by writing Event()

        :param event_id: A string that uniquely identifies the event
        :type event_id: str
        :param extends: If this event extends another one (see details in :ref:`event-hierarchy`)
        :type extends: Event
        """
        super(Event, self).__init__()

        _u.validate_func_arg_type(self, "__init__", "event_id", event_id, str)
        _u.validate_func_arg_type(self, "__init__", "extends", extends, Event, True)

        self._event_id = event_id
        self._offset = 0

        self._extended = False
        self._extends = extends
        if extends is not None:
            extends._extended = True


    #----------------------------------------------------
    @property
    def event_id(self):
        """
        The ID of this event (string)
        """
        return self._event_id


    #----------------------------------------------------
    @property
    def offset(self):
        """
        An offset (in seconds) relatively to the time the event occurred
        """
        return self._offset


    #----------------------------------------------------
    @property
    def extends(self):
        """The event that the present event extends (or None)"""
        return self._extends


    #----------------------------------------------------
    @property
    def event_hierarchy(self):
        """The present event, and all the events it extends"""

        result = []
        e = self
        while e is not None:
            result.append(e)
            e = e._extends

        return result


    #----------------------------------------------------
    def __add__(self, rhs):
        """Define a new event, in a time offset relatively to an existing event"""

        _u.validate_func_arg_type(self, "+", "right operand", rhs, numbers.Number)
        if rhs < 0:
            raise trajtracker.ValueError("Invalid offset ({:}) for event {:}. Only events with positive offset are acceptable".format(
                rhs, self._event_id))

        new_event = Event(self._event_id)
        new_event._offset = self._offset + rhs
        return new_event


    #----------------------------------------------------
    @staticmethod
    def parse(text):
        """
        Parse a string into an event object. "None" is acceptable.
        """
        if not isinstance(text, str):
            raise trajtracker.ValueError("invalid event format ({:}) - expecting a string value".format(text))

        if re.match('^\s*none\s*$', text.lower()):
            return None

        m = re.match('^\s*(\w+)\s*(\+\s*((\d+)|(\d*.\d+)))?\s*$', text)
        if m is None:
            raise trajtracker.ValueError("invalid event format ({:}) - expecting event_id or event_id+offset".format(text))

        event = Event(m.group(1))
        if m.group(2) is not None:
            event += float(m.group(3))

        return event

    #----------------------------------------------------
    def __str__(self):
        if self._offset == 0:
            return self._event_id
        else:
            return "{:} + {:.3g}sec".format(self._event_id, self._offset)

    #----------------------------------------------------
    def __eq__(self, other):
        return isinstance(other, Event) and self._event_id == other._event_id and self._offset == other._offset


