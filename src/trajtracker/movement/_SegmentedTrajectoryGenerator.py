"""

Generate a straight trajectory

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import numbers
import numpy as np

import trajtracker
import trajtracker._utils as _u
from trajtracker.data import fromXML


class SegmentedTrajectoryGenerator(trajtracker._TTrkObject):


    #---------------------------------------------------------------
    def __init__(self, segments=(), cyclic=False):

        super(SegmentedTrajectoryGenerator, self).__init__()

        self._segments = []
        self.cyclic = cyclic

        self.add_segments(segments)


    #============================================================================
    #     Get trajectory
    #============================================================================

    #---------------------------------------------------------------
    def get_traj_point(self, time):
        """
        Generate the trajectory - get one time point data

        :param time: in seconds
        :return: (x, y, visible)
        """

        _u.validate_func_arg_type(self, "get_traj_point", "time", time, numbers.Number)
        _u.validate_func_arg_not_negative(self, "get_traj_point", "time", time)

        #-- Handle time-too-large
        total_duration = self.duration
        if self._cyclic:
            time = time % total_duration
        elif time >= total_duration:
            last_segment = self._segments[-1]
            return last_segment['generator'].get_traj_point(last_segment['duration'])

        #-- Find relevant segment
        generator, time = self._get_generator_for(time)

        #-- Get point from the relevant segment
        return generator.get_traj_point(time)

    #---------------------------------------------------------------
    def _get_generator_for(self, time):

        for segment in self._segments:
            if time <= segment['duration']:
                return segment['generator'], time
            else:
                time -= segment['duration']

        raise Exception('trajtracker error: trajectory generator segment was not found, please report this bug')


    #============================================================================
    #     Configure
    #============================================================================

    # ---------------------------------------------------------------
    def add_segments(self, segments):

        _u.validate_func_arg_type(self, "add_segments", "segments", segments, (list, tuple))

        for i in range(len(segments)):
            segment = segments[i]
            _u.validate_func_arg_anylist(self, "add_segments", "segments[%d]" % i, segment, 2, 2)
            _u.validate_func_arg_type(self, "add_segments", "segments[%d][1]" % i, segment[1], numbers.Number)
            _u.validate_func_arg_positive(self, "add_segments", "segments[%d][1]" % i, segment[1])
            self.add_segment(segment[0], segment[1])


    # ---------------------------------------------------------------
    def add_segment(self, traj_generator, duration):

        _u.validate_func_arg_type(self, "add_segment", "duration", duration, numbers.Number)
        _u.validate_func_arg_positive(self, "add_segment", "duration", duration)

        if "get_traj_point" not in dir(traj_generator):
            raise TypeError("trajtracker error: {:}.add_segment() was called with an invalid traj_generator argument ({:})".format(
                type(self).__name__, traj_generator))

        self._segments.append(dict(generator=traj_generator, duration=duration))


    #------------------------------------------------------------
    @property
    def cyclic(self):
        """ Whether to stop after the trajectory duration has passed (False) or to restart the same trajectory (True) """
        return self._cyclic

    @cyclic.setter
    @fromXML(bool)
    def cyclic(self, value):
        _u.validate_attr_type(self, "cyclic", value, bool)
        self._cyclic = value

    #------------------------------------------------------------
    @property
    def duration(self):
        return sum([s['duration'] for s in self._segments])
