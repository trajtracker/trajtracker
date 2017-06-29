"""
Configuration of a number-to-position experiment

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

from enum import Enum
import expyriment as xpy
# noinspection PyProtectedMember
from trajtrackerp.common._BaseConfig import BaseConfig
from trajtrackerp import sounds_dir


class Config(BaseConfig):
    """
    Defines the set of configuration parameters supported by this implementation of
    the number-to-position experiment
    """

    def __init__(self, experiment_id, data_source, max_trial_duration,
                 use_text_targets=True, use_generic_targets=False,

                 fixation_type='cross', fixation_text=None,
                 fixzoom_box_size=(40, 40), fixzoom_dot_radius=3,
                 fixzoom_dot_colour=xpy.misc.constants.C_GREY,
                 fixzoom_zoom_duration=0.2, fixzoom_stay_duration=0.1,
                 fixzoom_show_event=None, fixzoom_start_zoom_event=None,

                 text_target_height=0.6, shuffle_trials=True,
                 log_stimulus_onset_offset=False,
                 min_trial_duration=0.2, speed_guide_enabled=False, min_inst_speed=10,
                 grace_period=0.3, max_zigzags=8, save_results=True, sound_by_accuracy=None,
                 sounds_dir=sounds_dir,
                 stimulus_then_move=False, finger_must_start_upwards=True,
                 finger_moves_min_time=None, finger_moves_max_time=None,

                 start_point_size=(40, 30), start_point_tilt=0,
                 start_point_colour=xpy.misc.constants.C_GREY,

                 confidence_rating=False,

                 nl_length=0.9, min_numberline_value=0, max_numberline_value=100, nl_labels_visible=True,
                 show_feedback=True, feedback_arrow_colors=xpy.misc.constants.C_GREEN,
                 feedback_accuracy_levels=None, post_response_target=False,
                 nl_line_width=2, nl_end_tick_height=5, nl_line_colour=xpy.misc.constants.C_WHITE,
                 nl_labels_font_name="Arial", nl_labels_box_size=(100, 30), nl_labels_offset=(0, 20),
                 nl_labels_colour=xpy.misc.constants.C_GREY, nl_distance_from_top=80,
                 max_response_excess=None):

        super(Config, self).__init__(
            experiment_id=experiment_id,
            data_source=data_source,
            max_trial_duration=max_trial_duration,
            use_text_targets=use_text_targets,
            use_generic_targets=use_generic_targets,
            fixation_type=fixation_type,
            fixation_text=fixation_text,
            fixzoom_box_size=fixzoom_box_size,
            fixzoom_dot_radius=fixzoom_dot_radius,
            fixzoom_dot_colour=fixzoom_dot_colour,
            fixzoom_zoom_duration=fixzoom_zoom_duration,
            fixzoom_stay_duration=fixzoom_stay_duration,
            fixzoom_show_event=fixzoom_show_event,
            fixzoom_start_zoom_event=fixzoom_start_zoom_event,
            text_target_height=text_target_height,
            shuffle_trials=shuffle_trials,
            log_stimulus_onset_offset=log_stimulus_onset_offset,
            min_trial_duration=min_trial_duration,
            speed_guide_enabled=speed_guide_enabled,
            min_inst_speed=min_inst_speed,
            grace_period=grace_period,
            max_zigzags=max_zigzags,
            save_results=save_results,
            sounds_dir=sounds_dir,
            stimulus_then_move=stimulus_then_move,
            finger_must_start_upwards=finger_must_start_upwards,
            finger_moves_min_time=finger_moves_min_time,
            finger_moves_max_time=finger_moves_max_time,
            start_point_size=start_point_size,
            start_point_tilt=start_point_tilt,
            start_point_colour=start_point_colour,
            confidence_rating=confidence_rating
        )

        #----- Configuration of number line -----

        #: The length of the number line. The length is specified either in pixels (an int value larger than 1)
        #: or as percentage of the screen width (a number between 0 and 1)
        self.nl_length = nl_length

        # The values at the left/right ends of the number line
        self.min_numberline_value = min_numberline_value
        self.max_numberline_value = max_numberline_value

        # Whether to show labels at the end of the number line
        self.nl_labels_visible = nl_labels_visible

        # Whether to show a feedback arrow (where the finger landed on the number line)
        self.show_feedback = show_feedback

        # Use this to show the feedback arrow in different colors, depending on the response accuracy.
        # Define a list of numbers between 0 and 1 (percentages of the number line length)
        self.feedback_accuracy_levels = feedback_accuracy_levels

        # Color of the feedback arrow (or a list of colors, in case you defined feedback_accuracy_levels;
        # in this case, the first color corresponds with best accuracy)
        self.feedback_arrow_colors = feedback_arrow_colors

        # Whether to show the correct target location after the response was made
        self.post_response_target = post_response_target

        self.max_response_excess = max_response_excess
        self.nl_line_width = nl_line_width
        self.nl_end_tick_height = nl_end_tick_height
        self.nl_line_colour = nl_line_colour
        self.nl_labels_font_name = nl_labels_font_name
        self.nl_labels_box_size = nl_labels_box_size
        self.nl_labels_offset = nl_labels_offset
        self.nl_labels_colour = nl_labels_colour
        self.nl_distance_from_top = nl_distance_from_top  # Distance of the numberline's main line from top-of-screen

        #----- Configuration of sounds -----

        # Use this in order to play a different sound depending on the subject's accuracy.
        # The parameter should be a list/tuple with several elements, each of which is a (endpoint_error, sound)
        # tuple. "endpoint_error" indicates a top error (as ratio of the number line length),
        # and "sound" is a sound file name.
        # The worst accuracy is ignored (e.g., if you specify [(0.05, 'good.wav'), (0.5, 'bad.wav')]
        # the program will play good.wav for endpoint errors up to 5% of the line length, and bad.wav for
        # any larger error
        self.sound_by_accuracy = sound_by_accuracy
