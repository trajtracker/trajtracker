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

    def __init__(self, experiment_id, data_source, max_trial_duration,
                 use_text_targets=True, use_generic_targets=False,
                 fixation_type='cross', fixation_text=None,
                 text_target_height=0.6, shuffle_trials=True,
                 nl_length=0.9, min_numberline_value=0, max_numberline_value=100,
                 show_feedback=True, feedback_arrow_colors=xpy.misc.constants.C_GREEN,
                 feedback_accuracy_levels=None, post_response_target=False,
                 min_trial_duration=0.2, speed_guide_enabled=False, min_inst_speed=10,
                 grace_period=0.3, max_zigzags=8, save_results=True, sound_by_accuracy=None, sounds_dir="sounds",
                 stimulus_then_move=False, finger_moves_min_time=None, finger_moves_max_time=None,
                 start_point_size=(40, 30), start_point_tilt=0,
                 start_point_colour=xpy.misc.constants.C_GREY):

        #: A unique identifier of this experiment.
        #: This string is saved as-is to the results file, to identify the experiment.
        self.experiment_id = experiment_id


        #----- Configuration of source data & targets -----

        #: The trials information. This can be:
        #: - The name of a CSV file(string)
        #: - An explicit list of trials
        #: - A list of target numbers
        self.data_source = data_source

        # If True, trials will be presented in random order
        self.shuffle_trials = shuffle_trials

        # Whether to use generic targets (e.g. pictures) and text targets.
        # Each of these values can be True, False, or None (which means that a column by this name is
        # expected in the CSV file)
        self.use_text_targets = use_text_targets
        self.use_generic_targets = use_generic_targets

        # The height of the text target, specified as percentage of the available distance
        # between the number line and the top of the screen (value between 0 and 1).
        # The actual target size will be printed in the output
        self.text_target_height = text_target_height

        #: The type of fixation to use: 'cross', 'text', or None
        self.fixation_type = fixation_type

        #: Default text to use for a text fixation
        self.fixation_text = fixation_text

        #----- Configuration of number line -----

        #: The length of the number line. The length is specified either in pixels (an int value larger than 1)
        #: or as percentage of the screen width (a number between 0 and 1)
        self.nl_length = nl_length

        # The values at the left/right ends of the number line
        self.min_numberline_value = min_numberline_value
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

        # The minimal/maximal time in which the finger should start moving.
        # The time is specified relatively to the time when the finger touched the screen
        self.finger_moves_min_time = finger_moves_min_time
        self.finger_moves_max_time = finger_moves_max_time

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

        self.sounds_dir = sounds_dir

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

        #--------------------------------------------------------------------
        #    Advanced configuration
        #--------------------------------------------------------------------

        # Text target
        self.text_target_font = "Arial"
        self.text_target_width = 600         # Width of the text box
        self.text_target_colour = xpy.misc.constants.C_WHITE
        self.text_target_justification = 1  # 1=center
        self.text_target_x_coord = 0         # Position
        self.text_target_last_stimulus_remains = False  # See MultiTextBox.last_stimulus_remains

        # Generic target
        self.generic_target_x_coord = 0
        self.generic_target_last_stimulus_remains = False # See MultiStimulus.last_stimulus_remains

        # For text and non-text targets
        self.stimulus_distance_from_top = 5   # Distance of top of stimulus from top of screen
        self.target_onset_time = [0]          # Default onset time
        self.target_duration = [1000]  # 1000 seconds = never disappear

        # The textbox containing error messages
        self.errmsg_textbox_coords = 0, 0
        self.errmsg_textbox_size = 290, 180
        self.errmsg_textbox_font_size = 16
        self.errmsg_textbox_font_name = "Arial"
        self.errmsg_textbox_font_colour = xpy.misc.constants.C_RED

        # Sounds
        self.sound_err = 'error.wav'
        self.sound_ok = 'click.wav'  # "sound_by_accuracy" overrides this

        # Direction validator (see documentation of MovementAngleValidator)
        self.dir_validator_min_angle = -90
        self.dir_validator_max_angle = 90
        self.dir_validator_calc_angle_interval = 20

        # Global speed validator
        self.global_speed_validator_milestones = [(.5, .33), (.5, .67)]  # see GlobalSpeedValidator.milestones

        # Zigzag validator
        self.zigzag_validator_min_angle_change_per_curve = 10  # see NCurvesValidator.min_angle_change_per_curve

        # Number line (see documentation of NumberLine)
        self.nl_line_width = 2
        self.nl_end_tick_height = 5
        self.nl_line_colour = xpy.misc.constants.C_WHITE
        self.nl_labels_font_name = "Arial"
        self.nl_labels_box_size = (100, 30)
        self.nl_labels_offset = (0, 20)
        self.nl_labels_colour = xpy.misc.constants.C_GREY
        self.nl_distance_from_top = 80  # Distance of the numberline's main line from top-of-screen

        # Start point
        self.start_point_x_coord = 0
