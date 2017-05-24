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

from trajtracker.paradigms import common


from trajtracker.paradigms.num2pos import DownArrow


#----------------------------------------------------------------
def create_experiment_objects(exp_info):
    """
    Create the full default configuration for the experiment.

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    create_numberline(exp_info)

    common.create_start_point(exp_info)
    common.create_textbox_target(exp_info)
    common.create_generic_target(exp_info)
    common.create_fixation(exp_info)
    common.create_errmsg_textbox(exp_info)
    common.create_traj_tracker(exp_info)
    common.create_validators(exp_info, direction_validator=True, global_speed_validator=True,
                             inst_speed_validator=True, zigzag_validator=True)
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

    numberline.preload()



#------------------------------------------------
def create_sounds(exp_info):
    """
    Load the sounds for the experiment
    
    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    exp_info.sound_err = common.load_sound(config, config.sound_err)

    if config.sound_by_accuracy is None:
        # One sound, independently of accuracy
        exp_info.sounds_ok = [common.load_sound(config, config.sound_ok)]
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

    exp_info.sounds_ok = [common.load_sound(config, x[1]) for x in cfg]
    exp_info.sounds_ok_max_ep_err = np.array([x[0] for x in cfg])


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

        loader.add_field('fixation.position', ttrk.io.csv_formats.parse_coord, optional=True)
        loader.add_field('fixation.position.x', int, optional=True)
        loader.add_field('fixation.position.x%', float, optional=True)
        loader.add_field('fixation.position.y', int, optional=True)

        loader.add_field('nl.position', ttrk.io.csv_formats.parse_coord, optional=True)
        loader.add_field('nl.position.x', int, optional=True)
        loader.add_field('nl.position.x%', float, optional=True)
        loader.add_field('nl.position.y', int, optional=True)

        return loader.load_file(ds)

    _u.validate_func_arg_is_collection(None, "load_data_source", "config.data_source", ds,
                                       min_length=1, allow_set=True)

    if sum([not isinstance(x, Number) for x in ds]) == 0:
        #-- A list of numbers was provided: simulate it as a CSV
        return [{"target": x, ttrk.io.CSVLoader.FLD_LINE_NUM: 0} for x in ds]

    if sum([not isinstance(x, dict) for x in ds]) == 0:
        #-- An explicit list of trials was provided
        for row in ds:
            if "target" not in row or not isinstance(row["target"], Number):
                raise trajtracker.ValueError("The data source must contain a 'target' field")
            if ttrk.io.CSVLoader.FLD_LINE_NUM not in row:
                row[ttrk.io.CSVLoader.FLD_LINE_NUM] = 0
        return ds

    raise ttrk.TypeError("invalid config.data_source")


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
