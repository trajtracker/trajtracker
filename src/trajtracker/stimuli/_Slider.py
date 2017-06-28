"""
A slider with moving gauge 

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
from numbers import Number
import numpy as np

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.stimuli import Orientation


class Slider(ttrk.TTrkObject):

    #------------------------------------------------------------------
    def __init__(self, bgnd_stimulus, gauge_stimulus, orientation=Orientation.Horizontal,
                 min_value=0, max_value=100, default_value=None, max_moves=None, visible=False,
                 slidable_range=None, position=None):
        """
        Constructor
        
        :param bgnd_stimulus: See :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus` 
        :param gauge_stimulus: See :attr:`~trajtracker.stimuli.Slider.gauge_stimulus`
        :param orientation: See :attr:`~trajtracker.stimuli.Slider.orientation`
        :param min_value: See :attr:`~trajtracker.stimuli.Slider.min_value`
        :param max_value: See :attr:`~trajtracker.stimuli.Slider.max_value`
        :param default_value: See :attr:`~trajtracker.stimuli.Slider.default_value`
        :param max_moves: See :attr:`~trajtracker.stimuli.Slider.max_moves`
        :param visible: See :attr:`~trajtracker.stimuli.Slider.visible`
        :param slidable_range: See :attr:`~trajtracker.stimuli.Slider.slidable_range`
        :param position: See :attr:`~trajtracker.stimuli.Slider.position`
        """
        super(Slider, self).__init__()

        self.bgnd_stimulus = bgnd_stimulus
        self.gauge_stimulus = gauge_stimulus

        self._stimulus = ttrk.stimuli.StimulusContainer("slider")
        self._stimulus.add(bgnd_stimulus)
        self._stimulus.add(gauge_stimulus, visible=False)

        self.orientation = orientation

        self.min_value = min_value
        self.max_value = max_value
        self.default_value = default_value
        self.max_moves = max_moves

        self.slidable_range = slidable_range
        self.set_drag_area(None)
        self.set_clickable_area(None)

        if position is not None:
            self.position = position

        self._visible = False  # Must initialize this before reset()
        self.reset()
        self.visible = visible


    #------------------------------------------------------------------
    @property
    def stimulus(self):
        """
        The slider object (background + gauge)
        """
        return self._stimulus


    #=============================================================================================
    #   Runtime API (called during a trial)
    #=============================================================================================

    #------------------------------------------------------------------
    def reset(self):
        """
        Reset the slider (when a new trial starts). 
        
        The slider will be reset to its default value. If it was locked, it will be unlocked.
        """
        self._n_moves = 0
        self._now_dragging = False
        self.locked = False
        self.current_value = self._default_value


    #------------------------------------------------------------------
    def update(self, clicked, xy):
        """
        Update the slider according to mouse movement
        
        **Note**: Unlike other stimulus objects in TrajTracker, here you should call the update() function also
        when the mouse is unclicked.
        
        :param clicked: Whether the mouse is presently clicked or not 
        :param xy: The coordinate to which the gauge is being dragged (x, y). This parameter is ignored in some 
                   situations, e.g., when clicked=False, when slider is locked, etc.
        """
        _u.validate_func_arg_type(self, "update", "clicked", clicked, (bool, int))
        clicked = bool(clicked)
        _u.validate_func_arg_type(self, "update", "xy", xy, ttrk.TYPE_COORD)

        if self.locked:
            return

        clicked = clicked and self._is_valid_mouse_pos(xy)

        if clicked:

            if not self._now_dragging:
                #-- Started clicking
                self._n_moves += 1
                self._gauge_stimulus.visible = self.visible
                self._log_write_if(ttrk.log_trace, "Start moving slider")
                self._now_dragging = True

            coord = xy[self._orientation_ind]
            self._current_value = self._coord_to_value(coord)
            self._move_gauge_to_coord(coord)

        elif self._now_dragging:  # and not clicked
            #-- Finger/mouse was just lifted

            self._now_dragging = False

            if self._max_moves is not None and self._n_moves >= self._max_moves:
                # Lifted too many times: lock the slider
                self.locked = True


    #------------------------------------------------------------------
    def _is_valid_mouse_pos(self, mouse_position):
        """
        Check if the mouse is in a valid position. If not, this touch/click will be ignored.
        """
        if self._now_dragging:
            return self._drag_area is None or \
                   self._drag_area.overlapping_with_position(mouse_position)

        else:
            area = self._bgnd_stimulus if (self._clickable_area is None) else self._clickable_area
            return area.overlapping_with_position(mouse_position)


    #------------------------------------------------------------------
    @property
    def current_value(self):
        """
        The slider's current value, in numeric units.
        
        Setting this property will move the gauge accordingly. Also, the value will be trimmed to the valid range,
        setting to None will hide the gauge, and setting to non-None will show it.
        """
        return self._current_value

    @current_value.setter
    def current_value(self, value):
        _u.validate_func_arg_type(self, "set_current_value", "value", value, Number, none_allowed=True)

        if self._locked:
            raise ttrk.InvalidStateError("{:}.current_value cannot be changed - the slider is locked".
                                         format(_u.get_type_name(self)))

        self._current_value = None if value is None else self._crop_value(value)

        self.gauge_stimulus.visible = self.visible and (value is not None)
        if value is not None:
            self._move_gauge_to_coord(self._value_to_coord(self._current_value))


    #------------------------------------------------------------------
    def _move_gauge_to_coord(self, coord):
        """
        Set the slider's value and move the gauge to the relevant location
        
        :param value: The slider's coordinate
        """

        if coord is None:
            self._current_value = None
            self.gauge_stimulus.visible = False
            return

        mincoord, maxcoord = self._get_gauge_min_max_coords()
        coord = max(min(coord, maxcoord), mincoord)

        if self._orientation == Orientation.Horizontal:
            self.gauge_stimulus.position = coord, self.gauge_stimulus.position[1]
        else:  # vertical
            self.gauge_stimulus.position = self.gauge_stimulus.position[0], coord


    #------------------------------------------------------------------
    @property
    def n_moves(self):
        """
        Get the number of times the gauge was moved since the last call to 
        :func:`~trajtracker.stimuli.Slider.reset`
        """
        return self._n_moves


    #=============================================================================================
    #   Handle the slider's coordinate system - convert between screen coordinates and
    #   slider value
    #=============================================================================================

    #------------------------------------------------------------------
    # Crop the value to be within the valid range (between min and max)
    def _crop_value(self, value):
        minimal = min(self._min_value, self._max_value)
        maximal = max(self._min_value, self._max_value)
        return max(minimal, min(value, maximal))


    #------------------------------------------------------------------
    def _value_to_coord(self, value):
        mincoord, maxcoord = self._get_gauge_min_max_coords()
        length_pixels = maxcoord - mincoord
        slider_ratio = (self._crop_value(value) - self._min_value) / (self._max_value - self._min_value)
        return mincoord + slider_ratio * length_pixels


    #------------------------------------------------------------------
    def _coord_to_value(self, coord):
        mincoord, maxcoord = self._get_gauge_min_max_coords()
        length_pixels = maxcoord - mincoord
        slider_ratio = (coord - mincoord) / length_pixels
        return self._crop_value(self._min_value + slider_ratio * (self._max_value - self._min_value))


    #------------------------------------------------------------------
    def _get_gauge_min_max_coords(self):
        i = self._orientation_ind
        pos = self.bgnd_stimulus.position[i]

        if self._slidable_range is None:
            size = int(self._bgnd_stimulus.surface_size[i] / 2)
            slidable_range = -size, size
        else:
            slidable_range = self._slidable_range

        return pos + slidable_range[0], pos + slidable_range[1]


    #=============================================================================================
    #   Logical & behavior properties
    #=============================================================================================

    # ------------------------------------------------------------------
    @property
    def visible(self):
        """
        Whether the slider is now visible or not.

        Note that even if the slider is visible, the gauge may sometimes be hidden.
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        _u.validate_attr_type(self, "visible", visible, bool)
        self._visible = visible
        self._gauge_stimulus.visible = visible and (self._current_value is not None)
        self._stimulus.visible = visible
        self._log_property_changed("visible")

    # ------------------------------------------------------------------
    @property
    def locked(self):
        """
        Whether the gauge can now move feely (locked = False) or not (locked = True)
        """
        return self._locked

    @locked.setter
    def locked(self, value):
        _u.validate_attr_type(self, "locked", value, bool)
        self._locked = value
        self._log_write_if(ttrk.log_trace, "Slider was {:}".format("locked" if self._locked else "unlocked"))

    #-----------------------------------------------------------
    @property
    def orientation(self):
        """ 
        The slider's orientation (horizontal or vertical).
        
        Changing the orientation will **not** cause :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`
        or :attr:`~trajtracker.stimuli.Slider.gauge_stimulus` to be rotated; it only affects the
        direction where the gauge can be moved.

        :type: trajtracker.stimuli.Orientation
        """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        if not isinstance(value, ttrk.stimuli.Orientation):
            raise ttrk.TypeError(
                "invalid value for {:}.orientation ({:}) - expecting Orientation.Horizontal or Orientation.Vertical".format(
                    _u.get_type_name(self), value))

        self._orientation = value
        self._log_property_changed("orientation")

    #------------------------------------------------------------------
    # Return 0 or 1: the index within size or position that corresponds with the orientation's axis
    #
    @property
    def _orientation_ind(self):
        return 0 if self._orientation == Orientation.Horizontal else 1


    #------------------------------------------------------------------
    @property
    def min_value(self):
        """
        The value at the slider's left/bottom end 
         
        If min_value > max_value, the slider is reversed (i.e., the smaller value is at the right or top)
         
        :type: Number 
        """
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        _u.validate_attr_type(self, "min_value", value, Number)
        self._min_value = value
        self._log_property_changed("min_value")


    #------------------------------------------------------------------
    @property
    def max_value(self):
        """
        The value at the slider's right/top end
        
        If min_value > max_value, the slider is reversed (i.e., the smaller value is at the right or top)
        
        :type: Number 
        """
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        _u.validate_attr_type(self, "max_value", value, Number)
        self._max_value = value
        self._log_property_changed("max_value")


    #------------------------------------------------------------------
    @property
    def default_value(self):
        """
        The slider's default value. This determines the initial position of the gauge after 
        :func:`~trajtracker.stimuli.Slider.reset` is called.
        
        If set to None, the gauge will only appear once the slider is touched. 
        
        Values exceeding :attr:`~trajtracker.stimuli.Slider.min_value` or :attr:`~trajtracker.stimuli.Slider.max_value`
        are cropped.
        
        :type: Number
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        _u.validate_attr_type(self, "default_value", value, Number, none_allowed=True)
        self._default_value = value
        self._log_property_changed("default_value")

    #------------------------------------------------------------------
    @property
    def max_moves(self):
        """
        The maximal number of times the gauge can move after :func:`~trajtracker.stimuli.Slider.reset`
        was called.
        
        If this number is exceeded, the slider is :attr:`~trajtracker.stimuli.Slider.locked`
         
        Value = *None* means no restriction.
        
        :type: int 
        """
        return self._max_moves

    @max_moves.setter
    def max_moves(self, value):
        _u.validate_attr_type(self, "max_moves", value, int, none_allowed=True)
        self._max_moves = value


    #=============================================================================================
    # Visual properties
    #=============================================================================================

    #------------------------------------------------------------------
    @property
    def position(self):
        """
        The slider's position, which is the position of :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`
        
        :type: tuple (x, y) 
        """
        return self._bgnd_stimulus.position

    @position.setter
    def position(self, value):
        self._bgnd_stimulus.position = value


    #------------------------------------------------------------------
    @property
    def size(self):
        """
        Get the slider's size, which is the size of :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`
        
        :type: tuple (width, height) 
        """
        return self._bgnd_stimulus.surface_size


    #------------------------------------------------------------------
    @property
    def bgnd_stimulus(self):
        """
        The stimulus serving as the background for this slider.
        """
        return self._bgnd_stimulus

    @bgnd_stimulus.setter
    def bgnd_stimulus(self, value):
        if value is None or "present" not in dir(value):
            raise ttrk.TypeError("Invalid {:}.bgnd_stimulus: expecting a stimulus".format(_u.get_type_name(self)))
        self._bgnd_stimulus = value


    #------------------------------------------------------------------
    @property
    def gauge_stimulus(self):
        """
        The stimulus serving as the gauge that actually slides.
        """
        return self._gauge_stimulus

    @gauge_stimulus.setter
    def gauge_stimulus(self, value):
        if value is None or "present" not in dir(value):
            raise ttrk.TypeError("Invalid {:}.gauge_stimulus: expecting a stimulus".format(_u.get_type_name(self)))
        self._gauge_stimulus = value


    #------------------------------------------------------------------
    @property
    def slidable_range(self):
        """
        The range on which the gauge can slide (in the relevant direction according to
        :attr:`~trajtracker.stimuli.Slider.orientation`). 
        Specified in pixels, relatively to the stimulus position.
        
        *None* means that the range is determined by the size of :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`
         
        :type: tuple with two integers (min, max)
        """
        return self._slidable_range

    @slidable_range.setter
    def slidable_range(self, value):
        _u.validate_attr_is_collection(self, "slide_coord_range", value, min_length=2, max_length=2, none_allowed=True)

        if value is None:

            self._slidable_range = None

        else:
            for i in range(2):
                _u.validate_attr_type(self, "slide_coord_range[%d]" % i, value[i], Number)

            #-- Make sure that first value is the smaller one
            if value[0] > value[1]:
                value = value[1], value[0]

            self._slidable_range = tuple(value)

        self._log_property_changed("slide_coord_range")


    #------------------------------------------------------------------
    @property
    def clickable_area(self):
        """
        The area that can be clicked in order to start moving the gauge.
        """
        return self._clickable_area


    def set_clickable_area(self, area, relative_position=False):
        """
        Set :attr:`~trajtracker.stimuli.Slider.clickable_area` : 
        the area that can be clicked in order to start moving the gauge.
        
        :param area: A stimulus. None = use default area (= :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`) 
        :param relative_position: The area's position, relative to :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`.
                             If this parameter is None, area.position will be used as absolute screen coordinates.
        """
        if area is not None and "size" not in dir(area):
            raise ttrk.TypeError("Invalid 'area' argument to {:}.set_clickable_area(): expecting a shape".
                                 format(_u.get_type_name(self)))


        if relative_position and area is not None:
            p = self._clickable_area.position
            p1 = self._bgnd_stimulus.position
            self._clickable_area.position = p[0] + p1[0], p[1] + p1[1]

        self._clickable_area = area


    #------------------------------------------------------------------
    @property
    def drag_area(self):
        """
        The area in which the mouse can move to continue moving the gauge.
         
        If the mouse exits this area, it's considered as if it was unclicked (i.e. the gauge will stop at 
        its present position).
        """
        return self._drag_area


    def set_drag_area(self, area, relative_position=False):
        """
        Set :attr:`~trajtracker.stimuli.Slider.drag_area` : 
        the area in which the mouse can move to continue moving the gauge.

        :param area: A stimulus. None = remove this restriction, finger/mouse can move anywhere to continue dragging the gauge. 
        :param relative_position: The area's position, relative to :attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`.
                             If this parameter is None, area.position will be used as absolute screen coordinates.
        """

        if area is not None and "size" not in dir(area):
            raise ttrk.TypeError("Invalid 'area' argument to {:}.set_drag_area(): expecting a shape".
                                 format(_u.get_type_name(self)))

        if relative_position and area is not None:
            p = self._drag_area.position
            p1 = self._bgnd_stimulus.position
            self._drag_area.position = p[0] + p1[0], p[1] + p1[1]

        self._drag_area = area
