"""

Generate a circular trajectory

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
import numbers
import numpy as np

import trajtracker
import trajtracker._utils as _u


class CircularTrajectoryGenerator(trajtracker.TTrkObject):

    def __init__(self, center=None, radius=None, degrees_per_sec=None, full_rotation_duration=None,
                 degrees_at_t0=None, clockwise=True):
        """
        Constructor - invoked when you create a new object by writing CircularTrajectoryGenerator()

        :param center: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.center`
        :param radius: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.radius`
        :param degrees_per_sec: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_per_sec`
        :param degrees_at_t0: See :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_at_t0`
        """
        super(CircularTrajectoryGenerator, self).__init__()

        if full_rotation_duration is not None and degrees_per_sec is not None:
            raise trajtracker.ValueError("you cannot provide both full_rotation_duration and degrees_per_sec " +
                             "to the constructor of {:}".format(_u.get_type_name(self)))

        self._center = None
        self._radius = None
        self._degrees_per_sec = None

        if center is not None:
            self.center = center

        if radius is not None:
            self.radius = radius

        if degrees_per_sec is not None:
            self.degrees_per_sec = degrees_per_sec

        if full_rotation_duration is not None:
            self.full_rotation_duration = full_rotation_duration

        self.degrees_at_t0 = degrees_at_t0
        self.clockwise = clockwise


    #============================================================================
    #     Generate trajectory
    #============================================================================

    def get_traj_point(self, time):
        """
        Return the trajectory info at a certain time

        :param time: in seconds
        :returns: a dict with the coordinates ('x' and 'y' entries).
        """

        _u.validate_func_arg_type(self, "get_xy", "time", time, numbers.Number)
        if self._center is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting center".format(_u.get_type_name(self)))
        if self._degrees_per_sec is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting degrees_per_sec".format(_u.get_type_name(self)))
        if self._radius is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting radius".format(_u.get_type_name(self)))

        dps = self._degrees_per_sec * (1 if self._clockwise else -1)
        curr_degrees = (self._degrees_at_t0 + dps * time) % 360

        curr_degrees_rad = curr_degrees / 360 * np.pi * 2

        x = int(np.abs(np.round(self._radius * np.sin(curr_degrees_rad))))
        y = int(np.abs(np.round(self._radius * np.cos(curr_degrees_rad))))

        if curr_degrees > 180:
            x = -x
        if 90 < curr_degrees < 270:
            y = -y

        return {'x': x + self._center[0], 'y': y + self._center[1]}


    #============================================================================
    #     Configure
    #============================================================================

    #------------------------------------------------------------
    @property
    def center(self):
        """
        The center of the circle (x,y coordinates)
        """
        return self._center

    @center.setter
    def center(self, value):
        value = _u.validate_attr_is_coord(self, "center", value)
        self._center = value
        self._log_property_changed("center")

    #------------------------------------------------------------
    @property
    def radius(self):
        """
        The radius of the circle
        """
        return self._radius

    @radius.setter
    def radius(self, value):
        _u.validate_attr_type(self, "radius", value, numbers.Number)
        _u.validate_attr_positive(self, "radius", value)
        self._radius = value
        self._log_property_changed("radius")

    #------------------------------------------------------------
    @property
    def degrees_per_sec(self):
        """
        The radial speed of movement (you can also specify the speed as
        :attr:`~trajtracker.movement.CircularTrajectoryGenerator.full_rotation_duration`)
        """
        return self._degrees_per_sec

    @degrees_per_sec.setter
    def degrees_per_sec(self, value):
        _u.validate_attr_type(self, "degrees_per_sec", value, numbers.Number)
        _u.validate_attr_positive(self, "degrees_per_sec", value)
        self._degrees_per_sec = value % 360
        self._log_property_changed("degrees_per_sec")

    #------------------------------------------------------------
    @property
    def full_rotation_duration(self):
        """
        The radial speed of movement, in seconds (you can also specify the speed as
        :attr:`~trajtracker.movement.CircularTrajectoryGenerator.degrees_per_sec`)
        """
        return 360 / self._degrees_per_sec

    @full_rotation_duration.setter
    def full_rotation_duration(self, value):
        _u.validate_attr_type(self, "full_rotation_duration", value, numbers.Number)
        _u.validate_attr_positive(self, "full_rotation_duration", value)
        self._degrees_per_sec = (360 / value) % 360
        self._log_property_changed("full_rotation_duration")

    #------------------------------------------------------------
    @property
    def degrees_at_t0(self):
        """
        Position (specified as degrees) where the stimulus should be at time=0
        """
        return self._degrees_at_t0

    @degrees_at_t0.setter
    def degrees_at_t0(self, value):
        value = _u.validate_attr_numeric(self, "degrees_at_t0", value, none_value=_u.NoneValues.ChangeTo0)
        self._degrees_at_t0 = value % 360
        self._log_property_changed("degrees_at_t0")


    #------------------------------------------------------------
    @property
    def clockwise(self):
        """
        Whether the movement is clockwise or counter-clockwise
        """
        return self._clockwise

    @clockwise.setter
    def clockwise(self, value):
        _u.validate_attr_type(self, "clockwise", value, bool)
        self._clockwise = value
        self._log_property_changed("clockwise")

