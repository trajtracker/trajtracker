"""
Configuration of the number-to-position experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import trajtracker as ttrk


#-- This event is dispatched when the finger leaves the "start" area and starts moving towards
#-- the number line
FINGER_STARTED_MOVING = ttrk.events.Event("FINGER_STARTED_MOVING")

#-- 3 possibilities for the feedback that indicates where the finger landed on the number line.
#-- If you want a different shape as feedback, create it by yourself.
FeedbackType = Enum('FeedbackType', 'none Arrow Line')


class Config(object):
    """
    Defines the set of configuration parameters supported by this implementation of
    the number-to-position experiment
    """

    def __init__(self, experiment_id, data_source, max_trial_duration, shuffle_trials=True, max_numberline_value=100,
                 nl_feedback_type=FeedbackType.Arrow, stimulus_then_move=False,
                 min_trial_duration=0.2, speed_guide_enabled=False, min_inst_speed=20,
                 grace_period=0.3, max_zigzags=8, save_results=True, sound_by_accuracy=None):

        # A unique identifier of this experiment.
        # This string is saved as-is to the results file, to identify the experiment.
        self.experiment_id = experiment_id

        # The trials information. This can be:
        # - The name of a CSV file(string)
        # - An explicit list of trials
        # - A list of target numbers
        self.data_source = data_source

        # If True, trials will be presented in random order
        self.shuffle_trials = shuffle_trials

        # The value at the right end of the number line
        self.max_numberline_value = max_numberline_value

        # True: The software decides when the target appears, and then the finger must start moving
        # False: The finger moves at will and this is what triggers the appearance of the target
        self.stimulus_then_move = stimulus_then_move

        # The shape of the feedback stimulus that indicates where the finger landed on the number line.
        # If you want a non-default shape as feedback, put here "None" and create the shape yourself in the
        # init function.
        self.nl_feedback_type = nl_feedback_type

        # Use this in order to play a different sound depending on the subject's accuracy.
        # The parameter should be a list/tuple with several elements, each of which is a (endpoint_error, sound)
        # tuple. "endpoint_error" indicates a top error (as ratio of the number line length),
        # and "sound" is a sound file name.
        # The worst accuracy is ignored (e.g., if you specify [(0.05, 'good.wav'), (0.5, 'bad.wav')]
        # the program will play good.wav for endpoint errors up to 5% of the line length, and bad.wav for
        # any larger error
        self.sound_by_accuracy = sound_by_accuracy

        #----- Configuration of validators

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
