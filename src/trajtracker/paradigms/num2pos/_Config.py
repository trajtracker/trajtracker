"""
Configuration of the number-to-position experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import expyriment as xpy
import trajtracker as ttrk


#-- This event is dispatched when the finger leaves the "start" area and starts moving towards
#-- the number line
FINGER_STARTED_MOVING = ttrk.events.Event("FINGER_STARTED_MOVING")


class Config(object):
    """
    Defines the set of configuration parameters supported by this implementation of
    the number-to-position experiment
    """

    def __init__(self, experiment_id, data_source, max_trial_duration, target_type='text',
                 text_target_height=1.0, shuffle_trials=True, max_numberline_value=100,
                 show_feedback=True, feedback_arrow_colors=xpy.misc.constants.C_GREEN,
                 feedback_accuracy_levels=None, post_response_target=False,
                 min_trial_duration=0.2, speed_guide_enabled=False, min_inst_speed=10,
                 grace_period=0.3, max_zigzags=8, save_results=True, sound_by_accuracy=None,
                 stimulus_then_move=False, start_point_size=(40, 30), start_point_tilt=0,
                 start_point_colour=xpy.misc.constants.C_GREY):

        # A unique identifier of this experiment.
        # This string is saved as-is to the results file, to identify the experiment.
        self.experiment_id = experiment_id


        #----- Configuration of source data -----

        # The trials information. This can be:
        # - The name of a CSV file(string)
        # - An explicit list of trials
        # - A list of target numbers
        self.data_source = data_source

        # If True, trials will be presented in random order
        self.shuffle_trials = shuffle_trials

        # The type of the target presented.
        # Different target types require different fields in the CSV data file
        ['text', 'picture'].index(target_type)  # validate that the target type is OK
        self.target_type = target_type

        # The height of the text target, specified as percentage of the available distance
        # between the number line and the top of the screen (value between 0 and 1).
        # The actual target size will be printed in the output
        self.text_target_height = text_target_height

        #----- Configuration of number line -----

        # The value at the right end of the number line
        self.max_numberline_value = max_numberline_value

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


        #----- Configuration of the "start" rectangle -----

        # True: The software decides when the target appears, and then the finger must start moving
        # False: The finger moves at will and this is what triggers the appearance of the target
        self.stimulus_then_move = stimulus_then_move

        # The size of the "start" rectangle: (width, height)
        self.start_point_size = start_point_size

        # Rotation of the "start" rectangle (clockwise degrees)
        self.start_point_tilt = start_point_tilt

        # Colour of the "start" rectangle
        self.start_point_colour = start_point_colour


        #----- Configuration of sounds -----

        # Use this in order to play a different sound depending on the subject's accuracy.
        # The parameter should be a list/tuple with several elements, each of which is a (endpoint_error, sound)
        # tuple. "endpoint_error" indicates a top error (as ratio of the number line length),
        # and "sound" is a sound file name.
        # The worst accuracy is ignored (e.g., if you specify [(0.05, 'good.wav'), (0.5, 'bad.wav')]
        # the program will play good.wav for endpoint errors up to 5% of the line length, and bad.wav for
        # any larger error
        self.sound_by_accuracy = sound_by_accuracy

        #----- Configuration of validators -----

        # Minimal and maximal valid time for reaching the number line (in seconds)
        self.min_trial_duration = min_trial_duration
        self.max_trial_duration = max_trial_duration

        # If True, the speed limit will be visualized as a moving line
        self.speed_guide_enabled = speed_guide_enabled

        # The minimal instantaneous speed (coord-per-second)
        self.min_inst_speed = min_inst_speed

        # (for both speed validators) Duration in the beginning of the trial during which speed
        # is not validated (in seconds).
        self.grace_period = grace_period

        #  (for zigzag validator) Maximal number of left-right deviations allowed per trial
        self.max_zigzags = max_zigzags

        # Whether to save the results (trials and trajectory)
        self.save_results = save_results
