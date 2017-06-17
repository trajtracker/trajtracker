"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
import time
import numbers
import numpy as np

import expyriment as xpy
from expyriment.misc import geometry

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils
import trajtracker.utils as u

from trajtracker.paradigms import common
from trajtracker.paradigms.common import get_parser_for


#----------------------------------------------------------------
def create_experiment_objects(exp_info):
    """
    Create the full default configuration for the experiment.

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo
    """

    load_data_source(exp_info)

    common.create_common_experiment_objects(exp_info)

    create_response_buttons(exp_info)
    create_feedback_areas(exp_info)
    create_sounds(exp_info)


#=======================================================================================
#                 Response buttons
#=======================================================================================

#----------------------------------------------------------------
def create_response_buttons(exp_info):
    """
    Create the two response buttons

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo
    """

    #-- Create buttons

    size = _get_response_buttons_size(exp_info)
    positions = _get_response_buttons_positions(exp_info, size)
    colors = _get_response_buttons_colors(exp_info)
    texts = _get_response_buttons_texts(exp_info)

    if texts is None:

        #-- No text: create rectangles
        for i in range(2):
            button = xpy.stimuli.Rectangle(size=size, position=positions[i], colour=colors[i])
            exp_info.response_buttons.append(button)
            exp_info.stimuli.add(button, visible=True, stimulus_id="resp_btn_%d" % i)

    else:

        common.validate_config_param_type("resp_btn_font_name", str, config.resp_btn_font_name)
        common.validate_config_param_type("resp_btn_font_size", str, config.resp_btn_font_size)
        common.validate_config_param_type("resp_btn_text_colour", ttrk.TYPE_RGB, config.resp_btn_text_colour)

        #-- Create buttons with text
        for i in range(2):
            button = xpy.stimuli.TextBox(text=texts[i],
                                         size=size,
                                         position=positions[i],
                                         text_font=config.resp_btn_font_name,
                                         text_size=config.resp_btn_font_size,
                                         text_colour=config.resp_btn_text_colour,
                                         background_colour=colors[i])
            exp_info.response_buttons.append(button)
            exp_info.stimuli.add(button, visible=True, stimulus_id="resp_btn_%d" % i)

    #-- create hotspots for detecting responses
    for i in range(2):
        area = ttrk.misc.nvshapes.Rectangle(size=size, position=positions[i])
        hotspot = ttrk.movement.Hotspot(area=area)
        hotspot.button_number = i
        exp_info.response_hotspots.append(hotspot)


#----------------------------------------------------------------
def _get_response_buttons_size(exp_info):

    width, height = common.validate_config_param_type("resp_btn_size", ttrk.TYPE_SIZE, exp_info.config.resp_btn_size)

    #-- If width/height are between [-1,1], they mean percentage of screen size
    if -1 < width < 1:
        width = int(width * exp_info.screen_size[0])
    elif not isinstance(width, int):
        raise ttrk.ValueError("Invalid config.resp_btn_size: a non-integer width was provided ({:})".format(width))
    if -1 < height < 1:
        height = int(height * exp_info.screen_size[1])
    elif not isinstance(height, int):
        raise ttrk.ValueError("Invalid config.resp_btn_size: a non-integer height was provided ({:})".format(height))

    return width, height


#----------------------------------------------------------------
def _get_response_buttons_positions(exp_info, button_size):

    config = exp_info.config

    position = config.resp_btn_positions

    if position is None:
        #-- Set default position: top-left and top-right of screen
        max_x = int(exp_info.screen_size[0] / 2)
        max_y = int(exp_info.screen_size[1] / 2)
        x = max_x - int(button_size[0] / 2)
        y = max_y - int(button_size[1] / 2)

        return (-x, -y), (x, -y)

    if u.is_coord(position, allow_float=True):
        #-- One pair of coords given: this is for the left side
        pos_left = -position[0], position[1]
        position = pos_left, position

    elif not trajtracker.utils.is_collection(position) or len(position) != 2 or \
            not u.is_coord(position[0], allow_float=True) or not u.is_coord(position[1], allow_float=True):
        raise ttrk.ValueError("config.resp_btn_positions should be either (x,y) coordinates " +
                              "or a pair of coordinates [(xleft, yleft), (xright, yright)]. " +
                              "The value provided is invalid: {:}".format(position))

    #-- If x/y are between [-1,1], they mean percentage of screen size
    result = []
    screen_width, screen_height = exp_info.screen_size
    for x, y in position:
        if -1 < x < 1:
            x = int(x * screen_width)
        elif not isinstance(x, int):
            raise ttrk.ValueError("Invalid config.resp_btn_positions: a non-integer x was provided ({:})".format(x))
        if -1 < y < 1:
            y = int(y * screen_height)
        elif not isinstance(y, int):
            raise ttrk.ValueError("Invalid config.resp_btn_positions: a non-integer y was provided ({:})".format(y))
        result.append((x, y))

    return result


#----------------------------------------------------------------
def _get_response_buttons_colors(exp_info):

    color = exp_info.config.resp_btn_colours

    if u.is_rgb(color):
        #-- One color given
        return color, color

    if not trajtracker.utils.is_collection(color) or len(color) != 2 or \
            not u.is_rgb(color[0]) or not u.is_rgb(color[1]):
        raise ttrk.ValueError("config.resp_btn_colours should be either a color (R,G,B) " +
                              "or a pair of colors (left_rgb, right_rgb). " +
                              "The value provided is invalid: {:}".format(color))

    return color


#----------------------------------------------------------------
def _get_response_buttons_texts(exp_info):

    text = exp_info.config.resp_btn_texts

    if text is None or (trajtracker.utils.is_collection(text) and len(text) == 0):
        return None

    if isinstance(text, str):
        #-- One text given
        return text, text

    if not trajtracker.utils.is_collection(text) or len(text) != 2 or \
            not isinstance(text[0], str) or not isinstance(text[1], str):
        raise ttrk.ValueError("config.resp_btn_texts should be either a string or a pair of strings. " +
                              "The value provided is invalid: {:}".format(text))

    return text


#=======================================================================================
#                 Feedback
#=======================================================================================


#----------------------------------------------------------------
def create_feedback_areas(exp_info):
    pass


#=======================================================================================
#                 Sounds
#=======================================================================================


#----------------------------------------------------------------
def create_sounds(exp_info):
    """
    Load sounds for this experiment
    
    :param exp_info: 
    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo
    """

    config = exp_info.config

    exp_info.sound_err = common.load_sound(config, config.sound_err)
    exp_info.sounds_ok = [common.load_sound(config, config.sound_ok)]


#=======================================================================================
#                 Data source
#=======================================================================================


#----------------------------------------------------------------
def load_data_source(exp_info):
    """
    Loads the CSV file with the per-trial configuration

    :param exp_info: 
    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo
    """

    ds_filename = exp_info.config.data_source
    common.validate_config_param_type("data_source", str, ds_filename)

    loader = common.create_csv_loader()

    loader.add_field('expected_response', int, optional=True)

    loader.add_field('left_resp_btn.text', str, optional=True)
    loader.add_field('right_resp_btn.text', str, optional=True)

    exp_info.trials = loader.load_file(ds_filename)

