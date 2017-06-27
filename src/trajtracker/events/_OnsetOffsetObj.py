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
        self.onset = None
        self.offset = None

    #---------------------------------------------------
    @property
    def onset(self):
        """
        The time when the object should appear on screen. 
        
        :type: :class:`~trajtracker.events.Event`, or *None* to avoid automatic onset.
        """
        return self._onset

    @onset.setter
    def onset(self, value):
        _u.validate_attr_type(self, "onset", value, Event, none_allowed=True)
        self._onset = value

    #---------------------------------------------------
    @property
    def offset(self):
        """
        The time when the object should disappear from screen. 
        
        :type: :class:`~trajtracker.events.Event`, or *None* to avoid automatic offset.
        """
        return self._offset

    @offset.setter
    def offset(self, value):
        _u.validate_attr_type(self, "offset", value, Event, none_allowed=True)
        self._offset = value
