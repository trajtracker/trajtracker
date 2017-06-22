"""
Static elements in the discrete-choice experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy

import trajtracker as ttrk
import trajtracker._utils as _u

from trajtracker.paradigms.common import BaseExperimentInfo, validate_config_param_type


class ExperimentInfo(BaseExperimentInfo):

    def __init__(self, config, xpy_exp, subject_id, subject_name):
        super(ExperimentInfo, self).__init__(config, xpy_exp, subject_id, subject_name)

        self._response_buttons = []
        self._response_hotspots = []
        self._feedback_stimuli = []

    #---------------------------------------------------------------
    @property
    def config(self):
        """
        The program's configuration parameters 

        :type: trajtracker.paradigms.dchoice.Config  
        """
        return self._config


    #---------------------------------------------------------------
    @property
    def response_buttons(self):
        return self._response_buttons


    #---------------------------------------------------------------
    @property
    def response_hotspots(self):
        return self._response_hotspots


    #---------------------------------------------------------------
    @property
    def feedback_stimuli(self):
        return self._feedback_stimuli


    #----------------------------------------------------------------
    def get_default_target_y(self):
        """
        Get the y coordinate where the target should be presented by default
        :return: tuple: (y coordinate, target height)
        """

        screen_top = self.screen_size[1] / 2
        height = self.get_response_buttons_size()[1]
        y = int(screen_top - self.config.stimulus_distance_from_top - height / 2)
        return y, height

    #----------------------------------------------------------------
    def get_response_buttons_size(self):

        width, height = validate_config_param_type("resp_btn_size", ttrk.TYPE_SIZE,
                                                   self.config.resp_btn_size)

        # -- If width/height are between [-1,1], they mean percentage of screen size
        if -1 < width < 1:
            width = int(width * self.screen_size[0])
        elif not isinstance(width, int):
            raise ttrk.ValueError("Invalid config.resp_btn_size: a non-integer width was provided ({:})".format(width))
        if -1 < height < 1:
            height = int(height * self.screen_size[1])
        elif not isinstance(height, int):
            raise ttrk.ValueError(
                "Invalid config.resp_btn_size: a non-integer height was provided ({:})".format(height))

        return width, height


    #----------------------------------------------------------------
    def speed_validation_end_y_coord(self):
        """
        Get the y coordinate where speed validation should end
        """
        return self.screen_size[1]
