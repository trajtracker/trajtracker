"""

Movement monitor: continuously track the movement speed

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


class SpeedMonitor(trajtracker.TTrkObject):


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
            raise trajtracker.ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time))

        self._log_func_enters("reset", [time])

        self._recent_points = []
        self._pre_recent_point = None
        self._last_moved_time = None
        self._last_stopped_time = None
        self._time0 = time


    #-------------------------------------------------------------------------
    # noinspection PyIncorrectDocstring
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Call this method whenever the finger/mouse moves

        :param time_in_trial: use the same time scale provided to reset()
        :param time_in_session: ignored
        """

        _u.update_xyt_validate_and_log(self, position, time_in_trial)
        self._validate_time(time_in_trial)

        x_coord, y_coord = position

        if self._time0 is None:
            self._time0 = time_in_trial

        if len(self._recent_points) == 0:
            distance = 0

        else:
            #-- Find distance to the last observed coordinate
            last_loc = self._recent_points[-1]
            if time_in_trial <= last_loc[2]:
                return  # The time did not move forward: ignore this data

            if x_coord == last_loc[0] and y_coord == last_loc[1]:
                # The coordinates did not change: ignore this data for speed calculation, but remember
                # for how long the finger is stopped
                self._last_stopped_time = time_in_trial
                return

            distance = np.sqrt((x_coord-last_loc[0]) ** 2 + (y_coord-last_loc[1]) ** 2)

        self._last_moved_time = time_in_trial
        self._last_stopped_time = None

        self._remove_recent_points_older_than(time_in_trial - self._calculation_interval)

        #-- Remember current coords & time
        self._recent_points.append((x_coord, y_coord, time_in_trial, distance))


    #--------------------------------------
    def _validate_time(self, time):

        #-- Validate that times are provided in increasing order
        prev_time = self._recent_points[-1][2] if len(self._recent_points) > 0 else self._time0
        if prev_time is not None and prev_time > time:
            raise trajtracker.InvalidStateError(
                "{:}.update_xyt() was called with time={:} after it was previously called with time={:}".format(
                    _u.get_type_name(self), time, prev_time))


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


    #-------------------------------------------------------------------------
    @property
    def stopped_duration(self):
        """ 
        If the finger is stopped, this tells you for how long it's been so.
        If the finger is moving, or didn't start moving yet, this will return 0.
        """

        if self._last_stopped_time is None or self._last_moved_time is None:
            return 0
        else:
            return self._last_stopped_time - self._last_moved_time


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
        self._log_property_changed("calculation_interval")
