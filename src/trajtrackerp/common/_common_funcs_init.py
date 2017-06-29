"""
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

import time
import numbers
import os
import numpy as np

import expyriment as xpy
from expyriment.misc import geometry

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtrackerp.common import FINGER_STARTED_MOVING, FINGER_STOPPED_MOVING


#---------------------------------------------------------------------
def get_subject_name_id():
    """
    Get the name (optional) and the initials of the subject
    """

    name_input = xpy.io.TextInput("Subject name - optional:", length=40,
                                  message_colour=xpy.misc.constants.C_WHITE)
    subj_name = name_input.get()

    if subj_name == "":
        default_id = ""
    else:
        name_elems = subj_name.lower().split(" ")
        default_id = "".join([e[0] for e in name_elems if len(e) > 0])

    id_input = xpy.io.TextInput("Subject ID (initials) - mandatory:", length=10,
                                message_colour=xpy.misc.constants.C_WHITE)
    while True:
        subj_id = id_input.get(default_id)
        if subj_id != "":
            break


    return subj_id, subj_name


#----------------------------------------------------------------
def create_common_experiment_objects(exp_info):
    """
    Create configuration for the experiment - object common to several trajtrackerp.
    
    exp_info.trials must be set before calling this function.

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    if exp_info.trials is None:
        raise ttrk.InvalidStateError('Please update exp_info.trials before calling create_common_experiment_objects()')

    create_start_point(exp_info)
    create_textbox_target(exp_info)
    create_generic_target(exp_info)
    create_fixation(exp_info)
    create_errmsg_textbox(exp_info)
    create_traj_tracker(exp_info)
    create_validators(exp_info, direction_validator=True, global_speed_validator=True,
                      inst_speed_validator=True, zigzag_validator=True)
    create_confidence_slider(exp_info)

    #-- Initialize experiment-level data
    exp_info.exp_data['WindowWidth'] = exp_info.screen_size[0]
    exp_info.exp_data['WindowHeight'] = exp_info.screen_size[1]
    exp_info.exp_data['nExpectedTrials'] = len(exp_info.trials)
    exp_info.exp_data['nTrialsCompleted'] = 0
    exp_info.exp_data['nTrialsFailed'] = 0
    exp_info.exp_data['nTrialsSucceeded'] = 0


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
    if not exp_info.config.finger_must_start_upwards:
        exp_info.start_point.exit_area = None

    exp_info.stimuli.add(exp_info.start_point.start_area, "start_point")

    exp_info.exp_data['TrajZeroCoordX'] = start_area_position[0]
    exp_info.exp_data['TrajZeroCoordY'] = start_area_position[1] + start_area_size[1]/2
    exp_info.exp_data['TrajPixelsPerUnit'] = 1


# ----------------------------------------------------------------
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
    exp_info.trajtracker.disable_event = FINGER_STOPPED_MOVING


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
        v.disable_event = FINGER_STOPPED_MOVING
        exp_info.add_validator(v, 'direction')


    if global_speed_validator:
        v = ttrk.validators.GlobalSpeedValidator(
            origin_coord=exp_info.start_point.position[1] + exp_info.start_point.start_area.size[1] / 2,
            end_coord=exp_info.speed_validation_end_y_coord(),
            grace_period=config.grace_period,
            max_trial_duration=config.max_trial_duration,
            milestones=config.global_speed_validator_milestones,
            show_guide=config.speed_guide_enabled)
        v.do_present_guide = False
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = FINGER_STOPPED_MOVING
        exp_info.add_validator(v, 'global_speed')
        exp_info.stimuli.add(v.guide.stimulus, "speed_guide", visible=False)


    if inst_speed_validator:
        v = ttrk.validators.InstantaneousSpeedValidator(
            min_speed=config.min_inst_speed,
            grace_period=config.grace_period,
            calculation_interval=0.05)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = FINGER_STOPPED_MOVING
        exp_info.add_validator(v, 'inst_speed')


    if zigzag_validator:
        v = ttrk.validators.NCurvesValidator(max_curves_per_trial=config.max_zigzags)
        v.direction_monitor.min_angle_change_per_curve = config.zigzag_validator_min_angle_change_per_curve
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = FINGER_STOPPED_MOVING
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

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else FINGER_STARTED_MOVING
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

    y, height = exp_info.get_default_target_y()

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

    fixation.preload()

    exp_info.fixation = fixation


#----------------------------------------------------------------
def create_fixation_zoom(exp_info):
    """
    Create a :class:`~trajtracker.stimuli.FixationZoom` fixation 

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    y, height = exp_info.get_default_target_y()

    if config.fixzoom_start_zoom_event is None:
        start_zoom_event = ttrk.events.TRIAL_STARTED + 0.2
    elif config.fixzoom_start_zoom_event == ttrk.events.TRIAL_STARTED or config.fixzoom_start_zoom_event == ttrk.events.TRIAL_INITIALIZED:
        raise ttrk.ValueError(('config.fixzoom_start_zoom_event was set to an invalid value ({:}): ' +
                              'it can only be set to times AFTER the trial has already started (e.g., ttrk.events.TRIAL_STARTED + 0.1)').
                              format(config.fixzoom_start_zoom_event))
    else:
        start_zoom_event = config.fixzoom_start_zoom_event

    fixation = ttrk.stimuli.FixationZoom(
        position=(config.text_target_x_coord, y),
        box_size=config.fixzoom_box_size,
        dot_radius=config.fixzoom_dot_radius,
        dot_colour=config.fixzoom_dot_colour,
        zoom_duration=config.fixzoom_zoom_duration,
        stay_duration=config.fixzoom_stay_duration,
        show_event=config.fixzoom_show_event,
        start_zoom_event=start_zoom_event)

    exp_info.fixation = fixation
    exp_info.add_event_sensitive_object(exp_info.fixation)


#----------------------------------------------------------------
def _create_textbox_target_impl(exp_info, role):

    config = exp_info.config

    target = ttrk.stimuli.MultiTextBox()

    y, height = exp_info.get_default_target_y()
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

    y, height = exp_info.get_default_target_y()
    target = ttrk.stimuli.MultiStimulus(position=(config.generic_target_x_coord, y))

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else FINGER_STARTED_MOVING
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

    elif fixtype == 'zoom':
        create_fixation_zoom(exp_info)

    else:
        raise ttrk.ValueError("Invalid config.fixation_type ({:})".format(fixtype))


#----------------------------------------------------------------
def create_fixation_cross(exp_info):
    y, height = exp_info.get_default_target_y()
    exp_info.fixation = xpy.stimuli.FixCross(size=(30, 30), position=(0, y), line_width=2)
    exp_info.fixation.preload()


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
def load_sound(config, filename):
    """
    Load a sound file
    
    :param config: The experiment configuration object 
    :param filename: No path needed. The file is expected to be under config.sounds_dir 
    """
    full_path = config.sounds_dir + "/" + filename
    if not os.path.isfile(full_path):
        raise ttrk.ValueError('Sound file {:} does not exist. Please check the file name (or perhaps you need to change config.sounds_dir)'.
                              format(full_path))
    sound = xpy.stimuli.Audio(full_path)
    sound.preload()
    return sound


#-----------------------------------------------------------------------------------------
def create_csv_loader():
    """
    Create a :class:`~trajtracker.io.CSVLoader` for loading the data from the CSV file; 
    initialize the loader with definitions of the columns common to all trajtrackerp. 
    """

    loader = ttrk.io.CSVLoader()
    loader.add_field('use_text_targets', bool, optional=True)
    loader.add_field('use_generic_targets', bool, optional=True)
    loader.add_field('finger_moves_min_time', float, optional=True)
    loader.add_field('finger_moves_max_time', float, optional=True)

    loader.add_field('text.text_size', get_parser_for(int), optional=True)
    loader.add_field('text.bold', get_parser_for(bool), optional=True)
    loader.add_field('text.italic', get_parser_for(bool), optional=True)
    loader.add_field('text.underline', get_parser_for(bool), optional=True)
    loader.add_field('text.justification', get_parser_for(ttrk.io.csv_formats.parse_text_justification), optional=True)
    loader.add_field('text.text_colour', get_parser_for(ttrk.io.csv_formats.parse_rgb), optional=True)
    loader.add_field('text.background_colour', get_parser_for(ttrk.io.csv_formats.parse_rgb), optional=True)
    loader.add_field('text.size', get_parser_for(ttrk.io.csv_formats.parse_size), optional=True)
    loader.add_field('text.position', get_parser_for(ttrk.io.csv_formats.parse_coord), optional=True)
    loader.add_field('text.position.x', get_parser_for(int), optional=True)
    loader.add_field('text.position.y', get_parser_for(int), optional=True)
    loader.add_field('text.onset_time', get_parser_for(float), optional=True)
    loader.add_field('text.duration', get_parser_for(float), optional=True)

    loader.add_field('genstim.position', get_parser_for(ttrk.io.csv_formats.parse_coord), optional=True)
    loader.add_field('genstim.position.x', get_parser_for(int), optional=True)
    loader.add_field('genstim.position.y', get_parser_for(int), optional=True)
    loader.add_field('genstim.onset_time', get_parser_for(float), optional=True)
    loader.add_field('genstim.duration', get_parser_for(float), optional=True)

    loader.add_field('fixation.position', ttrk.io.csv_formats.parse_coord, optional=True)
    loader.add_field('fixation.position.x', int, optional=True)
    loader.add_field('fixation.position.x%', float, optional=True)
    loader.add_field('fixation.position.y', int, optional=True)

    return loader


#-----------------------------------------------------------------------------------------
def get_parser_for(type_cast_function, delimiter=";", always_create_list=False):
    """
    Given a type name (or an str->type parsing function), return a function that can parse
    both this type and delimited lists of this type.
    
    This is used for parsing CSV files
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


#-----------------------------------------------------------------------------------------
def validate_config_param_type(param_name, param_type, param_value, none_allowed=False, type_name=None):
    """
    Validate that a certain configuration parameter is of the specified type
    """

    if none_allowed and param_value is None:
        return

    if isinstance(param_type, (type, tuple)):
        if not isinstance(param_value, param_type):
            if type_name is None:
                type_name = _u.get_type_name(param_type)

            raise ttrk.TypeError("config.{:} was set to a non-{:} value ({:})".format(param_name, type_name, param_value))

    elif param_type == ttrk.TYPE_RGB:
        if not u.is_rgb(param_value):
            raise ttrk.TypeError("config.{:} was set to an invalid value ({:}) - expecting (red,green,blue)".
                                 format(param_name, param_value))

    elif param_type == ttrk.TYPE_COORD:
        if not u.is_coord(param_value, allow_float=True):
            raise ttrk.TypeError("config.{:} was set to an invalid value ({:}) - expecting (x, y)".
                                 format(param_name, param_value))
        if isinstance(param_value, geometry.XYPoint):
            param_value = param_value.x, param_value.y

    elif param_type == ttrk.TYPE_SIZE:
        if not u.is_collection(param_value) or \
                        len(param_value) != 2 or \
                not isinstance(param_value[0], numbers.Number) or \
                not isinstance(param_value[1], numbers.Number):
            raise ttrk.TypeError("config.{:} was set to an invalid value '{:}' - expecting size, i.e., (width, height) with two integers".
                                 format(param_name, param_value))

    elif param_type == ttrk.TYPE_CALLABLE:
        if "__call__" not in dir(value):
            raise ttrk.TypeError(
                "config.{:} was set to a non-callable value ({:})".format(param_name, param_value))

    else:
        raise Exception("trajtracker internal error: unsupported type '{:}'".format(param_type))

    return param_value


#-----------------------------------------------------------------------------------------
def validate_config_param_values(param_name, param_value, allowed_values):
    """
    Validate that a certain configuration parameter is one of the listed values
    """

    if param_value not in allowed_values:
        allowed_values_str = ", ".join([str(v) for v in allowed_values])
        raise ttrk.TypeError("config.{:} was set to an invalid value ({:}). Allowed values are: {:}".
                             format(param_name, param_value, allowed_values_str))


#-----------------------------------------------------------------------------------------
# noinspection PyIncorrectDocstring
def xy_to_pixels(value, screen_size, parameter_name=None):
    """
    Translate a stimulus size or position to pixels.
    
    The input is either one value (x or y) or a pair of values (x, y).
    It may denote either a stimulus size or a position.
    
    If x/y is an int value (or a pair of ints), it is left unchanged.
    If it is a float value, it is interpreted as percentage of the screen size. In this case,  
    the value should be between 0.0 and 1.0 for size, or between -0.5 and 0.5 for position (but the function will
    accept any value between -0.5 and 1.0)
    
    :param value: The value to convert - either a number or a pair of numbers  
    :param screen_size: The screen size - either a number or a pair of numbers (must match the "value" paremeter)
    :param parameter_name: If this is not None, errors will yield an exception, indicating this parameter
    :return: An int or a pair of ints (scale = pixels). If the input value is not a valid size, return None.
    """

    if isinstance(value, numbers.Number):

        #-- A single value

        if isinstance(value, int):
            return value

        elif -0.5 <= value <= 1:
            _u.validate_func_arg_type(None, "common.xy_to_pixels", "screen_size", screen_size, int)
            return int(np.round(value * screen_size))

        else:
            return None

    if u.is_collection(value) and len(value) == 2 and \
            isinstance(value[0], numbers.Number) and isinstance(value[1], numbers.Number):

        #-- Pair of values
        _u.validate_func_arg_is_collection(None, "common.xy_to_pixels", "screen_size", screen_size, 2, 2)

        retval = xy_to_pixels(value[0], screen_size[0]), xy_to_pixels(value[1], screen_size[1])
        if retval[0] is None or retval[1] is None:
            return None
        else:
            return retval

    else:
        #-- Not a valid xy
        return None


#-----------------------------------------------------------------------------------------
def create_confidence_slider(exp_info):
    """
    Create a :class:`~trajtracker.stimuli.Slider` for measuring subjective confidence rating
    
    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """
    config = exp_info.config

    y = config.confidence_slider_y
    validate_config_param_type("confidence_slider_y", numbers.Number, y)
    y = xy_to_pixels(y, exp_info.screen_size[1])
    if y is None:
        raise ttrk.ValueError('Invalid config.confidence_slider_y ({:}): '.format(config.confidence_slider_y) +
                              'expecting either an integer or ratio of screen height (between -0.5 and 0.5)')

    validate_config_param_type("confidence_rating", bool, config.confidence_rating)
    if not exp_info.config.confidence_rating:
        return

    #-- Create the confidence slider
    slider_bgnd = _create_confidence_slider_background(exp_info)
    gauge = _create_slider_gauge(slider_bgnd.surface_size[0])
    slider = ttrk.stimuli.Slider(slider_bgnd, gauge, orientation=ttrk.stimuli.Orientation.Vertical,
                                 min_value=0, max_value=100, position=(0, y))

    exp_info.stimuli.add(slider.stimulus, "confidence_slider", visible=False)
    exp_info.confidence_slider = slider


#-----------------------------------------------------------------------------------------
# Create the slider's background (red-to-green scale)
#
def _create_confidence_slider_background(exp_info):

    filename = exp_info.config.confidence_slider_picture
    height = exp_info.config.confidence_slider_height

    validate_config_param_type("confidence_slider_height", numbers.Number, height)
    validate_config_param_type("confidence_slider_picture", str, filename)

    #-- Find slider height in pixels
    height = xy_to_pixels(height, exp_info.screen_size[1])
    if height is None:
        raise ttrk.ValueError("Invalid config.confidence_slider_height ({:})".format(exp_info.config.confidence_slider_height))

    #-- Load picture
    file_path = ttrk.trajtrackerp.images_dir + os.path.sep + filename
    slider_pic = xpy.stimuli.Picture(file_path)

    #-- Resize picture
    # noinspection PyTypeChecker
    slider_pic.scale(height / slider_pic.surface_size[1])

    slider_pic.preload()

    return slider_pic


#-----------------------------------------------------------------------------------------
# Create the slider's moving part (the gauge)
#
def _create_slider_gauge(width):

    width1 = int(width*0.8)
    width2 = int(width*1.2)
    rect1 = xpy.stimuli.Rectangle(size=(width1, 7), position=(0, 0), colour=xpy.misc.constants.C_WHITE)
    rect2 = xpy.stimuli.Rectangle(size=(width2, 3), position=(0, 0), colour=xpy.misc.constants.C_WHITE)

    canvas = xpy.stimuli.Canvas(size=(width2, 7), position=(0, 0))
    rect1.plot(canvas)
    rect2.plot(canvas)

    return canvas
