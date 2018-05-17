"""

Touch-sensitive area: detect touching certain screen areas

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

import numbers

import trajtracker as ttrk
import trajtracker._utils as _u


class Hotspot(ttrk.TTrkObject):

    #----------------------------------------------------
    def __init__(self, event_manager=None, area=None, min_touch_duration=0,
                 on_touched_dispatch_event=None, on_touched_callback=None, enabled=True, name=''):

        super(Hotspot, self).__init__()

        self.name = name
        self._event_manager = event_manager
        self.area = area
        self.min_touch_duration = min_touch_duration
        self.on_touched_dispatch_event = on_touched_dispatch_event
        self.on_touched_callback = on_touched_callback
        self._start_touch_time = None
        self._dispatched = False
        self._touched = False
        self.enabled = enabled


    #==============================================================================
    #        Runtime API
    #==============================================================================


    #----------------------------------------------------------------------------
    def reset(self, time=None):
        self._touched = False
        self._dispatched = False
        self._start_touch_time = None


    #----------------------------------------------------------------------------
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        
        :param position: 
        :param time_in_trial: 
        :param time_in_session: used only when working with an event manager (for dispatching an event)
        :return: 
        """

        if self._on_touched_dispatch_event is None:
            _u.update_xyt_validate_and_log(self, position, time_in_trial)
        else:
            _u.update_xyt_validate_and_log(self, position, time_in_trial, time_in_session)

        now_touching_me = self._area.overlapping_with_position(position)
        self._log_write_if(ttrk.log_trace, "Hotspot {:}: touch detected in position {:}, this {:} hotspot".
                           format(self._name, position, "overlaps" if now_touching_me else "does not overlap"))

        if not now_touching_me:
            # Stopped touching
            self._start_touch_time = None
            self._dispatched = False
            self._log_write_if(ttrk.log_trace, "Hotspot {:}: stopped touching".format(self._name))
            return

        if not self._enabled:
            self._log_write_if(ttrk.log_trace, "Hotspot {:} is disabled, ignored".format(self._name))
            return

        if self._start_touch_time is None:
            # Started touching
            self._start_touch_time = time_in_trial
            self._dispatched = False
            self._log_write_if(ttrk.log_trace, "Hotspot {:}: started touching".format(self._name))

        if not self._dispatched and time_in_trial - self._start_touch_time >= self._min_touch_duration:
            # Touching for long enough
            self._invoke_on_touched(time_in_trial, time_in_session)
            self._dispatched = True


    #----------------------------------------------------------------------------
    def _invoke_on_touched(self, time_in_trial, time_in_session):

        self._touched = True
        self._log_write_if(ttrk.log_debug, "Hotspot {:} touched".format(self._name))

        #-- Directly invoke a callback action
        if self._on_touched_callback is not None:
            self._log_write_if(ttrk.log_trace, "Hotspot {:}: invoking callback function".format(self._name))
            self._on_touched_callback(time_in_trial)

        #-- Dispatch an event
        if self._on_touched_dispatch_event is not None:
            if time_in_session is None:
                raise ttrk.ValueError("When {:} is dispatching an event, update_xyt() should get time_in_session".format(_u.get_type_name(self)))

            self._log_write_if(ttrk.log_trace, "Hotspot {:}: dispatching 'touch' event".format(self._name))
            self._event_manager.dispatch_event(ttrk.events.Event(self._on_touched_dispatch_event), time_in_trial, time_in_session)


    #----------------------------------------------------------------------------
    @property
    def touched(self):
        """
        Indicates whether the hotspot was touched during this trial (any time after reset() was called)
        :return: bool
        """
        return self._touched


    #==============================================================================
    #        Configuration
    #==============================================================================

    #----------------------------------------------------
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        _u.validate_attr_type(self, 'name', value, str)
        self._name = value


    #----------------------------------------------------
    @property
    def enabled(self):
        """Whether the hotspot is currently enabled (active) or not. Default = True."""
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        _u.validate_attr_type(self, 'enabled', value, bool)
        self._enabled = value


    #----------------------------------------------------
    @property
    def area(self):
        """
        The area that should be touched
        
        :type: Any shape - from expyriment, or from :doc:`trajtracker <../misc/shapes>`,
                           or any other class with an *overlapping_with_position()* method
        """
        return self._area

    @area.setter
    def area(self, value):
        if value is not None and "overlapping_with_position" not in dir(value):
            raise ttrk.TypeError("Invalid {:}.overlapping_with_position - expecting a shape".format(_u.get_type_name(self)))
        self._area = value


    #----------------------------------------------------
    @property
    def min_touch_duration(self):
        """
        The area will be considered as touched only when touched for at least this time
        :type: float (seconds) 
        """
        return self._min_touch_duration

    @min_touch_duration.setter
    def min_touch_duration(self, value):
        _u.validate_attr_type(self, "min_touch_duration", value, numbers.Number, none_allowed=True)
        _u.validate_attr_not_negative(self, "min_touch_duration", value)
        value = 0 if value is None else value

        self._min_touch_duration = value
        self._log_property_changed("min_touch_duration")


    #----------------------------------------------------
    @property
    def on_touched_dispatch_event(self):
        """
        An event to dispatch when the hotspot is touched.
         
        To use this, you must set event_manager in the constructor
        
        :type: str 
        """
        return self._on_touched_dispatch_event

    @on_touched_dispatch_event.setter
    def on_touched_dispatch_event(self, value):
        _u.validate_attr_type(self, "on_touched_dispatch_event", value, str, none_allowed=True)
        if value is not None and self._event_manager is None:
            raise ttrk.ValueError("{:}.on_touched_dispatch_event cannot be set without an event manager".format(_u.get_type_name(self)))

        self._on_touched_dispatch_event = value
        self._log_property_changed("on_touched_dispatch_event")

    #------------------------------------------------------
    @property
    def on_touched_callback(self):
        """
        A function to call when the hotspot is touched.
        
        The function should expect time_in_trial as a single argument. 
        """
        return

    @on_touched_callback.setter
    def on_touched_callback(self, value):
        _u.validate_attr_type(self, "on_touched_callback", value, ttrk.TYPE_CALLABLE, none_allowed=True)

        self._on_touched_callback = value
        self._log_property_changed("on_touched_callback")
