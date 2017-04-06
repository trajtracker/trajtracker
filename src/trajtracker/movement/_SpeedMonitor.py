"""

Movement monitor: continuously track the movement speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers
import numpy as np

import trajtracker
import trajtracker._utils as _u


class SpeedMonitor(trajtracker._TTrkObject):


    #-------------------------------------------------------------------------
    def __init__(self, calculation_interval):
        """
        Constructor - invoked when you create a new object by writing SpeedMonitor()

        :param calculation_interval: See :attr:`~trajtracker.movement.SpeedMonitor.calculation_interval`
        """
        super(SpeedMonitor, self).__init__()

        self.calculation_interval = calculation_interval

        self.reset()



    #====================================================================================
    #   Runtime API - update movement
    #====================================================================================


    #-------------------------------------------------------------------------
    def reset(self, time=None):
        """
        Called when a trial starts - reset any previous movement

        :param time: The time when the trial starts.
        """

        if time is not None and not isinstance(time, (int, float)):
            raise ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time))

        self._log_func_enters("reset", [time])

        self._recent_points = []
        self._pre_recent_point = None
        self._time0 = time


    #-------------------------------------------------------------------------
    # noinspection PyIncorrectDocstring
    def update_xyt(self, x_coord, y_coord, time):
        """
        Call this method whenever the finger/mouse moves

        :param time: use the same time scale provided to reset()
        """

        _u.validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time, numbers.Number)
        self._validate_time(time)

        self._log_func_enters("update_xyt", [x_coord, y_coord, time])

        if self._time0 is None:
            self._time0 = time

        #-- Find distance to recent coordinate
        if len(self._recent_points) > 0:
            last_loc = self._recent_points[-1]
            if time == last_loc[2]:
                return
            distance = np.sqrt((x_coord-last_loc[0]) ** 2 + (y_coord-last_loc[1]) ** 2)
        else:
            distance = 0

        self._remove_recent_points_older_than(time - self._calculation_interval)

        #-- Remember current coords & time
        self._recent_points.append((x_coord, y_coord, time, distance))


    #--------------------------------------
    def _validate_time(self, time):

        #-- Validate that times are provided in increasing order
        prev_time = self._recent_points[-1][2] if len(self._recent_points) > 0 else self._time0
        if prev_time is not None and prev_time > time:
            raise trajtracker.InvalidStateError("{0}.update_xyt() was called with time={1} after it was previously called with time={2}".format(self.__class__, time, prev_time))


    #--------------------------------------
    # Remove all _recent_points that are older than the given threshold.
    # Remember the newest removed point.
    #
    def _remove_recent_points_older_than(self, latest_good_time):

        if len(self._recent_points) == 0:
            return

        #-- find _recent_points that are old enough to remove
        older_than_threshold = np.where([p[2] <= latest_good_time for p in self._recent_points])[0]

        if len(older_than_threshold) >= 1:
            last_ind_to_remove = older_than_threshold[-1]
            self._pre_recent_point = self._recent_points[last_ind_to_remove]
            self._recent_points = self._recent_points[last_ind_to_remove+1:]


    #====================================================================================
    #   Runtime API - get info about movement
    #====================================================================================

    #-------------------------------------------------------------------------
    @property
    def time_in_trial(self):
        """ Time elapsed since trial started (sec) """

        if self._time0 is None or len(self._recent_points) == 0:
            return None

        return self._recent_points[-1][2] - self._time0


    #-------------------------------------------------------------------------
    @property
    def xspeed(self):
        """ The instantaneous X speed (coords/sec) """

        if self._pre_recent_point is None:
            return None

        y1 = self._pre_recent_point[0]
        y2 = self._recent_points[-1][0]
        return (y2-y1) / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def yspeed(self):
        """ The instantaneous Y speed (coords/sec) """

        if self._pre_recent_point is None:
            return None

        y1 = self._pre_recent_point[1]
        y2 = self._recent_points[-1][1]
        return (y2-y1) / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def xyspeed(self):
        """
        The instantaneous speed (coords/sec) - for this calculation we consider the full distance traveled by the mouse/finger
        """

        if self._pre_recent_point is None:
            return None

        distance = sum([loc[3] for loc in self._recent_points])
        return distance / self.last_calculation_interval


    #-------------------------------------------------------------------------
    @property
    def last_calculation_interval(self):
        """ The time interval (sec) used for the last calculation of speed & direction """

        if self._pre_recent_point is None:
            return None
        else:
            return self._recent_points[-1][2] - self._pre_recent_point[2]


    #====================================================================================
    #   Properties
    #====================================================================================

    #-------------------------------------------------------------------------
    @property
    def calculation_interval(self):
        """
        The time interval (in seconds) over which calculations are performed.
        Use shorter time period if available
        """
        return self._calculation_interval


    @calculation_interval.setter
    def calculation_interval(self, value):
        _u.validate_attr_type(self, "calculation_interval", value, numbers.Number)
        _u.validate_attr_not_negative(self, "calculation_interval", value)
        self._calculation_interval = value
        self._log_setter("calculation_interval")
