"""

 Validate the finger direction

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

import expyriment
import numpy as np

import trajtracker as ttrk
import trajtracker._utils as _u
import trajtracker.utils as u
import trajtracker.validators
from trajtracker.misc import EnabledDisabledObj


# noinspection PyAttributeOutsideInit
class MovementAngleValidator(ttrk.TTrkObject, EnabledDisabledObj):


    err_invalid_angle = "InvalidAngle"
    arg_angle = 'angle'  # ExperimentError argument: the angle actually observed


    def __init__(self, min_angle=None, max_angle=None, calc_angle_interval=None,
                 grace_period=0, enabled=True):
        """
        Constructor - invoked when you create a new object by writing MovementAngleValidator()

        :param min_angle: See :attr:`~trajtracker.movement.MovementAngleValidator.min_angle`
        :param max_angle: See :attr:`~trajtracker.movement.MovementAngleValidator.max_angle`
        :param calc_angle_interval: See :attr:`~trajtracker.movement.MovementAngleValidator.calc_angle_interval`
        :param grace_period: See :attr:`~trajtracker.movement.MovementAngleValidator.grace_period`
        :param enabled: See :attr:`~trajtracker.movement.MovementAngleValidator.enabled`
        """
        ttrk.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        self.min_angle = min_angle
        self.max_angle = max_angle
        self.calc_angle_interval = calc_angle_interval
        self.grace_period = grace_period

        self.reset()


    #========================================================================
    #      Validation API
    #========================================================================

    #-----------------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def reset(self, time0=None):
        """
        Called when a trial starts - reset any previous movement
        """

        self._log_func_enters("reset", [time0])

        self._prev_locations = []


    #-----------------------------------------------------------------------------------
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Given a current position, check whether the movement complies with the speed limits.

        :param position: Current (x,y) coordinates
        :param time_in_trial: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :param time_in_session: ignored
        :return: None if all OK, ExperimentError if error
        """

        if not self._enabled or self._min_angle == self._max_angle or self._min_angle is None or self._max_angle is None:
            return None

        _u.update_xyt_validate_and_log(self, position, time_in_trial)
        self._validate_time(time_in_trial)

        curr_xyt = position + (time_in_trial,)

        if time_in_trial <= self._grace_period:
            self._prev_locations.append(curr_xyt)
            return None

        can_compute_angle = self._remove_far_enough_prev_locations(position[0], position[1])

        #-- Remember current coords & time
        self._prev_locations.append(curr_xyt)

        x0, y0, t0 = self._prev_locations[0]

        if can_compute_angle and (x0, y0) != position:
            #-- Validate direction
            angle = u.get_angle((x0, y0), position)
            if self._angle_is_ok(angle):
                #-- all is OK
                return None

            else:
                #-- Error
                angle_deg = angle / (np.pi * 2) * 360

                self._log_write_if(ttrk.log_info, "InvalidAngle (%.1f degrees)" % angle_deg, prepend_self=True)

                return ttrk.validators.create_experiment_error(self, self.err_invalid_angle, "You moved in an incorrect direction",
                                                               {self.arg_angle: angle_deg})

        else:
            #-- Direction cannot be validated - the finger hasn't moved enough yet
            pass

        return None


    #----------------
    def _validate_time(self, time):

        if len(self._prev_locations) > 0 and self._prev_locations[-1][2] > time:
            raise ttrk.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(self.__class__, time, self._prev_locations[-1][2]))


    #-------------------------------------
    # Remove the first entries in self._prev_locations, as long as the first entry remains far enough
    # for angle computation (i.e., farther than self._calc_angle_interval)
    #
    # Returns True if, after this function call, self._prev_locations[0] is far enough for angle computation
    #
    def _remove_far_enough_prev_locations(self, x_coord, y_coord):

        if len(self._prev_locations) == 0:
            return False

        distance2 = self._calc_angle_interval ** 2
        too_close_ind = len(self._prev_locations)
        found_far_enough_entry = False
        for i in range(len(self._prev_locations)):
            x, y, t = self._prev_locations[i]
            if (x-x_coord)**2 + (y-y_coord)**2 < distance2:
                # This entry is already too close
                too_close_ind = i
                break
            else:
                found_far_enough_entry = True

        if too_close_ind > 1:
            self._prev_locations = self._prev_locations[too_close_ind-1:]

        return found_far_enough_entry


    #-------------------------------------
    def _angle_is_ok(self, angle):
        if self._min_angle < self._max_angle:
            return self._min_angle_rad <= angle <= self._max_angle_rad
        else:
            return not (self._max_angle_rad < angle < self._min_angle_rad)


    #========================================================================
    #      Config
    #========================================================================

    #-----------------------------------------------------------------------------------
    @property
    def min_angle(self):
        """
        The minimal valid angle (in degrees)
        This value can be either smaller or larger than :attr:`~trajtracker.validators.MovementAngleValidator.max_angle`
        """
        return self._min_angle


    @min_angle.setter
    def min_angle(self, value):

        if value is None:
            self._min_angle = None
            self._min_angle_rad = None
            return

        _u.validate_attr_numeric(self, "min_angle", value)

        self._min_angle = value % 360
        self._min_angle_rad = self._min_angle / 360 * np.pi * 2

        self._log_property_changed("min_angle")

    #-----------------------------------------------------------------------------------
    @property
    def max_angle(self):
        """
        The maximal valid angle (in degrees)
        This value can be either smaller or larger than :attr:`~trajtracker.validators.MovementAngleValidator.min_angle`
        """
        return self._max_angle


    @max_angle.setter
    def max_angle(self, value):

        if value is None:
            self._max_angle = None
            self._max_angle_rad = None
            return

        _u.validate_attr_numeric(self, "max_angle", value)

        self._max_angle = value % 360
        self._max_angle_rad = self._max_angle / 360 * np.pi * 2

        self._log_property_changed("max_angle")

    #-----------------------------------------------------------------------------------
    @property
    def calc_angle_interval(self):
        """
        Time minimal distance over which a direction vector can be calculated
        """
        return self._calc_angle_interval

    @calc_angle_interval.setter
    def calc_angle_interval(self, value):
        value = _u.validate_attr_numeric(self, "calc_angle_interval", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "calc_angle_interval", value)
        self._calc_angle_interval = value
        self._log_property_changed("calc_angle_interval")

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        value = _u.validate_attr_numeric(self, "grace_period", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "grace_period", value)
        self._grace_period = value
        self._log_property_changed("grace_period")

