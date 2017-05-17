"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import time
from numbers import Number
from operator import itemgetter
import numpy as np

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u

from trajtracker.paradigms.num2pos import DownArrow, FINGER_STARTED_MOVING


#----------------------------------------------------------------
def create_experiment_objects(exp_info):
    """
    Create the full default configuration for the experiment.

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    create_numberline(exp_info)

    create_start_point(exp_info)
    create_textbox_target(exp_info)
    create_generic_target(exp_info)
    create_fixation(exp_info)
    create_errmsg_textbox(exp_info)
    create_traj_tracker(exp_info)
    create_validators(exp_info, direction_validator=True, global_speed_validator=True, inst_speed_validator=True,
                      zigzag_validator=True)
    create_sounds(exp_info)

    exp_info.trials = load_data_source(config)

    #-- Initialize experiment-level data

    exp_info.exp_data['WindowWidth'] = exp_info.screen_size[0]
    exp_info.exp_data['WindowHeight'] = exp_info.screen_size[1]
    exp_info.exp_data['nExpectedTrials'] = len(exp_info.trials)
    exp_info.exp_data['nTrialsCompleted'] = 0
    exp_info.exp_data['nTrialsFailed'] = 0
    exp_info.exp_data['nTrialsSucceeded'] = 0


#----------------------------------------------------------------
def create_numberline(exp_info):
    """
    Create a :class:`~trajtracker.stimuli.NumberLine` object with default configuration

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    _u.validate_func_arg_type(None, "create_numberline", "max_value", config.max_numberline_value, Number)

    if isinstance(config.nl_length, int) and config.nl_length > 1:
        nl_length = config.nl_length
    elif isinstance(config.nl_length, Number) and 0 < config.nl_length <= 1:
        nl_length = int(exp_info.screen_size[0] * config.nl_length)
    else:
        raise ttrk.ValueError("Invalid value for config.nl_length: {:}".format(config.nl_length))

    numberline = ttrk.stimuli.NumberLine(
        position=(0, int(exp_info.screen_size[1] / 2 - config.nl_distance_from_top)),
        line_length=nl_length,
        line_width=config.nl_line_width,
        min_value=config.min_numberline_value,
        max_value=config.max_numberline_value)

    # -- Graphical properties of the number line
    numberline.end_tick_height = config.nl_end_tick_height
    numberline.line_colour = config.nl_line_colour

    # -- The labels at the end of the line
    numberline.labels_visible = True
    numberline.labels_font_name = config.nl_labels_font_name
    numberline.labels_box_size = config.nl_labels_box_size
    hsr = u.get_font_height_to_size_ratio(numberline.labels_font_name)
    numberline.labels_font_size = int(numberline.labels_box_size[1] / hsr)
    numberline.labels_font_colour = config.nl_labels_colour
    numberline.labels_offset = config.nl_labels_offset

    exp_info.numberline = numberline

    #-- Feedback arrow/line

    if config.show_feedback:

        ttrk.log_write("The finger landing position will be presented after each trial")

        if len(config.feedback_arrow_colors) == 0:
            raise ValueError("Invalid configuration: feedback_arrow_colors is an empty list")

        multicolor = len(config.feedback_arrow_colors) > 1

        colors = config.feedback_arrow_colors
        colors = colors if _u.is_collection(colors) else [colors]
        numberline.feedback_stimuli = [DownArrow(c) for c in colors]
        [s.preload() for s in numberline.feedback_stimuli]

        numberline.feedback_stim_offset = (0, int(numberline.feedback_stimuli[0].size[1] / 2))
        numberline.feedback_stim_hide_event = ttrk.events.TRIAL_STARTED

        i = 0
        for stim in numberline.feedback_stimuli:
            exp_info.stimuli.add(stim, "feedback" if multicolor else "feedback(accuracy level %d)" % i, False)
            i += 1

        if config.feedback_accuracy_levels is not None:
            numberline.feedback_stim_chooser = config.feedback_accuracy_levels

    #-- For directly showing the target

    exp_info.target_pointer = xpy.stimuli.Rectangle(size=(3, 30),
                                                    colour=xpy.misc.constants.C_WHITE)
    exp_info.target_pointer.preload()
    exp_info.target_pointer_height = exp_info.target_pointer.size[1]


#----------------------------------------------------------------
def create_start_point(exp_info):
    """
    Create the "start" area, with default configuration

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    start_area_size = config.start_point_size
    start_area_position = (config.start_point_x_coord,
                           - (exp_info.screen_size[1] / 2 - start_area_size[1] / 2))

    exp_info.start_point = ttrk.movement.RectStartPoint(size=start_area_size,
                                                        position=start_area_position,
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
    
    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    if not exp_info.config.save_results:
        return

    curr_time = time.strftime("%Y%m%d_%H%M", time.localtime())
    exp_info.trials_out_filename = "trials_{:}_{:}.csv".format(exp_info.subject_id, curr_time)
    exp_info.traj_out_filename = "trajectory_{:}_{:}.csv".format(exp_info.subject_id, curr_time)
    exp_info.session_out_filename = "session_{:}_{:}.xml".format(exp_info.subject_id, curr_time)

    traj_file_path = xpy.io.defaults.datafile_directory + "/" + exp_info.traj_out_filename
    exp_info.trajtracker = ttrk.movement.TrajectoryTracker(traj_file_path)
    exp_info.trajtracker.enable_event = FINGER_STARTED_MOVING
    exp_info.trajtracker.disable_event = ttrk.events.TRIAL_ENDED


#----------------------------------------------------------------
def create_validators(exp_info, direction_validator, global_speed_validator, inst_speed_validator, zigzag_validator):
    """
    Create movement validators, with default configuration.

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo

    :param direction_validator: Whether to include the validator that enforces upward-only movement
    :type direction_validator: bool

    :param global_speed_validator: Whether to validate that the finger reaches each y coordinate in time
    :type global_speed_validator: bool

    :param inst_speed_validator: Whether to validate the finger's instantaneous speed
    :type inst_speed_validator: bool

    :param zigzag_validator: Whether to prohibit zigzag movement
    :type zigzag_validator: bool

    :return: tuple: (list_of_validators, dict_of_validators)
    """

    _u.validate_func_arg_type(None, "create_validators", "direction_validator", direction_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "global_speed_validator", global_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "inst_speed_validator", inst_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "zigzag_validator", zigzag_validator, bool)

    config = exp_info.config

    if direction_validator:
        v = ttrk.validators.MovementAngleValidator(
            min_angle=config.dir_validator_min_angle,
            max_angle=config.dir_validator_max_angle,
            calc_angle_interval=config.dir_validator_calc_angle_interval)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'direction')


    if global_speed_validator:
        v = ttrk.validators.GlobalSpeedValidator(
            origin_coord=exp_info.start_point.position[1] + exp_info.start_point.start_area.size[1] / 2,
            end_coord=exp_info.numberline.position[1],
            grace_period=config.grace_period,
            max_trial_duration=config.max_trial_duration,
            milestones=config.global_speed_validator_milestones,
            show_guide=config.speed_guide_enabled)
        v.do_present_guide = False
        v.movement_started_event = FINGER_STARTED_MOVING
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'global_speed')
        exp_info.stimuli.add(v.guide.stimulus, "speed_guide", visible=False)


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
        v.direction_monitor.min_angle_change_per_curve = config.zigzag_validator_min_angle_change_per_curve
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'zigzag')


#----------------------------------------------------------------
def create_textbox_target(exp_info):
    """
    Create a textbox to serve as the target. This text box supports multiple texts (so it can be used
    for RSVP, priming, etc.)

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    target = _create_textbox_target_impl(exp_info, "target")

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else ttrk.paradigms.num2pos.FINGER_STARTED_MOVING
    target.onset_time = config.target_onset_time
    target.duration = config.target_duration
    target.last_stimulus_remains = config.text_target_last_stimulus_remains

    exp_info.text_target = target
    exp_info.add_event_sensitive_object(target)


#----------------------------------------------------------------
def create_textbox_fixation(exp_info):
    """
    Create a textbox to serve as the fixation. 

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    y, height = get_target_y(exp_info)

    text = exp_info.config.fixation_text

    fixation = xpy.stimuli.TextBox(
        text='' if text is None else text,
        size=(config.text_target_width, int(height)),
        position=(config.text_target_x_coord, y),
        text_font=config.text_target_font,
        text_colour=config.text_target_colour,
        text_justification=config.text_target_justification
    )

    hsr = u.get_font_height_to_size_ratio(fixation.text_font)
    font_size = int(height / hsr * config.text_target_height)
    fixation.text_size = font_size
    ttrk.log_write("Fixation font size = {:}, height = {:.1f} pixels".format(font_size, font_size*hsr), print_to_console=True)

    exp_info.fixation = fixation


#----------------------------------------------------------------
def _create_textbox_target_impl(exp_info, role):

    config = exp_info.config

    target = ttrk.stimuli.MultiTextBox()

    y, height = get_target_y(exp_info)
    target.position = (config.text_target_x_coord, y)
    target.text_font = config.text_target_font
    target.size = (config.text_target_width, int(height))
    target.text_colour = config.text_target_colour
    target.text_justification = config.text_target_justification

    if not (0 < config.text_target_height <= 1):
        raise ttrk.ValueError("Invalid config.text_target_height ({:}): value must be between 0 and 1, check out the documentation".format(config.text_target_height))

    hsr = u.get_font_height_to_size_ratio(target.text_font)
    font_size = int(height / hsr * config.text_target_height)
    target.text_size = font_size
    ttrk.log_write("{:} font size = {:}, height = {:.1f} pixels".format(role, font_size, font_size*hsr), print_to_console=True)

    return target


#----------------------------------------------------------------
def create_generic_target(exp_info):
    """
    Create a handler for non-text targets (pictures, shapes, etc.). This object supports multiple targets
    (so it can be used for RSVP, priming, etc.)

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    y, height = get_target_y(exp_info)
    target = ttrk.stimuli.MultiStimulus(position=(config.generic_target_x_coord, y))

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else ttrk.paradigms.num2pos.FINGER_STARTED_MOVING
    target.onset_time = config.target_onset_time
    target.duration = config.target_duration
    target.last_stimulus_remains = config.generic_target_last_stimulus_remains

    exp_info.generic_target = target
    exp_info.add_event_sensitive_object(target)


#----------------------------------------------------------------
def create_fixation(exp_info):
    """
    Create the fixation shape

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    fixtype = exp_info.config.fixation_type.lower()

    if fixtype is None:
        pass

    if fixtype == 'cross':
        create_fixation_cross(exp_info)

    elif fixtype == 'text':
        create_textbox_fixation(exp_info)

    else:
        raise ttrk.ValueError("Invalid config.fixation_type ({:})".format(fixtype))


#----------------------------------------------------------------
def create_fixation_cross(exp_info):
    y, height = get_target_y(exp_info)
    exp_info.fixation = ttrk.paradigms.general.FixationCross(radius=15)
    exp_info.fixation.position = (0, y)


#----------------------------------------------------------------
def get_target_y(exp_info):
    """
    Create the y coordinate where the target should be presented 

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    screen_top = exp_info.screen_size[1] / 2
    height = screen_top - exp_info.numberline.position[1] - exp_info.config.stimulus_distance_from_top - 1
    y = int(screen_top - exp_info.config.stimulus_distance_from_top - height / 2)
    return y, height


#----------------------------------------------------------------
def create_errmsg_textbox(exp_info):
    """
    Create a stimulus that can show the error messages

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    exp_info.errmsg_textbox = xpy.stimuli.TextBox(
        text="",
        size=config.errmsg_textbox_size,
        position=config.errmsg_textbox_coords,
        text_font=config.errmsg_textbox_font_name,
        text_size=config.errmsg_textbox_font_size,
        text_colour=config.errmsg_textbox_font_colour)


#----------------------------------------------------------------
def register_to_event_manager(exp_info):
    """
    Register all event-sensitive objects to the event manager

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    for obj in exp_info.event_sensitive_objects:
        exp_info.event_manager.register(obj)


#------------------------------------------------
def create_sounds(exp_info):
    """
    Load the sounds for the experiment
    
    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    exp_info.sound_err = load_sound(config, config.sound_err)

    if config.sound_by_accuracy is None:
        # One sound, independently of accuracy
        exp_info.sounds_ok = [load_sound(config, config.sound_ok)]
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

    exp_info.sounds_ok = [load_sound(config, x[1]) for x in cfg]
    exp_info.sounds_ok_max_ep_err = np.array([x[0] for x in cfg])


#------------------------------------------------
def load_sound(config, filename):
    sound = xpy.stimuli.Audio(config.sounds_dir + "/" + filename)
    sound.preload()
    return sound


#----------------------------------------------------------------
def load_data_source(config):
    """
    Loads the CSV file with the per-trial configuration
    
    :param config: the program's configuration
    :type config: :doc:`Config <Config>`
    """

    ds = config.data_source

    if isinstance(ds, str):
        #-- Load from file
        loader = ttrk.io.CSVLoader()
        loader.add_field('target', lambda s: int(s) if s.isdigit() else float(s))
        loader.add_field('use_text_targets', bool, optional=True)
        loader.add_field('use_generic_targets', bool, optional=True)
        loader.add_field('finger_moves_min_time', float, optional=True)
        loader.add_field('finger_moves_max_time', float, optional=True)

        loader.add_field('text.text_size', getparser(int), optional=True)
        loader.add_field('text.bold', getparser(bool), optional=True)
        loader.add_field('text.italic', getparser(bool), optional=True)
        loader.add_field('text.underline', getparser(bool), optional=True)
        loader.add_field('text.justification', getparser(ttrk.io.csv_formats.parse_text_justification), optional=True)
        loader.add_field('text.text_colour', getparser(ttrk.io.csv_formats.parse_rgb), optional=True)
        loader.add_field('text.background_colour', getparser(ttrk.io.csv_formats.parse_rgb), optional=True)
        loader.add_field('text.size', getparser(ttrk.io.csv_formats.parse_size), optional=True)
        loader.add_field('text.position', getparser(ttrk.io.csv_formats.parse_coord), optional=True)
        loader.add_field('text.position.x', getparser(int), optional=True)
        loader.add_field('text.position.y', getparser(int), optional=True)
        loader.add_field('text.onset_time', getparser(float), optional=True)
        loader.add_field('text.duration', getparser(float), optional=True)

        loader.add_field('genstim.position', getparser(ttrk.io.csv_formats.parse_coord), optional=True)
        loader.add_field('genstim.position.x', getparser(int), optional=True)
        loader.add_field('genstim.position.y', getparser(int), optional=True)
        loader.add_field('genstim.onset_time', getparser(float), optional=True)
        loader.add_field('genstim.duration', getparser(float), optional=True)

        loader.add_field('fixation.position', getparser(ttrk.io.csv_formats.parse_coord), optional=True)
        loader.add_field('fixation.position.x', getparser(int), optional=True)
        loader.add_field('fixation.position.y', getparser(int), optional=True)

        loader.add_field('nl.position', getparser(ttrk.io.csv_formats.parse_coord), optional=True)
        loader.add_field('nl.position.x', getparser(int), optional=True)
        loader.add_field('nl.position.y', getparser(int), optional=True)

        return loader.load_file(ds)

    _u.validate_func_arg_is_collection(None, "load_data_source", "config.data_source", ds,
                                       min_length=1, allow_set=True)

    if sum([not isinstance(x, Number) for x in ds]) == 0:
        #-- A list of numbers was provided: simulate it as a CSV
        return [{"target": str(x), ttrk.io.CSVLoader.FLD_LINE_NUM: 0} for x in ds]

    if sum([not isinstance(x, dict) for x in ds]) == 0:
        #-- An explicit list of trials was provided
        for row in ds:
            if "target" not in row or not isinstance(row["target"], str):
                raise trajtracker.ValueError("The data source must contain a 'target' field")
            if ttrk.io.CSVLoader.FLD_LINE_NUM not in row:
                row[ttrk.io.CSVLoader.FLD_LINE_NUM] = 0
        return ds

    raise TypeError("trajtracker error: invalid config.data_source")


#-----------------------------------------------------------------------------------------
def getparser(type_cast_function, delimiter=";", always_create_list=False):
    """
    Given a type name (or an str->type parsing function), return a function that can parse
    both this type and delimited lists of this type
    """
    def parse(str_value):
        if delimiter in str_value:
            return [type_cast_function(s) for s in str_value.split(delimiter)]
        else:
            value = type_cast_function(str_value)
            if always_create_list:
                value = [value]
            return value

    return parse
