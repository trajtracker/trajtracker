"""

 Validate the number of curves per trial

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
from trajtracker.data import fromXML


class NCurvesValidator(_BaseValidator):
    """
    Validate that there aren't too many curves per trial (i.e., that the participant is not zigzagging)

    A curve is defined as a trajectory section where the finger/mouse consistently changes its course
    in the same direction (clockwise or counter-clockwise).

    """


    err_too_many_curves = "TooManyCurves"


    #-----------------------------------------------------------------
    def __init__(self, direction_monitor=None, max_curves_per_trial=None, enabled=True):
        """
        Constructor

        :param direction_monitor: A :class:`~trajtracker.movement.DirectionMonitor` object for tracking curves.
                                  If this object is not provided, a default one would be created.
        :param max_curves_per_trial: See :attr:`~trajtracker.validators.NCurvesValidator.max_curves_per_trial`
        :param enabled: See :attr:`~trajtracker.validators.NCurvesValidator.enabled`
        """

        super(NCurvesValidator, self).__init__(enabled=enabled)

        if direction_monitor is None:
            direction_monitor = trajtracker.movement.DirectionMonitor(1)

        self._direction_monitor = direction_monitor
        self.max_curves_per_trial = max_curves_per_trial



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
    def check_xyt(self, x_coord, y_coord, time):
        """
        Validate the number of curves in the trial

        :param x_coord: Current x coordinate (in the predefined coordinate system)
        :param y_coord: Current y coordinate (in the predefined coordinate system)
        :param time: Time, in seconds. The zero point doesn't matter, as long as you're consistent until reset() is called.
        :return: None if all OK, ExperimentError if error
        """

        self._check_xyt_validate_and_log(x_coord, y_coord, time)
        self._direction_monitor.update_xyt(x_coord, y_coord, time)

        if not self.enabled:
            return None

        if self._direction_monitor.n_curves > self._max_curves_per_trial:
            return self._create_experiment_error(self.err_too_many_curves, "Too many left-right deviations", {})

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
    @fromXML(int)
    def max_curves_per_trial(self, value):
        _u.validate_attr_numeric(self, "max_curves_per_trial", value, none_value=_u.NoneValues.Valid)
        _u.validate_attr_not_negative(self, "max_curves_per_trial", value)
        self._max_curves_per_trial = value

    #-------------------------------------
    @property
    def min_distance(self):
        """
        The minimal distance between points required for calculating direction
        (see :attr:`trajtracker.movement.DirectionMonitor.min_distance`)
        """
        return self._direction_monitor.min_distance

    @min_distance.setter
    @fromXML(float)
    def min_distance(self, value):
        self._direction_monitor.min_distance = value


    #-------------------------------------
    @property
    def min_angle_change_per_curve(self):
        """
        A curve must change the finger/mouse direction by at least this amount (specified in degrees).
        Smaller changes do not count as curves.
        (see :attr:`trajtracker.movement.DirectionMonitor.min_angle_change_per_curve`)
        """
        return self._direction_monitor.min_angle_change_per_curve

    @min_angle_change_per_curve.setter
    @fromXML(float)
    def min_angle_change_per_curve(self, value):
        self._direction_monitor.min_angle_change_per_curve = value
