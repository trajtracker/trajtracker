"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import time
from numbers import Number
from operator import itemgetter
import numpy as np

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u

from trajtracker.paradigms.num2pos import Arrow, FINGER_STARTED_MOVING, CsvConfigFields


#----------------------------------------------------------------
def create_experiment_objects(exp_info, config):
    """
    Create the full default configuration for the experiment.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    create_numberline(exp_info, config)
    exp_info.numberline.log_level = ttrk.log_debug

    create_start_point(exp_info, config)
    create_textbox_target(exp_info, config)
    create_errmsg_textbox(exp_info)
    create_traj_tracker(exp_info)
    create_validators(exp_info, direction_validator=True, global_speed_validator=True,
                      inst_speed_validator=True, zigzag_validator=True, config=config)
    create_sounds(exp_info, config)

    exp_info.trials = load_data_source(config)

    #-- Initialize experiment-level data

    exp_info.exp_data['WindowWidth'] = exp_info.screen_size[0]
    exp_info.exp_data['WindowHeight'] = exp_info.screen_size[1]
    exp_info.exp_data['nExpectedTrials'] = len(exp_info.trials)
    exp_info.exp_data['nExpectedGoodTrials'] = len(exp_info.trials)
    exp_info.exp_data['nTrialsCompleted'] = 0
    exp_info.exp_data['nTrialsFailed'] = 0
    exp_info.exp_data['nTrialsSucceeded'] = 0


#----------------------------------------------------------------
def create_numberline(exp_info, config):
    """
    Create a :class:`~trajtracker.stimuli.NumberLine` object with default configuration

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    _u.validate_func_arg_type(None, "create_numberline", "max_value", config.max_numberline_value, Number)

    numberline = ttrk.stimuli.NumberLine(
        position=(0, exp_info.screen_size[1] / 2 - 80),
        line_length=int(exp_info.screen_size[0] * 0.85),
        min_value=0,
        max_value=config.max_numberline_value)

    # -- Graphical properties of the number line
    numberline.position = (0, exp_info.screen_size[1] / 2 - 80)
    numberline.line_length = exp_info.screen_size[0] * 0.85
    numberline.line_width = 2
    numberline.end_tick_height = 5
    numberline.line_colour = xpy.misc.constants.C_WHITE

    # -- The labels at the end of the line
    numberline.labels_visible = True
    numberline.labels_font_name = "Arial"
    numberline.labels_font_size = 26
    numberline.labels_font_colour = xpy.misc.constants.C_GREY
    numberline.labels_box_size = (100, 30)
    numberline.labels_offset = (0, 20)

    exp_info.numberline = numberline

    #-- Feedback arrow/line

    if config.show_feedback:

        if len(config.feedback_arrow_colors) == 0:
            raise ValueError("Invalid configuration: feedback_arrow_colors is an empty list")

        multicolor = len(config.feedback_arrow_colors) > 1

        colors = config.feedback_arrow_colors
        colors = colors if _u.is_collection(colors) else [colors]
        numberline.feedback_stimuli = [Arrow(c) for c in colors]
        [s.preload() for s in numberline.feedback_stimuli]

        numberline.feedback_stim_offset = (0, numberline.feedback_stimuli[0].size[1] / 2)
        numberline.feedback_stim_hide_event = ttrk.events.TRIAL_STARTED

        i = 0
        for stim in numberline.feedback_stimuli:
            exp_info.stimuli.add(stim, "feedback" if multicolor else "feedback(accuracy level %d)" % i, False)
            i += 1

        if config.feedback_accuracy_levels is not None:
            numberline.feedback_stim_chooser = config.feedback_accuracy_levels

    #-- For directly showing the target

    target_pointer_length = 20
    exp_info.target_pointer = xpy.stimuli.Line(start_point=(0, 0), end_point=(0, target_pointer_length),
                                               line_width=2, colour=xpy.misc.constants.C_WHITE)
    exp_info.target_pointer.preload()
    exp_info.target_pointer_height = target_pointer_length

#----------------------------------------------------------------
def create_start_point(exp_info, config):
    """
    Create the "start" area, with default configuration

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    start_area_size = config.start_point_size
    start_area_position = (0, - (exp_info.screen_size[1] / 2 - start_area_size[1] / 2))

    exp_info.start_point = ttrk.movement.RectStartPoint(size=start_area_size, position=start_area_position,
                                                        rotation=config.start_point_tilt,
                                                        colour=config.start_point_colour)

    exp_info.stimuli.add(exp_info.start_point.start_area, "start_point")

    exp_info.exp_data['TrajZeroCoordX'] = start_area_position[0]
    exp_info.exp_data['TrajZeroCoordY'] = start_area_position[1] + start_area_size[1]/2
    exp_info.exp_data['TrajPixelsPerUnit'] = 1


#----------------------------------------------------------------
def create_traj_tracker(exp_info):
    """
    Create the object that tracks the trajectory
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    if not exp_info.config.save_results:
        return

    curr_time = time.strftime("%Y-%m-%d_%H-%M", time.localtime())
    exp_info.trials_out_filename = "trials_{:}_{:}.csv".format(exp_info.xpy_exp.subject, curr_time)
    exp_info.traj_out_filename = "trajectory_{:}_{:}.csv".format(exp_info.xpy_exp.subject, curr_time)

    traj_file_path = xpy.io.defaults.datafile_directory + "/" + exp_info.traj_out_filename
    exp_info.trajtracker = ttrk.movement.TrajectoryTracker(traj_file_path)
    exp_info.trajtracker.enable_event = FINGER_STARTED_MOVING
    exp_info.trajtracker.disable_event = ttrk.events.TRIAL_ENDED


#----------------------------------------------------------------
def create_validators(exp_info, direction_validator, global_speed_validator, inst_speed_validator, zigzag_validator,
                      config):
    """
    Create movement validators, with default configuration.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo

    :param direction_validator: Whether to include the validator that enforces upward-only movement
    :type direction_validator: bool

    :param global_speed_validator: Whether to validate that the finger reaches each y coordinate in time
    :type global_speed_validator: bool

    :param inst_speed_validator: Whether to validate the finger's instantaneous speed
    :type inst_speed_validator: bool

    :param zigzag_validator: Whether to prohibit zigzag movement
    :type zigzag_validator: bool

    :type config: trajtracker.paradigms.num2pos.Config

    :return: tuple: (list_of_validators, dict_of_validators)
    """

    _u.validate_func_arg_type(None, "create_validators", "direction_validator", direction_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "global_speed_validator", global_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "inst_speed_validator", inst_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "zigzag_validator", zigzag_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "config", config, ttrk.paradigms.num2pos.Config)


    if direction_validator:
        v = ttrk.validators.MovementAngleValidator(
            min_angle=-90,
            max_angle=90,
            calc_angle_interval=20)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'direction')


    if global_speed_validator:
        v = ttrk.validators.GlobalSpeedValidator(
            origin_coord=exp_info.start_point.position[1] + exp_info.start_point.start_area.size[1] / 2,
            end_coord=exp_info.numberline.position[1],
            grace_period=config.grace_period,
            max_trial_duration=config.max_trial_duration,
            milestones=[(.5, .33), (.5, .67)],
            show_guide=config.speed_guide_enabled)
        v.do_present_guide = False
        v.movement_started_event = FINGER_STARTED_MOVING
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'global_speed')


    if inst_speed_validator:
        v = ttrk.validators.InstantaneousSpeedValidator(
            min_speed=config.min_inst_speed,
            grace_period=config.grace_period,
            calculation_interval=0.05)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'inst_speed')


    if zigzag_validator:
        v = ttrk.validators.NCurvesValidator(max_curves_per_trial=config.max_zigzags)
        v.direction_monitor.min_angle_change_per_curve = 10  # Changes smaller than 10 degrees don't count as curves
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'zigzag')


#----------------------------------------------------------------
def create_textbox_target(exp_info, config):
    """
    Create a textbox to serve as the target. This text box supports multiple texts (so it can be used
    for RSVP, priming, etc.)

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    POSITION_FROM_TOP = 5

    screen_top = exp_info.screen_size[1] / 2
    height = screen_top - exp_info.numberline.position[1] - POSITION_FROM_TOP - 1
    y = int(screen_top - POSITION_FROM_TOP - height/2)

    target = ttrk.stimuli.MultiTextBox()

    target.position = (0, y)
    target.size = (600, height)
    target.text_size = 50
    target.text_colour = xpy.misc.constants.C_WHITE
    target.text_justification = 1  # center

    target.onset_event = TRIAL_STARTED if config.stimulus_then_move else ttrk.paradigms.num2pos.FINGER_STARTED_MOVING
    target.onset_time = [0]
    target.duration = [1000]  # never disappear

    exp_info.set_target(target, target.stimulus)
    exp_info.add_event_sensitive_object(target)


#----------------------------------------------------------------
def create_errmsg_textbox(exp_info):
    """
    Create a stimulus that can show the error messages

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    exp_info.errmsg_textbox = xpy.stimuli.TextBox(
        text="", size=(290, 180), position=(0, 0),
        text_font="Arial", text_size=16, text_colour=xpy.misc.constants.C_RED)


#----------------------------------------------------------------
def register_to_event_manager(exp_info):
    """
    Register all relevant objects to the event manager

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    for obj in exp_info.event_sensitive_objects:
        exp_info.event_manager.register(obj)


#------------------------------------------------
def create_sounds(exp_info, config):
    """
    Load the sounds for the experiment
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config
    """

    exp_info.sound_err = load_sound('error.wav')

    if config.sound_by_accuracy is None:
        # One sound, independently of accuracy
        exp_info.sounds_ok = [load_sound('click.wav')]
        exp_info.sounds_ok_max_ep_err = [1]
        return

    #-- Validate configuration
    _u.validate_attr_is_collection(config, "sound_by_accuracy", config.sound_by_accuracy, 1, allow_set=True)
    for sound_cfg in config.sound_by_accuracy:
        _u.validate_attr_is_collection(config, "sound_by_accuracy[*]", sound_cfg, 2, 2)
        _u.validate_attr_numeric(config, "sound_by_accuracy[*]", sound_cfg[0])
        if not (0 < sound_cfg[0] <= 1):
            raise trajtracker.ValueError("invalid accuracy level ({:}) in config.sound_by_accuracy".format(
                sound_cfg[0]))
        _u.validate_attr_type(config, "sound_by_accuracy[*]", sound_cfg[1], str)

    #-- Load sounds and save configuration

    cfg = [list(x) for x in config.sound_by_accuracy]
    cfg.sort(key=itemgetter(0))
    cfg[-1][0] = 1

    exp_info.sounds_ok = [load_sound(x[1]) for x in cfg]
    exp_info.sounds_ok_max_ep_err = np.array([x[0] for x in cfg])


#------------------------------------------------
def load_sound(filename):
    sound = xpy.stimuli.Audio("sounds/" + filename)
    sound.preload()
    return sound


#----------------------------------------------------------------
def load_data_source(config):

    ds = config.data_source

    if isinstance(ds, str):
        #-- Load from file
        loader = ttrk.data.CSVLoader()
        return loader.load_file(ds)

    _u.validate_func_arg_is_collection(None, "load_data_source", "config.data_source", ds,
                                       min_length=1, allow_set=True)

    if sum([not isinstance(x, Number) for x in ds]) == 0:
        #-- A list of numbers was provided: simulate it as a CSV
        return [{CsvConfigFields.Target: str(x), ttrk.data.CSVLoader.FLD_LINE_NUM: 0} for x in ds]

    if sum([not isinstance(x, dict) for x in ds]) == 0:
        #-- An explicit list of trials was provided
        for row in ds:
            if CsvConfigFields.Target not in row or not isinstance(row[CsvConfigFields.Target], str):
                raise trajtracker.ValueError("The data source must contain a '{:}' string value per trial".format(CsvConfigFields.Target))
            if ttrk.data.CSVLoader.FLD_LINE_NUM not in row:
                row[ttrk.data.CSVLoader.FLD_LINE_NUM] = 0
        return ds

    raise TypeError("trajtracker error: invalid config.data_source")
