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
import numbers
import numpy as np

import expyriment as xpy
from expyriment.misc import geometry

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils
import trajtracker.utils as u

from trajtrackerp import common
from trajtrackerp.common import get_parser_for
from trajtrackerp.dchoice import ExperimentInfo


#----------------------------------------------------------------
def initialize_experiment(config, xpy_exp, subj_id, subj_name=""):
    """
    A default implementation for running a complete experiment, end-to-end: loading the data,
    initializing all objects, running all trials, and saving the results.

    :param config:
    :type config: trajtrackerp.dchoice.Config 

    :param xpy_exp: Expyriment's `active experiment <http://docs.expyriment.org/expyriment.design.Experiment.html>`_
                    object
    :param subj_id: The subject initials from the num2pos app welcome screen
    :param subj_name: The subject name from the num2pos app welcome screen (or an empty string) 
    """

    exp_info = ExperimentInfo(config, xpy_exp, subj_id, subj_name)

    create_experiment_objects(exp_info)

    common.register_to_event_manager(exp_info)

    return exp_info


#----------------------------------------------------------------
def create_experiment_objects(exp_info):
    """
    Create the full default configuration for the experiment.

    :param exp_info: 
    :type exp_info: trajtrackerp.dchoice.ExperimentInfo
    """

    load_data_source(exp_info)

    common.create_common_experiment_objects(exp_info)

    create_response_buttons(exp_info)
    create_feedback_stimuli(exp_info)
    create_sounds(exp_info)


#=======================================================================================
#                 Response buttons
#=======================================================================================

#----------------------------------------------------------------
def create_response_buttons(exp_info):
    """
    Create the two response buttons

    :param exp_info: 
    :type exp_info: trajtrackerp.dchoice.ExperimentInfo
    """

    #-- Create buttons

    size = exp_info.get_response_buttons_size()
    positions = _get_response_buttons_positions(exp_info, size)
    colors = _get_response_buttons_colors(exp_info)
    texts = _get_response_buttons_texts(exp_info)

    exp_info.response_button_size = size
    exp_info.response_button_positions = positions

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
        exp_info.trajectory_sensitive_objects.append(hotspot)


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

        return (-x, y), (x, y)

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
def create_feedback_stimuli(exp_info):
    """
    Create the stimuli to be used as feedback for the participant's response
    :param exp_info:
    :type exp_info: trajtrackerp.dchoice.ExperimentInfo
    """

    common.validate_config_param_values("feedback_stim_type", exp_info.config.feedback_stim_type,
                                        ['rectangle', 'picture', None])
    common.validate_config_param_values("feedback_select_by", exp_info.config.feedback_select_by,
                                        ['response', 'expected', 'accuracy'])
    common.validate_config_param_type("feedback_duration", numbers.Number, exp_info.config.feedback_duration)

    if exp_info.config.feedback_select_by in ('accuracy', 'expected') and \
                    len(exp_info.trials) > 0 and 'expected_response' not in exp_info.trials[0]:
        raise ttrk.BadFormatError('Invalid format for {:}: when config.feedback_select_by=accuracy, you must include an expected_response column in the file'.
                                  format(exp_info.config.data_source))

    fb_type = exp_info.config.feedback_stim_type
    if fb_type == 'picture':
        _create_feedback_pictures(exp_info)

    elif fb_type == 'rectangle':
        _create_feedback_rectangles(exp_info)

    positions = _get_feedback_stim_positions(exp_info)

    for i in range(len(exp_info.feedback_stimuli)):

        feedback_stim = exp_info.feedback_stimuli[i]
        feedback_stim.position = positions[i]
        feedback_stim.visible = False

        #-- Hide feedback stimuli after delay
        exp_info.event_manager.register_operation(ttrk.events.TRIAL_SUCCEEDED + exp_info.config.feedback_duration,
                                                  lambda t1, t2: hide_feedback_stimuli(exp_info),
                                                  recurring=True,
                                                  cancel_pending_operation_on=ttrk.events.TRIAL_STARTED,
                                                  description="Hide feedback stimulus")

    # exp_info.event_manager.log_level = ttrk.log_debug


#----------------------------------------------------------------
def hide_feedback_stimuli(exp_info):
    for stim in exp_info.feedback_stimuli:
        stim.visible = False


#----------------------------------------------------------------
# Create two feedback stimuli - two pictures
#
def _create_feedback_pictures(exp_info):

    pics = exp_info.config.feedback_pictures

    if not u.is_collection(pics) or len(pics) != 2 or not isinstance(pics[0], xpy.stimuli.Picture) \
            or not isinstance(pics[1], xpy.stimuli.Picture):
        raise ttrk.TypeError("Invalid config.feedback_pictures: expecting two pictures")

    for i in range(2):
        exp_info.feedback_stimuli.append(pics[i])


#----------------------------------------------------------------
def _create_feedback_rectangles(exp_info):

    sizes = _get_feedback_rect_sizes(exp_info)
    colors = _get_feedback_rect_colors(exp_info)

    for i in range(2):
        fb_stim = xpy.stimuli.Rectangle(size=sizes[i], colour=colors[i])
        exp_info.feedback_stimuli.append(fb_stim)
        exp_info.stimuli.add(fb_stim, "feedback%d" % i)


#----------------------------------------------------------------
# Return two sizes - one for each of the feedback areas
#
def _get_feedback_rect_sizes(exp_info):

    size_param = exp_info.config.feedback_rect_size

    #-- If size was explicitly provided: use it
    if size_param is not None and not isinstance(size_param, numbers.Number):

        single_size = common.xy_to_pixels(size_param, exp_info.screen_size)
        if single_size is None:
            #-- The "feedback_rect_size" argument is NOT a pair of numbers.
            #-- So we expect it to be an array with two sets of coordinates.

            common.validate_config_param_type("feedback_rect_size", (list, tuple, np.ndarray),
                                              size_param, type_name="array/list/tuple")
            result = [common.xy_to_pixels(s, exp_info.screen_size) for s in size_param]
            if len(size_param) != 2 or result[0] is None or result[1] is None:
                raise ttrk.ValueError('Invalid config.feedback_rect_size: expecting either a size or a pair of sizes')

            return result

        else:
            #-- The "feedback_rect_size" argument is a pair of numbers - already translated
            #-- to pixels
            return single_size, single_size

    #-- feedback_rect_size was not specified explicitly: set it to default values

    if exp_info.config.feedback_place == 'button':

        #-- The feedback area overlaps with the buttons
        return exp_info.response_button_size, exp_info.response_button_size

    elif exp_info.config.feedback_place == 'middle':

        #-- The feedback area is between the buttons

        width = exp_info.screen_size[0] - 2 * exp_info.response_button_size[0]
        if isinstance(size_param, int):
            height = size_param
        elif isinstance(size_param, numbers.Number):
            height = int(np.round(size_param * exp_info.screen_size[1]))
        else:
            height = int(np.round(exp_info.response_button_size[1] / 4))

        return (width, height), (width, height)

    else:
        raise ttrk.ValueError("Unsupported feedback_place({:})".format(exp_info.config.feedback_place))


#----------------------------------------------------------------
# Return (x,y) coordinates for each of the feedback areas - i.e., ((x1,y1), (x2,y2))
#
def _get_feedback_stim_positions(exp_info, sizes=None):

    if sizes is None:
        sizes = [s.size for s in exp_info.feedback_stimuli]
    pos_param = exp_info.config.feedback_stim_position

    #-- If position was explicitly provided: use it
    if pos_param is not None:

        common.validate_config_param_type("feedback_stim_position", (list, tuple, np.ndarray),
                                          pos_param, type_name="array/list/tuple")
        if u.is_coord(pos_param):
            #-- One position given: use for both feedback areas
            pos_param = tuple(pos_param)
            return pos_param, pos_param

        elif len(pos_param) == 2 and u.is_coord(pos_param[0]) and u.is_coord(pos_param[1]):
            return tuple(pos_param)

        else:
            raise ttrk.ValueError("Invalid config.feedback_stim_position: expecting (x,y) or [(x1,y1), (x2,y2)]")

    #-- Position was not explicitly provided: use default position

    scr_width, scr_height = exp_info.screen_size

    if exp_info.config.feedback_place == 'button':

        #-- Position is top screen corners
        x1 = - (scr_width / 2 - sizes[0][0] / 2)
        y1 = scr_height / 2 - sizes[0][1] / 2
        x2 = (scr_width / 2 - sizes[1][0] / 2)
        y2 = scr_height / 2 - sizes[1][1] / 2

        return (x1, y1), (x2, y2)

    elif exp_info.config.feedback_place == 'middle':

        #-- Position is top-middle of screen
        y1 = scr_height / 2 - sizes[0][1] / 2
        y2 = scr_height / 2 - sizes[1][1] / 2
        return (0, y1), (0, y2)

    else:
        raise ttrk.ValueError("Unsupported config.feedback_place ({:})".format(config.feedback_place))


#----------------------------------------------------------------
def _get_feedback_rect_colors(exp_info):

    colors_param = exp_info.config.feedback_btn_colours

    if colors_param is None:
        if exp_info.config.feedback_place == 'button':
            return xpy.misc.constants.C_GREEN, xpy.misc.constants.C_GREEN
        
        elif exp_info.config.feedback_place == 'middle':
            return xpy.misc.constants.C_GREEN, xpy.misc.constants.C_RED
        
        else:
            raise ttrk.ValueError('Unsupported config.feedback_place ({:})'.format(exp_info.config.feedback_place))

    if u.is_rgb(colors_param):
        return colors_param, colors_param

    if u.is_collection(colors_param) and u.is_rgb(colors_param[0]) and u.is_rgb(colors_param[1]):
        return tuple(colors_param)

    else:
        raise ttrk.ValueError('Invalid config.feedback_btn_colours ({:}) - expecting a color (Red,Green,Blue) or an array.tuple with two colors'.format(colors_param))


#=======================================================================================
#                 Sounds
#=======================================================================================


#----------------------------------------------------------------
def create_sounds(exp_info):
    """
    Load sounds for this experiment
    
    :param exp_info: 
    :type exp_info: trajtrackerp.dchoice.ExperimentInfo
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
    :type exp_info: trajtrackerp.dchoice.ExperimentInfo
    """

    ds_filename = exp_info.config.data_source
    common.validate_config_param_type("data_source", str, ds_filename)

    loader = common.create_csv_loader()

    loader.add_field('expected_response', int, optional=True)

    loader.add_field('left_resp_btn.text', str, optional=True)
    loader.add_field('right_resp_btn.text', str, optional=True)

    exp_info.trials, fieldnames = loader.load_file(ds_filename)

    exp_info.exported_trial_csv_columns = [f for f in fieldnames if f not in ('expected_response')]
