"""
Functions to support the number-to-position paradigm

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
from numbers import Number
from operator import itemgetter
import numpy as np

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils
import trajtracker.utils as u

from trajtrackerp import common
from trajtrackerp.common import get_parser_for

from trajtrackerp.num2pos import DownArrow


#----------------------------------------------------------------
def create_experiment_objects(exp_info):
    """
    Create the full default configuration for the experiment.

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    load_data_source(exp_info)

    create_numberline(exp_info)
    common.create_common_experiment_objects(exp_info)
    create_experiment_attrs(exp_info)

    create_sounds(exp_info)


#----------------------------------------------------------------
def create_experiment_attrs(exp_info):
    """
    Set some experiment-level attributes

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    exp_info.exp_data['MinTarget'] = config.min_numberline_value
    exp_info.exp_data['MaxTarget'] = config.max_numberline_value
    exp_info.exp_data['ShowFeedback'] = 1 if config.show_feedback else 0
    if config.max_response_excess is not None:
        exp_info.exp_data['MaxResponseExcess'] = config.max_response_excess


#----------------------------------------------------------------
def create_numberline(exp_info):
    """
    Create a :class:`~trajtracker.stimuli.NumberLine` object with default configuration

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    common.validate_config_param_type("min_numberline_value", Number, config.min_numberline_value)
    common.validate_config_param_type("max_numberline_value", Number, config.max_numberline_value)
    common.validate_config_param_type("max_response_excess", Number, config.max_response_excess, True)
    common.validate_config_param_type("nl_distance_from_top", int, config.nl_distance_from_top)
    common.validate_config_param_type("nl_end_tick_height", int, config.nl_end_tick_height, True)
    common.validate_config_param_type("nl_labels_box_size", ttrk.TYPE_SIZE, config.nl_labels_box_size)
    common.validate_config_param_type("nl_labels_colour", ttrk.TYPE_RGB, config.nl_labels_colour)
    common.validate_config_param_type("nl_labels_font_name", str, config.nl_labels_font_name)
    common.validate_config_param_type("nl_labels_offset", ttrk.TYPE_COORD, config.nl_labels_offset)
    common.validate_config_param_type("nl_labels_visible", bool, config.nl_labels_visible)
    common.validate_config_param_type("nl_length", Number, config.max_numberline_value)
    common.validate_config_param_type("nl_line_colour", ttrk.TYPE_RGB, config.nl_line_colour)
    common.validate_config_param_type("nl_line_width", int, config.nl_line_width)
    common.validate_config_param_type("post_response_target", bool, config.post_response_target)
    common.validate_config_param_type("show_feedback", bool, config.show_feedback)

    nl_length = common.xy_to_pixels(config.nl_length, exp_info.screen_size[0])
    if nl_length is None:
        raise ttrk.ValueError("Invalid config.nl_length value ({:})".format(config.nl_length))

    distance_from_top = common.xy_to_pixels(config.nl_distance_from_top, exp_info.screen_size[1])
    if distance_from_top is None:
        raise ttrk.ValueError("Invalid config.nl_distance_from_top value ({:})".format(config.nl_distance_from_top))

    numberline = ttrk.stimuli.NumberLine(
        position=(0, int(exp_info.screen_size[1] / 2) - distance_from_top),
        line_length=nl_length,
        line_width=config.nl_line_width,
        min_value=config.min_numberline_value,
        max_value=config.max_numberline_value)

    # -- Graphical properties of the number line
    numberline.end_tick_height = config.nl_end_tick_height
    numberline.line_colour = config.nl_line_colour

    # -- The labels at the end of the line
    numberline.labels_visible = config.nl_labels_visible
    numberline.labels_font_name = config.nl_labels_font_name
    numberline.labels_box_size = config.nl_labels_box_size
    hsr = u.get_font_height_to_size_ratio(numberline.labels_font_name)
    numberline.labels_font_size = int(numberline.labels_box_size[1] / hsr)
    numberline.labels_font_colour = config.nl_labels_colour
    numberline.labels_offset = config.nl_labels_offset

    exp_info.numberline = numberline

    #-- Save for results
    exp_info.exp_data['NLLength'] = config.nl_length
    exp_info.exp_data['NLDistanceFromTop'] = distance_from_top

    #-- Feedback arrow/line

    if config.show_feedback:

        ttrk.log_write("The finger landing position will be presented after each trial")

        if len(config.feedback_arrow_colors) == 0:
            raise ValueError("Invalid configuration: feedback_arrow_colors is an empty list")

        multicolor = len(config.feedback_arrow_colors) > 1

        colors = config.feedback_arrow_colors
        colors = colors if trajtracker.utils.is_collection(colors) else [colors]
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
def load_data_source(exp_info):
    """
    Loads the CSV file with the per-trial configuration
    """

    ds = exp_info.config.data_source

    if isinstance(ds, str):
        #-- Load from file
        loader = common.create_csv_loader()

        loader.add_field('target', lambda s: int(s) if s.isdigit() else float(s))

        loader.add_field('nl.position', ttrk.io.csv_formats.parse_coord, optional=True)
        loader.add_field('nl.position.x', int, optional=True)
        loader.add_field('nl.position.x%', float, optional=True)
        loader.add_field('nl.position.y', int, optional=True)

        exp_info.trials, fieldnames = loader.load_file(ds)
        exp_info.exported_trial_csv_columns = [f for f in fieldnames if f not in ('target')]
        return

    _u.validate_func_arg_is_collection(None, "load_data_source", "config.data_source", ds,
                                       min_length=1, allow_set=True)

    if sum([not isinstance(x, Number) for x in ds]) == 0:
        #-- A list of numbers was provided: simulate it as a CSV
        exp_info.trials = [{"target": x, ttrk.io.CSVLoader.FLD_LINE_NUM: 0} for x in ds]

    elif sum([not isinstance(x, dict) for x in ds]) == 0:
        #-- An explicit list of trials was provided
        for row in ds:
            if "target" not in row or not isinstance(row["target"], Number):
                raise trajtracker.ValueError("The data source must contain a 'target' field")
            if ttrk.io.CSVLoader.FLD_LINE_NUM not in row:
                row[ttrk.io.CSVLoader.FLD_LINE_NUM] = 0
        exp_info.trials = ds

    else:
        raise ttrk.TypeError("invalid config.data_source")
