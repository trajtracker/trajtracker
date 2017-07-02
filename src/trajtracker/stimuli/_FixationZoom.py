"""

FixationZoom: a fixation stimulus of 4 dots moving inside 

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

from __future__ import division
import numpy as np

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u


class FixationZoom(ttrk.TTrkObject):

    #---------------------------------------------------------
    def __init__(self, position=(0, 0), box_size=(20, 20),
                 dot_radius=2, dot_colour=xpy.misc.constants.C_BLUE, dot_generator=None,
                 zoom_duration=0.2, stay_duration=0.1,
                 show_event=None, start_zoom_event=None):

        super(FixationZoom, self).__init__()

        self.position = position
        self.box_size = box_size
        self.dot_radius = dot_radius
        self.dot_colour = dot_colour
        self.dot_generator = self._default_generate_dot
        self.zoom_duration = zoom_duration
        self.stay_duration = stay_duration
        if dot_generator is not None:
            self.dot_generator = dot_generator

        self.show_event = show_event
        self.start_zoom_event = start_zoom_event

        self._stimulus = ttrk.stimuli.StimulusContainer(name="FixationZoom")

        self._need_to_regenerate_dots = True
        self._now_visible = False
        self._dots = []


    #---------------------------------------------------------
    @property
    def stimulus(self):
        """
        A :class:`~trajtracker.stimuli.StimulusContainer` containing all the fixation's dots
        """
        return self._stimulus


    #===================================================================
    # Runtime API: without events
    #===================================================================

    #---------------------------------------------------------
    # noinspection PyUnusedLocal
    def reset(self, time0=None):
        """
        Reset the fixation stimulus. Call this when the trial is initialized.
        """
        self._log_func_enters("reset", [time0])
        if self._need_to_regenerate_dots:
            self._generate_dots()
            self._need_to_regenerate_dots = False

        self.hide()
        self._set_dot_position_for_time(0)


    #---------------------------------------------------------
    def show(self):
        """
        Show the dots in the virtual rectangle's corners
        """
        self._log_func_enters("show")

        if self._need_to_regenerate_dots:
            raise ttrk.InvalidStateError('{:}.show() was called without calling reset() first'.format(_u.get_type_name(self)))

        self._set_dot_position_for_time(0)
        self._start_zoom_time = None
        self._now_visible = True

        for dot in self._dots:
            dot.visible = True


    #---------------------------------------------------------
    def hide(self):
        """
        Hide the dots; if zoom-in is still occurring, terminate it
        """
        self._log_func_enters("hide")

        self._start_zoom_time = None
        self._now_visible = False

        for dot in self._dots:
            dot.visible = False


    #---------------------------------------------------------
    @property
    def visible(self):
        """
        Set the fixation visible/invisible. This is equivalent to calling 
        :func:`~trajtracker.stimuli.FixationZoom.show` or :func:`~trajtracker.stimuli.FixationZoom.hide`
        
        :type: bool
        """
        return self._now_visible

    @visible.setter
    def visible(self, value):
        _u.validate_attr_type(self, "visible", value, bool)
        if value:
            self.show()
        else:
            self.hide()
        self._log_property_changed(self, "visible")


    #---------------------------------------------------------
    def start_zoom(self, time_in_session):
        """
        Start the zoom process
        """
        self._log_func_enters("start_zoom")

        if not self._now_visible:
            self.show()

        self._start_zoom_time = time_in_session
        self._set_dot_position_for_time(0)


    #---------------------------------------------------------
    def update(self, time):
        """
        Call this method periodically (preferably on each frame) to refresh the position of the dots.
        
        :func:`~trajtracker.stimuli.FixationZoom.start_zoom` must be called first.
        
        This method is equivalent to :func:`~trajtracker.stimuli.FixationZoom.update_xyt` 
        """
        self.update_xyt(time_in_session=time)


    #---------------------------------------------------------
    # noinspection PyUnusedLocal
    def update_xyt(self, position=None, time_in_trial=None, time_in_session=None):
        """
        Call this method periodically (preferably on each frame) to refresh the position of the dots.

        :func:`~trajtracker.stimuli.FixationZoom.start_zoom` must be called first.

        This method is equivalent to :func:`~trajtracker.stimuli.FixationZoom.update` . 
        You may find this one more convenient because it has the same API as the update_xyt() methods
        of other classes.
        """
        if self._should_log(ttrk.log_trace):
            self._log_func_enters("update_xyt")

        if not self._now_visible or self._start_zoom_time is None:
            #-- Either the zoom-in did not start yet, or it's already finished zooming in and the stimulus was hidden
            return

        if (self._stay_duration is not None) and time_in_session > (self._start_zoom_time + self._zoom_duration + self._stay_duration):
            self.hide()
        else:
            self._set_dot_position_for_time(time_in_session - self._start_zoom_time)


    #---------------------------------------------------------
    def _generate_dots(self):
        # noinspection PyUnusedLocal
        self._dots = []
        for dot_id in range(4):
            dot = self._dot_generator(self)
            self._stimulus.remove(dot_id)
            self._stimulus.add(dot, stimulus_id=dot_id, visible=False)
            self._dots.append(dot)


    #---------------------------------------------------------
    def _set_dot_position_for_time(self, time):

        if time < 0 or time > 10000:
            raise ttrk.ValueError('{:}._set_dot_position_for_time(): invalid "time" argument ({:})'.
                                  format(_u.get_type_name(self), time))

        remaining_time_ratio = 1 - (min(time, self._zoom_duration) / self._zoom_duration)

        dx = int(np.round(self._box_size[0] / 2 * remaining_time_ratio))
        dy = int(np.round(self._box_size[1] / 2 * remaining_time_ratio))

        self._dots[0].position = self.position[0] - dx, self.position[1] - dy  # top-left
        self._dots[1].position = self.position[0] + dx, self.position[1] - dy  # top-right
        self._dots[2].position = self.position[0] - dx, self.position[1] + dy  # bottom-left
        self._dots[3].position = self.position[0] + dx, self.position[1] + dy  # bottom-right

        if self._should_log(ttrk.log_trace):
            self._log_write("Set dots location, remaining time = {:.0f}%".format(remaining_time_ratio*100), True)


    #---------------------------------------------------------
    @staticmethod
    def _default_generate_dot(self):
        return xpy.stimuli.Circle(radius=self._dot_radius, colour=self._dot_colour)


    #===================================================================
    # Runtime API: with events
    #===================================================================


    #--------------------------------------------------------------
    def on_registered(self, event_manager):

        if self.start_zoom_event is None:
            raise ttrk.ValueError('{:}.start_zoom_event was not defined'.format(_u.get_type_name(self)))

        if self.show_event is not None:
            event_manager.register_operation(event=self.show_event,
                                             operation=lambda t1, t2: self.show(),
                                             recurring=True,
                                             description="FixationZoom: show")

        event_manager.register_operation(event=self.start_zoom_event,
                                         operation=lambda t_trial, t_session: self.start_zoom(t_session),
                                         recurring=True,
                                         description="FixationZoom: start zoom in")


    #===================================================================
    # Properties
    #===================================================================


    #---------------------------------------------------------
    @property
    def position(self):
        """
        Coordinates of the fixation center (x,y)
        """
        return self._position

    @position.setter
    def position(self, value):
        _u.validate_attr_type(self, "position", value, ttrk.TYPE_COORD)
        self._position = value
        self._log_property_changed(self, "position")


    #---------------------------------------------------------
    @property
    def box_size(self):
        """
        The size of the virtual box occupied by the four dots before zooming in (width, height).
        Dots will appear at the corners of this box.
        """
        return self._box_size

    @box_size.setter
    def box_size(self, value):
        _u.validate_attr_is_stim_size(self, "size", value)
        self._box_size = value
        self._log_property_changed(self, "box_size")


    #---------------------------------------------------------
    @property
    def dot_radius(self):
        """
        The size of each of the 4 dots (in pixels)

        Ignored if :attr:`~trajtracker.stimuli.FixationZoom.dot_generator` is overriden.
        
        :type: int
        """
        return self._dot_radius

    @dot_radius.setter
    def dot_radius(self, value):
        _u.validate_attr_type(self, "dot_radius", value, int)
        _u.validate_attr_positive(self, "dot_radius", value)
        self._dot_radius = value
        self._need_to_regenerate_dots = True
        self._log_property_changed(self, "dot_radius")


    #---------------------------------------------------------
    @property
    def dot_colour(self):
        """
        The colour of each of the 4 dots.
        
        Ignored if :attr:`~trajtracker.stimuli.FixationZoom.dot_generator` is overriden.
        
        :type: (red,green,blue) tuple
        """
        return self._dot_colour

    @dot_colour.setter
    def dot_colour(self, value):
        _u.validate_attr_type(self, "dot_colour", value, ttrk.TYPE_RGB)
        self._dot_colour = value
        self._need_to_regenerate_dots = True
        self._log_property_changed(self, "dot_colour")


    #---------------------------------------------------------
    @property
    def dot_generator(self):
        """
        A function that generates a stimulus to be used as one of the four dots.
        
        The function receives one argument (the FixationZoom object) and returns a stimulus.
          
        Default: generate circles.
        """
        return self._dot_generator

    @dot_generator.setter
    def dot_generator(self, value):
        _u.validate_attr_type(self, "dot_generator", value, ttrk.TYPE_CALLABLE)
        self._dot_generator = value
        self._need_to_regenerate_dots = True
        self._log_property_changed(self, "dot_generator")


    #---------------------------------------------------------
    @property
    def zoom_duration(self):
        """
        Duration (in seconds) it takes to "zoom in" the dots (move them to the center)
        """
        return self._zoom_duration

    @zoom_duration.setter
    def zoom_duration(self, value):
        _u.validate_attr_numeric(self, "zoom_duration", value)
        _u.validate_attr_positive(self, "zoom_duration", value)
        self._zoom_duration = value
        self._log_property_changed(self, "zoom_duration")


    #---------------------------------------------------------
    @property
    def stay_duration(self):
        """
        Duration (in seconds) the stimulus remains on screen, after zoom in is finished, before it disappears.
        
        If set to None, the stimulus will not disappear but remain on screen.
        """
        return self._stay_duration

    @stay_duration.setter
    def stay_duration(self, value):
        _u.validate_attr_numeric(self, "stay_duration", value, none_value=True)
        _u.validate_attr_not_negative(self, "stay_duration", value)
        self._stay_duration = value
        self._log_property_changed(self, "stay_duration")


    #---------------------------------------------------------
    @property
    def show_event(self):
        """
        When working with the the :doc:`events mechanism <../events/events_overview>`: the 
        event on which the fixation will be presented.
        
        If None, :attr:`~trajtracker.stimuli.FixationZoom.start_zoom_event` will also trigger
        the onset of the fixation.
         
        **Note**: This cannot be TRIAL_INITIALIZED or TRIAL_STARTED - it must be a later event.
        """
        return self._show_event

    @show_event.setter
    def show_event(self, value):
        _u.validate_attr_type(self, "show_event", value, ttrk.events.Event, none_allowed=True)
        self._show_event = value
        self._log_property_changed(self, "show_event")


    #---------------------------------------------------------
    @property
    def start_zoom_event(self):
        """
        When working with the the :doc:`events mechanism <../events/events_overview>`: the 
        event on which the fixation will start zooming.

        **Note**: This cannot be TRIAL_INITIALIZED or TRIAL_STARTED - it must be a later event.
        """
        return self._start_zoom_event

    @start_zoom_event.setter
    def start_zoom_event(self, value):
        _u.validate_attr_type(self, "start_zoom_event", value, ttrk.events.Event, none_allowed=True)
        self._start_zoom_event = value
        self._log_property_changed(self, "start_zoom_event")
