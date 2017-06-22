"""
Base class for experiment configuration

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import expyriment as xpy
import trajtracker as ttrk


#-- This event is dispatched when the finger leaves the "start" area and starts moving towards
#-- the number line
FINGER_STARTED_MOVING = ttrk.events.Event("FINGER_STARTED_MOVING")


class BaseConfig(object):

    def __init__(self, experiment_id, data_source, max_trial_duration,
                 use_text_targets, use_generic_targets,
                 fixation_type, fixation_text,
                 fixzoom_box_size, fixzoom_dot_radius, fixzoom_dot_colour,
                 fixzoom_zoom_duration, fixzoom_stay_duration,
                 fixzoom_show_event, fixzoom_start_zoom_event,
                 text_target_height, shuffle_trials,
                 log_stimulus_onset_offset,
                 min_trial_duration, speed_guide_enabled, min_inst_speed,
                 grace_period, max_zigzags, save_results, sounds_dir,
                 stimulus_then_move, finger_moves_min_time, finger_moves_max_time,
                 start_point_size, start_point_tilt,
                 start_point_colour):

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

        #: Whether to create a CSV log file indicating the times when each stimulus was presented/hidden
        self.log_stimulus_onset_offset = log_stimulus_onset_offset

        #----- Configuration of the fixation -----

        #: The type of fixation to use: 'cross', 'text', 'zoom', or None
        self.fixation_type = fixation_type

        #: Default text to use for a text fixation
        self.fixation_text = fixation_text

        self.fixzoom_box_size = fixzoom_box_size
        self.fixzoom_dot_radius = fixzoom_dot_radius
        self.fixzoom_dot_colour = fixzoom_dot_colour
        self.fixzoom_zoom_duration = fixzoom_zoom_duration
        self.fixzoom_stay_duration = fixzoom_stay_duration
        self.fixzoom_show_event = fixzoom_show_event
        self.fixzoom_start_zoom_event = fixzoom_start_zoom_event

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
        #todo: add these parameters to the documentation

        # Text target
        self.text_target_font = "Arial"
        self.text_target_width = 300         # Width of the text box
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

        # Start point
        self.start_point_x_coord = 0


    #---------------------------------------------------
    @property
    def is_fixation_zoom(self):
        return self.fixation_type == 'zoom'
