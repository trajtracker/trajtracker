"""

Generate a straight trajectory

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


class LineTrajectoryGenerator(trajtracker.TTrkObject):

    #---------------------------------------------------------------
    def __init__(self, start_point=None, end_point=None, duration=None, return_to_start=False, cyclic=False):
        """
        Constrcutor

        :param start_point: See :attr:`~trajtracker.movement.LineTrajectoryGenerator.start_point`
        :param end_point: See :attr:`~trajtracker.movement.LineTrajectoryGenerator.end_point`
        :param duration: See :attr:`~trajtracker.movement.LineTrajectoryGenerator.duration`
        :param return_to_start: See :attr:`~trajtracker.movement.LineTrajectoryGenerator.return_to_start`
        :param cyclic: See :attr:`~trajtracker.movement.LineTrajectoryGenerator.cyclic`
        """

        super(LineTrajectoryGenerator, self).__init__()

        self._start_point = None
        self._end_point = None
        self._duration = None
        self.return_to_start = return_to_start
        self.cyclic = cyclic

        if start_point is not None:
            self.start_point = start_point

        if end_point is not None:
            self.end_point = end_point

        if duration is not None:
            self.duration = duration


    #============================================================================
    #     Get trajectory
    #============================================================================


    def get_traj_point(self, time):
        """
        Return the trajectory info at a certain time

        :param time: in seconds
        :returns: a dict with the coordinates ('x' and 'y' entries).
        """

        _u.validate_func_arg_type(self, "get_xy", "time", time, numbers.Number)
        if self._start_point is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting start_point".format(_u.get_type_name(self)))
        if self._end_point is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting end_point".format(_u.get_type_name(self)))
        if self._duration is None:
            raise trajtracker.InvalidStateError("{:}.get_xy() was called without setting duration".format(_u.get_type_name(self)))

        max_duration = self._duration * (2 if self._return_to_start else 1)
        if self._cyclic:
            time = time % max_duration
        else:
            time = min(time, max_duration)

        if time > self._duration:
            #-- Returning to start
            time -= self._duration
            start_pt = self._end_point
            end_pt = self._start_point
        else:
            start_pt = self._start_point
            end_pt = self._end_point

        time_ratio = time / self._duration
        x = start_pt[0] + time_ratio * (end_pt[0] - start_pt[0])
        y = start_pt[1] + time_ratio * (end_pt[1] - start_pt[1])

        return dict(x=x, y=y)



    #============================================================================
    #     Configure
    #============================================================================

    #------------------------------------------------------------
    @property
    def start_point(self):
        """
        The trajecotry starting point (x,y)
        """
        return self._start_point

    @start_point.setter
    def start_point(self, value):
        value = _u.validate_attr_is_coord(self, "start_point", value)
        self._start_point = value
        self._log_property_changed("start_point")


    #------------------------------------------------------------
    @property
    def end_point(self):
        """
        The trajecotry end point (x,y)
        """
        return self._end_point

    @end_point.setter
    def end_point(self, value):
        value = _u.validate_attr_is_coord(self, "end_point", value)
        self._end_point = value
        self._log_property_changed("end_point")


    #------------------------------------------------------------
    @property
    def duration(self):
        """
        The time (in seconds) it should take for moving from start to end.
        """
        return self._duration

    @duration.setter
    def duration(self, value):
        _u.validate_attr_type(self, "duration", value, numbers.Number)
        _u.validate_attr_positive(self, "duration", value)
        self._duration = value
        self._log_property_changed("duration")


    #------------------------------------------------------------
    @property
    def return_to_start(self):
        """ If True, the trajectory will go to the end point and then back to the start point """
        return self._return_to_start

    @return_to_start.setter
    def return_to_start(self, value):
        _u.validate_attr_type(self, "return_to_start", value, bool)
        self._return_to_start = value
        self._log_property_changed("return_to_start")


    #------------------------------------------------------------
    @property
    def cyclic(self):
        """ Whether to stop after the trajectory duration has passed (False) or to restart the same trajectory (True) """
        return self._cyclic

    @cyclic.setter
    def cyclic(self, value):
        _u.validate_attr_type(self, "cyclic", value, bool)
        self._cyclic = value
        self._log_property_changed("cyclic")
