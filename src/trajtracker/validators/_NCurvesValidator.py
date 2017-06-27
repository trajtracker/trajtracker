"""

 Validate the number of curves per trial

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

import trajtracker
import trajtracker._utils as _u
import trajtracker.utils as u
import trajtracker.validators
from trajtracker.misc import EnabledDisabledObj


class NCurvesValidator(trajtracker.TTrkObject, EnabledDisabledObj):


    err_too_many_curves = "TooManyCurves"


    #-----------------------------------------------------------------
    def __init__(self, direction_monitor=None, max_curves_per_trial=None, enabled=True):
        """
        Constructor - invoked when you create a new object by writing NCurvesValidator()

        :param direction_monitor: A :class:`~trajtracker.movement.DirectionMonitor` object for tracking curves.
                                  If this object is not provided, a default one would be created.
        :param max_curves_per_trial: See :attr:`~trajtracker.validators.NCurvesValidator.max_curves_per_trial`
        :param enabled: See :attr:`~trajtracker.validators.NCurvesValidator.enabled`
        """

        trajtracker.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        if direction_monitor is None:
            direction_monitor = trajtracker.movement.DirectionMonitor(20)

        self._direction_monitor = direction_monitor
        self.max_curves_per_trial = max_curves_per_trial


    #-------------------------------------
    @property
    def direction_monitor(self):
        return self._direction_monitor


    #=================================================================
    #    Validate
    #=================================================================

    #-----------------------------------------------------------
    # noinspection PyUnusedLocal
    def reset(self, time0=None):
        """
        Called when a trial starts - reset any previous curves
        """

        self._log_func_enters("reset", [time0])

        self._direction_monitor.reset()


    #-----------------------------------------------------------
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Validate the number of curves in the trial

        :param position: Current (x,y) coordinates
        :param time_in_trial: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :param time_in_session: ignored
        :return: None if all OK, ExperimentError if error
        """

        _u.update_xyt_validate_and_log(self, position, time_in_trial)
        self._direction_monitor.update_xyt(position, time_in_trial)

        if not self.enabled:
            return None

        if self._direction_monitor.n_curves > self._max_curves_per_trial:
            return trajtracker.validators.create_experiment_error(self, self.err_too_many_curves, "Too many left-right deviations", {})

        return None


    #=================================================================
    #    Configure
    #=================================================================

    #----------------------------------------------------
    @property
    def max_curves_per_trial(self):
        """
        Maximal number of curves allowed per trial.
        """
        return self._max_curves_per_trial

    @max_curves_per_trial.setter
    def max_curves_per_trial(self, value):
        _u.validate_attr_numeric(self, "max_curves_per_trial", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_not_negative(self, "max_curves_per_trial", value)
        self._max_curves_per_trial = value
        self._log_property_changed("max_curves_per_trial")

    #-------------------------------------
    @property
    def min_distance(self):
        """
        The minimal distance between points required for calculating direction
        (see :attr:`DirectionMonitor.min_distance <trajtracker.movement.DirectionMonitor.min_distance>`)
        """
        return self._direction_monitor.min_distance

    @min_distance.setter
    def min_distance(self, value):
        self._direction_monitor.min_distance = value
        self._log_property_changed("min_distance")


    #-------------------------------------
    @property
    def min_angle_change_per_curve(self):
        """
        A curve must change the finger/mouse direction by at least this amount (specified in degrees).
        Smaller changes do not count as curves.
        (see :attr:`DirectionMonitor.min_angle_change_per_curve <trajtracker.movement.DirectionMonitor.min_angle_change_per_curve>`)
        """
        return self._direction_monitor.min_angle_change_per_curve

    @min_angle_change_per_curve.setter
    def min_angle_change_per_curve(self, value):
        self._direction_monitor.min_angle_change_per_curve = value
        self._log_property_changed("min_angle_change_per_curve")
