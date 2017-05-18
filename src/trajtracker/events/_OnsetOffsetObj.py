"""

Objects that can define onset and offset relatively to an event

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
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
