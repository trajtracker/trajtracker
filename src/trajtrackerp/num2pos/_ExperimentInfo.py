"""
Static elements in the number-to-position experiment

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

import expyriment as xpy

import trajtracker as ttrk
import trajtracker._utils as _u

from trajtrackerp.common import BaseExperimentInfo


class ExperimentInfo(BaseExperimentInfo):


    def __init__(self, config, xpy_exp, subject_id, subject_name):
        super(ExperimentInfo, self).__init__(config, xpy_exp, subject_id, subject_name)

        self._numberline = None
        self._target_pointer = None

        #: Specify, for each entry in sounds_ok, the maximal endpoint error acceptable for this sound.
        self.sounds_ok_max_ep_err = None


    #---------------------------------------------------------------
    @property
    def config(self):
        """
        The program's configuration parameters 
        
        :type: trajtrackerp.num2pos.Config  
        """
        return self._config


    #---------------------------------------------------------------
    @property
    def numberline(self):
        """
        The number line
        
        :type: trajtracker.stimuli.NumberLine 
        """
        return self._numberline

    @numberline.setter
    def numberline(self, nl):
        if self._numberline is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.numberline cannot be set twice")
        self._numberline = nl
        self.stimuli.add(nl, "numberline")
        self._trajectory_sensitive_objects.append(nl)
        self._event_sensitive_objects.append(nl)


    #---------------------------------------------------------------
    @property
    def target_pointer(self):
        """
        A stimulus that directly indicates the target location on the number line
        (in the default implementation, this is a down-pointing arrow)
        """
        return self._target_pointer

    @target_pointer.setter
    def target_pointer(self, value):
        if self._target_pointer is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.target_pointer cannot be set twice")

        self._target_pointer = value
        self.stimuli.add(value, "target_pointer", visible=False)

    #----------------------------------------------------------------
    def get_default_target_y(self):
        """
        Get the y coordinate where the target should be presented by default
        :return: tuple: (y coordinate, target height)
        """

        screen_top = self.screen_size[1] / 2
        height = screen_top - self.numberline.position[1] - self.config.stimulus_distance_from_top - 1
        y = int(screen_top - self.config.stimulus_distance_from_top - height / 2)
        return y, height


    #----------------------------------------------------------------
    def speed_validation_end_y_coord(self):
        """
        Get the y coordinate where speed validation should end
        """
        return self.numberline.position[1]
