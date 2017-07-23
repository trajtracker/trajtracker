"""
Validate that finger was not lifted in mid-trial

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

from enum import Enum
import numbers
import numpy as np

import expyriment as xpy

import trajtracker
import trajtracker._utils as _u
import trajtracker.validators
from trajtracker.misc import EnabledDisabledObj
from trajtracker.validators import ExperimentError


# noinspection PyAttributeOutsideInit
class FingerLiftedValidator(trajtracker.TTrkObject, EnabledDisabledObj):

    err_finger_lifted = "FingerLifted"


    #--------------------------------------------------------------------------
    def __init__(self, enabled=True, max_offscreen_duration=0):
        """
        Constructor

        :param enabled: See :attr:`~trajtracker.validators.FingerLiftedValidator.enabled`
        :param max_offscreen_duration: See :attr:`~trajtracker.validators.FingerLiftedValidator.max_offscreen_duration`
        """

        super(FingerLiftedValidator, self).__init__()
        EnabledDisabledObj.__init__(self, enabled=enabled)

        self.max_offscreen_duration = max_offscreen_duration
        self._last_touched_time = None

        self.reset()


    #--------------------------------------------------------------------------
    @property
    def max_offscreen_duration(self):
        """
        The maximal duration (in seconds) that the finger is allowed to remain off-screen in mid trial.

        :type: number
        """
        return self._max_offscreen_duration

    @max_offscreen_duration.setter
    def max_offscreen_duration(self, value):
        _u.validate_attr_type(self, "max_offscreen_duration", value, numbers.Number)
        _u.validate_attr_not_negative(self, "max_offscreen_duration", value)
        self._max_offscreen_duration = value


    #--------------------------------------------------------------------------
    def reset(self, time=None):
        """
        Called when a trial starts - reset any previous movement
        """
        self._last_touched_time = None


    #--------------------------------------------------------------------------
    # noinspection PyUnusedLocal
    def update_touching(self, touching, time_in_trial, time_in_session):
        """
        Validate movement.

        :param touching: Whether the finger is currently touching the screen (or mouse is clicked)
        :type touching: bool
        :param time_in_trial: Time from start of trial
        :param time_in_session: Time from start of session
        :returns: None if all OK; ExperimentError object if error
        """

        if touching:
            #-- Update touch time
            self._last_touched_time = time_in_session

        elif self._last_touched_time is None:
            #-- Not touched yet
            return None

        elif self._enabled and (self._max_offscreen_duration == 0 or (time_in_session - self._last_touched_time) > self._max_offscreen_duration):
            #-- Finger lifted for too long
            return trajtracker.validators.create_experiment_error(
                self, self.err_finger_lifted, "You lifted your finger")

        return None