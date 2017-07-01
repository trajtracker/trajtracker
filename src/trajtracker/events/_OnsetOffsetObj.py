"""

Objects that can define onset and offset relatively to an event

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

from trajtracker.events import Event
import trajtracker._utils as _u


class OnsetOffsetObj(object):

    def __init__(self):
        self.onset_event = None
        self.offset_event = None

    #---------------------------------------------------
    @property
    def onset_event(self):
        """
        The time when the object should appear on screen. 
        
        :type: :class:`~trajtracker.events.Event`, or *None* to avoid automatic onset.
        """
        return self._onset_event

    @onset_event.setter
    def onset_event(self, value):
        _u.validate_attr_type(self, "onset", value, Event, none_allowed=True)
        self._onset_event = value

    #---------------------------------------------------
    @property
    def offset_event(self):
        """
        The time when the object should disappear from screen. 
        
        :type: :class:`~trajtracker.events.Event`, or *None* to avoid automatic offset.
        """
        return self._offset_event

    @offset_event.setter
    def offset_event(self, value):
        _u.validate_attr_type(self, "offset", value, Event, none_allowed=True)
        self._offset_event = value
