"""

 Validate the finger direction

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers

import expyriment
import numpy as np

import trajtracker
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.validators import _BaseValidator


# noinspection PyAttributeOutsideInit
class MovementAngleValidator(_BaseValidator):


    err_invalid_angle = "invalid_angle"
    arg_angle = 'angle'  # ValidationFailed exception argument: the angle actually observed


    def __init__(self, units_per_mm, min_angle=None, max_angle=None, calc_angle_interval=None,
                 grace_period=0, enabled=True):
        """
        Constructor

        :param units_per_mm: The ratio of units (provided in the call to :func:`~trajtracker.movement.MovementAngleValidator.check_xyt`) per mm.
                             This is relevant for computation of :func:`~trajtracker.movement.MovementAngleValidator.calc_angle_interval`
        :param min_angle: See :attr:`~trajtracker.movement.MovementAngleValidator.min_angle`
        :param max_angle: See :attr:`~trajtracker.movement.MovementAngleValidator.max_angle`
        :param calc_angle_interval: See :attr:`~trajtracker.movement.MovementAngleValidator.calc_angle_interval`
        :param grace_period: See :attr:`~trajtracker.movement.MovementAngleValidator.grace_period`
        :param enabled: See :attr:`~trajtracker.movement.MovementAngleValidator.enabled`
        """
        super(MovementAngleValidator, self).__init__(enabled=enabled)

        if not isinstance(units_per_mm, numbers.Number) or units_per_mm <= 0:
            raise ValueError("trajtracker error: invalid units_per_mm argument ({0}) to constructor of {1}".format(units_per_mm, self.__class__))

        self._units_per_mm = units_per_mm

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
        self._prev_locations = []


    #-----------------------------------------------------------------------------------
    def check_xyt(self, x_coord, y_coord, time):
        """
        Given a current position, check whether the movement complies with the speed limits.

        :param x_coord: Current x coordinate (in the predefined coordinate system)
        :param y_coord: Current y coordinate (in the predefined coordinate system)
        :param time: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :return: None if all OK, ValidationFailed if error
        """

        if not self._enabled or self._min_angle == self._max_angle or self._min_angle is None or self._max_angle is None:
            return None

        self._check_xyt_validate_and_log(x_coord, y_coord, time)
        self._validate_time(time)

        x_coord /= self._units_per_mm
        y_coord /= self._units_per_mm

        curr_xyt = (x_coord, y_coord, time)

        if time <= self._grace_period:
            self._prev_locations.append(curr_xyt)
            return None

        can_compute_angle = self._remove_far_enough_prev_locations(x_coord, y_coord)

        #-- Remember current coords & time
        self._prev_locations.append(curr_xyt)

        x0, y0, t0 = self._prev_locations[0]

        if can_compute_angle and (x0, y0) != (x_coord, y_coord):
            #-- Validate direction
            angle = u.get_angle((x0, y0), (x_coord, y_coord))
            if self._angle_is_ok(angle):
                #-- all is OK
                return None

            else:
                #-- Error
                angle_deg = angle / (np.pi * 2) * 360

                if self._log_level:
                    # noinspection PyProtectedMember
                    expyriment._active_exp._event_file_log("%s,InvalidAngle,%.1f" % (str(self.__class__), angle_deg), 1)

                return self._create_validation_error(self.err_invalid_angle, "You moved in an incorrect direction",
                                                     {self.arg_angle: angle_deg})

        else:
            #-- Direction cannot be validated - the finger hasn't moved enough yet
            pass

        return None


    #----------------
    def _validate_time(self, time):

        if len(self._prev_locations) > 0 and self._prev_locations[-1][2] > time:
            raise trajtracker.InvalidStateError("{0}.mouse_at() was called with time={1} after it was previously called with time={2}".format(self.__class__, time, self._prev_locations[-1][2]))


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

        self._log_setter("min_angle")

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

        self._log_setter("max_angle")

    #-----------------------------------------------------------------------------------
    @property
    def calc_angle_interval(self):
        """
        Time minimal distance (in mm) over which a direction vector can be calculated
        """
        return self._calc_angle_interval

    @calc_angle_interval.setter
    def calc_angle_interval(self, value):
        value = _u.validate_attr_numeric(self, "calc_angle_interval", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "calc_angle_interval", value)
        self._calc_angle_interval = value
        self._log_setter("calc_angle_interval")

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
        self._log_setter("grace_period")

