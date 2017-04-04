"""

An event during an experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers, re

import trajtracker
import trajtracker._utils as _u


# noinspection PyProtectedMember
class Event(trajtracker._TTrkObject):
    # todo: change example to a text box and trial starts


    #----------------------------------------------------
    def __init__(self, event_id):
        super(Event, self).__init__()
        self._event_id = event_id
        self._offset = 0


    #----------------------------------------------------
    @property
    def event_id(self):
        """The ID of this event (string)"""
        return self._event_id


    #----------------------------------------------------
    @property
    def offset(self):
        """An offset (in seconds) relatively to the time the event occurred"""
        return self._offset


    #----------------------------------------------------
    def __add__(self, rhs):
        """Define a new event, in a time offset relatively to an existing event"""

        _u.validate_func_arg_type(self, "+", "right operand", rhs, numbers.Number)
        if rhs < 0:
            raise ValueError("trajtracker error: Invalid offset ({:}) for event {:}. Only events with positive offset are acceptable".format(
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
            raise ValueError("trajtracker error: invalid event format ({:}) - expecting a string value".format(text))

        if re.match('^\s*none\s*$', text.lower()):
            return None

        m = re.match('^\s*(\w+)\s*(\+\s*((\d+)|(\d*.\d+)))?\s*$', text)
        if m is None:
            raise ValueError("trajtracker error: invalid event format ({:}) - expecting event_id or event_id+offset".format(text))

        event = Event(m.group(1))
        if m.group(2) is not None:
            event += float(m.group(3))

        return event
