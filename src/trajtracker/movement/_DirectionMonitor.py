"""

Movement monitor: continuously track the movement direction

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
from enum import Enum

import trajtracker as ttrk
import trajtracker._utils as _u
import trajtracker.utils as u


class DirectionMonitor(ttrk.TTrkObject):

    Units = Enum("Units", "Degrees Radians")


    #-------------------------------------------------------------------------
    def __init__(self, min_distance=0, angle_units=Units.Degrees, zero_angle=0, min_angle_change_per_curve=0):
        """
        Constructor - invoked when you create a new object by writing DirectionMonitor()

        :param min_distance: See :attr:`~trajtracker.movement.DirectionMonitor.min_distance`
        :param angle_units: See :attr:`~trajtracker.movement.DirectionMonitor.angle_units`
        :param min_angle_change_per_curve: See :attr:`~trajtracker.movement.DirectionMonitor.min_angle_change_per_curve`
        """
        super(DirectionMonitor, self).__init__()

        self.min_distance = min_distance
        self.angle_units = angle_units
        self.zero_angle = zero_angle
        self.min_angle_change_per_curve = min_angle_change_per_curve

        self.reset()



    #====================================================================================
    #   Runtime API - update movement
    #====================================================================================


    #-------------------------------------------------------------------------
    def reset(self):
        """
        Called when a trial starts - reset any previous movement
        """

        self._log_func_enters("reset")

        self._recent_near_coords = []
        self._pre_recent_coord = None

        self._curr_angle = None

        #-- "current curve" is a curve that is validated
        self._curr_curve_direction = None
        self._curr_curve_start_angle = None
        self._curr_curve_start_index = None

        #-- "new curve" is when we observe a very small change in angle, but we're not yet sure
        #-- it should count as a curve.
        self._possible_curve_direction = None
        self._possible_curve_start_angle = None
        self._possible_curve_start_index = None

        self._n_curves = 0


    #-------------------------------------------------------------------------
    # noinspection PyIncorrectDocstring
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Call this method whenever the finger/mouse moves
        
        :param time_in_session: ignored
        """

        _u.update_xyt_validate_and_log(self, position, time_in_trial)

        self._remove_far_enough_recent_coords(position[0], position[1])

        # remember coordinates
        self._recent_near_coords.append(position + (time_in_trial,))

        last_angle = self._curr_angle
        self._calc_curr_angle()
        self._check_if_new_curve(last_angle)


    #-------------------------------------
    # Calculate the recent movement direction
    #
    def _calc_curr_angle(self):

        if self._pre_recent_coord is None:
            self._curr_angle = None
            return

        angle = u.get_angle(self._pre_recent_coord, self._recent_near_coords[-1])

        if self._angle_units == self.Units.Degrees:
            angle = angle / (np.pi * 2) * 360

        if self._zero_angle != 0:
            angle -= self._zero_angle

        max_angle = self._max_angle()
        angle = angle % max_angle
        if angle > max_angle / 2:
            angle -= max_angle

        self._curr_angle = angle


    #-------------------------------------
    def _max_angle(self):
        return 360 if self._angle_units == self.Units.Degrees else np.pi * 2


    #-------------------------------------
    def _check_if_new_curve(self, prev_angle):

        if self._curr_angle is None or prev_angle is None:
            return

        max_angle = self._max_angle()
        change_in_angle = (self._curr_angle - prev_angle) % max_angle
        if change_in_angle == 0:
            return

        curr_curve_direction = 1 if change_in_angle <= max_angle / 2 else -1

        #-- Compare the angular acceleration's direction between existing curve and new data
        if curr_curve_direction == self._curr_curve_direction:

            #-- Angular acceleration remained in the same direction: we're still in the same curve as before
            self._clear_possible_curve()

        else:
            #-- Angular acceleration changed its direction: this may be a new curve

            if self._possible_curve_direction is None:
                #-- Mark the beginning of a possible curve
                self._possible_curve_direction = curr_curve_direction
                self._possible_curve_start_angle = self._curr_angle
                self._possible_curve_start_index = len(self._recent_near_coords) - 1
                self._last_pre_curve_angle = prev_angle

            #-- Check if the finger/mouse changed its direction enough
            change_in_angle_along_curve = (self._curr_angle - self._last_pre_curve_angle) % max_angle
            change_in_angle_along_curve = min(change_in_angle_along_curve, max_angle-change_in_angle_along_curve)

            if change_in_angle_along_curve >= self._min_angle_change_per_curve:
                #-- The change in angle is large enough: this counts as a new curve

                self._n_curves += 1

                self._curr_curve_direction = curr_curve_direction
                self._curr_curve_start_angle = self._curr_angle
                self._curr_curve_start_index = len(self._recent_near_coords) - 1

                if self._should_log(ttrk.log_debug):
                    self._log_write(
                        "A new curve (a change of {:} degrees was detected, direction={:}, starting at time = {:} s)".format(
                            change_in_angle_along_curve, curr_curve_direction, self._recent_near_coords[-1][2]), True)

                self._clear_possible_curve()


    #-------------------------------------------------
    def _clear_possible_curve(self):
        self._possible_curve_direction = None
        self._possible_curve_start_angle = None
        self._possible_curve_start_index = None
        self._last_pre_curve_angle = None

    #-------------------------------------
    # Remove the first entries in self._prev_locations, as long as the first entry remains far enough
    # for angle computation (i.e., farther than self._calc_angle_interval)
    #
    # Returns True if, after this function call, self._prev_locations[0] is far enough for angle computation
    #
    def _remove_far_enough_recent_coords(self, x_coord, y_coord):

        if len(self._recent_near_coords) == 0:
            return

        sq_min_distance = self._min_distance ** 2

        self._pre_recent_coord = None

        #-- Find the latest coordinate that is far enough
        for i in range(len(self._recent_near_coords)-1, -1, -1):
            x, y, t = self._recent_near_coords[i]
            if (x - x_coord) ** 2 + (y - y_coord) ** 2 >= sq_min_distance:
                #-- This coordinate is far enough
                self._pre_recent_coord = (x, y)
                break


    #====================================================================================
    #   Runtime API - get info
    #====================================================================================

    #-------------------------------------
    @property
    def curr_angle(self):
        """ The angle where the finger/mouse is now going at """
        return self._curr_angle

    #-------------------------------------
    @property
    def curr_curve_direction(self):
        """
        The direction of the current curve (i.e., to which direction the mouse/finger currently turns)
        1 = clockwise, -1 = counter clockwise
        """
        return self._curr_curve_direction

    # -------------------------------------
    @property
    def curr_curve_start_angle(self):
        """
        The finger/mouse angle at the beginning of the current curve
        """
        return self._curr_curve_start_angle

    # -------------------------------------
    @property
    def curr_curve_start_xyt(self):
        """
        The coordinates and time at the beginning of the current curve
        """
        if self._curr_curve_start_index is None:
            return None
        else:
            return self._recent_near_coords[self._curr_curve_start_index]

    #-------------------------------------
    @property
    def n_curves(self):
        """
        The number of curves since the last call to reset()
        """
        return self._n_curves


    #====================================================================================
    #   Configure
    #====================================================================================

    #-------------------------------------
    @property
    def min_distance(self):
        """ The minimal distance between points required for calculating direction """
        return self._min_distance

    @min_distance.setter
    def min_distance(self, value):
        _u.validate_attr_numeric(self, "min_distance", value)
        _u.validate_attr_not_negative(self, "min_distance", value)
        self._min_distance = value
        self._log_property_changed("min_distance")
        if value < 20 and self._should_log(ttrk.log_warn):
            self._log_write("WARNING: min_distance was set to a small value ({:}), this may result in incorrect directions", True)


    #-------------------------------------
    @property
    def angle_units(self):
        """
        Units for specifying angles (Units.Degrees or Units.Radians)
        """
        return self._angle_units

    @angle_units.setter
    def angle_units(self, value):
        _u.validate_attr_type(self, "angle_units", value, self.Units)
        self._angle_units = value
        self._log_property_changed("angle_units")

    #-------------------------------------
    @property
    def zero_angle(self):
        """
        The angle that counts as zero (0=up).
        This means that:
        - the value returned from :attr:`~trajtracker.movement.DirectionMonitor.curr_angle` will be rotated by this value
        - The counting of left/right curves will be relatively to this zero angle
        """
        return self._zero_angle

    @zero_angle.setter
    def zero_angle(self, value):
        _u.validate_attr_numeric(self, "zero_angle", value)
        self._zero_angle = value
        self._log_property_changed("zero_angle")


    #-------------------------------------
    @property
    def min_angle_change_per_curve(self):
        """
        A curve must change the finger/mouse direction by at least this amount.
        Smaller changes do not count as curves.
        """
        return self._min_angle_change_per_curve

    @min_angle_change_per_curve.setter
    def min_angle_change_per_curve(self, value):
        _u.validate_attr_numeric(self, "min_angle_change_per_curve", value)
        _u.validate_attr_not_negative(self, "min_angle_change_per_curve", value)
        self._min_angle_change_per_curve = value
        self._log_property_changed("min_angle_change_per_curve")
