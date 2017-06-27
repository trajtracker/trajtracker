"""
  Validator for minimal/maximal instantaneous speed

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

import trajtracker._utils as _u
import trajtracker.validators
from trajtracker.movement import SpeedMonitor
from trajtracker.misc import EnabledDisabledObj
from trajtracker.validators import ValidationAxis, ExperimentError


# noinspection PyAttributeOutsideInit
class InstantaneousSpeedValidator(trajtracker.TTrkObject, EnabledDisabledObj):

    err_too_slow = "TooSlowInstantaneous"
    err_too_fast = "TooFast"
    err_stopped = "FingerStopped"
    arg_speed = 'speed'  # ExperimentError argument: the speed observed
    arg_stopped_duration = "stopped_duration"

    #-----------------------------------------------------------------------------------
    def __init__(self, axis=ValidationAxis.y, enabled=True, min_speed=None, max_speed=None,
                 max_stop_duration=None, grace_period=0, calculation_interval=0, movement_monitor=None):
        """
        Constructor - invoked when you create a new object by writing InstantaneousSpeedValidator()

        :param axis: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.axis`
        :param enabled: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.enabled`
        :param min_speed: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.min_speed`
        :param max_speed: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.max_speed`
        :param max_stop_duration: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.max_stop_duration`
        :param grace_period: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.grace_period`
        :param calculation_interval: See :attr:`~trajtracker.validators.InstantaneousSpeedValidator.calculation_interval`
        """

        trajtracker.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        if movement_monitor is None:
            self._speed_monitor = SpeedMonitor(calculation_interval)
        elif isinstance(movement_monitor, SpeedMonitor):
            self._speed_monitor = movement_monitor
        else:
            raise trajtracker.ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "__init__", "movement_monitor", "InstMovementMonitor", movement_monitor))

        self.axis = axis
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.grace_period = grace_period
        self.calculation_interval = calculation_interval
        self.max_stop_duration = max_stop_duration

        self.reset()


    #========================================================================
    #      Validation API
    #========================================================================


    #-----------------------------------------------------------------------------------
    def reset(self, time0=None):
        """
        Called when a trial starts - reset any previous movement

        :param time0: The time when the trial starts. The grace period will be determined according to this time.
        """

        self._log_func_enters("reset", [time0])

        self._speed_monitor.reset(time0)


    #-----------------------------------------------------------------------------------
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Given a current position, check whether the movement complies with the speed limits.

        :param position: Current (x,y) coordinates
        :param time_in_trial: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :param time_in_session: ignored
        :return: None if all OK, ExperimentError if error
        """

        if not self._enabled:
            return None

        _u.update_xyt_validate_and_log(self, position, time_in_trial)

        self._speed_monitor.update_xyt(position, time_in_trial)


        #-- Calculate speed, if possible
        if self._speed_monitor.time_in_trial is not None and \
            self._speed_monitor.time_in_trial > self._grace_period and \
                self._speed_monitor.last_calculation_interval is not None:

            if self._axis == ValidationAxis.x:
                speed = self._speed_monitor.xspeed

            elif self._axis == ValidationAxis.y:
                speed = self._speed_monitor.yspeed

            elif self._axis == ValidationAxis.xy:
                speed = self._speed_monitor.xyspeed

            else:
                return None

            if self._min_speed is not None and speed < self._min_speed:
                return trajtracker.validators.create_experiment_error(self, self.err_too_slow, "You moved too slowly, or completely stopped moving", {self.arg_speed: speed})

            if self._max_speed is not None and speed > self._max_speed:
                return trajtracker.validators.create_experiment_error(self, self.err_too_fast, "You moved too fast", {self.arg_speed: speed})

            t_stopped = self._speed_monitor.stopped_duration
            if self._max_stop_duration is not None and t_stopped is not None and t_stopped > self._max_stop_duration:
                return trajtracker.validators.create_experiment_error(self, self.err_stopped, "You stopped moving",
                                                                      {self.arg_stopped_duration: t_stopped})

        return None


    #========================================================================
    #      Config
    #========================================================================

    #-----------------------------------------------------------------------------------
    @property
    def axis(self):
        """
        The ValidationAxis on which speed is validated
        ValidationAxis.x or ValidationAxis.y: limit the speed in the relevant axis.
        ValidationAxis.xy: limit the diagonal speed
        """
        return self._axis

    @axis.setter
    def axis(self, value):
        _u.validate_attr_type(self, "axis", value, ValidationAxis)
        self._axis = value
        self._log_property_changed("axis")


    #-----------------------------------------------------------------------------------
    @property
    def min_speed(self):
        """
        The minimal valid instantaneous speed (coords/sec).
        Only positive values are valid. None = minimal speed will not be enforced.
        
        If the finger completely stopped moving, speed information is N/A and this validation will not be triggered.
        To disallow full stops, use :attr:`~trajtracker.validators.InstantaneousSpeedValidator.max_stop_duration`
        """
        return self._min_speed

    @min_speed.setter
    def min_speed(self, value):
        _u.validate_attr_numeric(self, "min_speed", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_positive(self, "min_speed", value)
        self._min_speed = value
        self._log_property_changed("min_speed")

    #-----------------------------------------------------------------------------------
    @property
    def max_speed(self):
        """
        The maximal valid instantaneous speed (coords/sec).
        Only positive values are valid. None = maximal speed will not be enforced.
        """
        return self._max_speed

    @max_speed.setter
    def max_speed(self, value):
        _u.validate_attr_numeric(self, "max_speed", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_positive(self, "max_speed", value)
        self._max_speed = value
        self._log_property_changed("max_speed")

    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    def grace_period(self, value):
        value = _u.validate_attr_numeric(self, "grace_period", value, none_value=_u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "grace_period", value)
        self._grace_period = value
        self._log_property_changed("grace_period")

    #-----------------------------------------------------------------------------------
    @property
    def calculation_interval(self):
        """
        Time interval (in seconds) for testing speed: the speed is calculated according to the difference in
        (x,y) coordinates over a time interval at least this long.
        """
        return self._speed_monitor.calculation_interval

    @calculation_interval.setter
    def calculation_interval(self, value):
        self._speed_monitor.calculation_interval = value
        self._log_property_changed("calculation_interval")

    #-----------------------------------------------------------------------------------
    @property
    def max_stop_duration(self):
        """
        The maximal allowed duration of a finger/mouse stop in mid-trial
        
        :type: Number 
        """
        return self._max_stop_duration

    @max_stop_duration.setter
    def max_stop_duration(self, value):
        _u.validate_attr_type(self, "max_stop_duration", value, numbers.Number, none_allowed=True)
        _u.validate_attr_positive(self, "max_stop_duration", value)
        self._max_stop_duration = value
        self._log_property_changed("max_stop_duration")
