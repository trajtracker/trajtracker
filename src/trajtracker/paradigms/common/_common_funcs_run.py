"""
Functions common to several paradigms

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


import numpy as np
import csv
import numbers
import random
import time
from enum import Enum
# noinspection PyPep8Naming
import xml.etree.cElementTree as ET

import expyriment as xpy

import trajtracker as ttrk

import trajtracker.utils as u
from trajtracker.validators import ExperimentError
from trajtracker.movement import StartPoint

# noinspection PyProtectedMember
from trajtracker.paradigms.common._BaseConfig import FINGER_STARTED_MOVING

RunTrialResult = Enum('RunTrialResult', 'Succeeded Failed Aborted')


#----------------------------------------------------------------
def init_experiment(exp_info):

    exp_info.session_start_localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    if exp_info.config.shuffle_trials:
        random.shuffle(exp_info.trials)

    exp_info.trajtracker.init_output_file()

    exp_info.session_start_time = u.get_time()


#----------------------------------------------------------------
def on_finger_touched_screen(exp_info, trial):
    """
    This function should be called when the finger touches the screen

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    """

    exp_info.errmsg_textbox.visible = False

    show_fixation(exp_info)

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_STARTED, 0,
                                          u.get_time() - exp_info.session_start_time)

    exp_info.stimuli.present()

    trial.start_time = u.get_time()

    #-- Reset all trajectory-sensitive objects
    for obj in exp_info.trajectory_sensitive_objects:
        obj.reset(0)


#----------------------------------------------------------------
def on_finger_started_moving(exp_info, trial):
    """
    This function should be called when the finger leaves the "start" area and starts moving

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    show_fixation(exp_info, False)
    t = u.get_time()
    time_in_trial = t - trial.start_time
    time_in_session = t - exp_info.session_start_time
    trial.results['time_started_moving'] = time_in_trial

    #-- This event is dispatched before calling present(), because it might trigger operations that
    #-- show/hide stuff
    exp_info.event_manager.dispatch_event(FINGER_STARTED_MOVING, time_in_trial, time_in_session)

    exp_info.stimuli.present()

    if not exp_info.config.stimulus_then_move:
        trial.results['targets_t0'] = u.get_time() - trial.start_time


#----------------------------------------------------------------
def wait_until_finger_moves(exp_info, trial):
    """
    The function returns after the finger started moving (or on error)

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 

    :return: None if all OK; if trial should terminate, a tuple with two values:
             (1) RunTrialResult.xxx (2) An ExperimentError object
    """

    # -- Wait for the participant to start moving the finger
    if exp_info.config.is_fixation_zoom:
        # noinspection PyUnusedLocal
        def on_loop_callback(time_in_trial, time_in_session):
            exp_info.fixation.update_xyt(time_in_session=time_in_session)
    else:
        on_loop_callback = None

    exp_info.start_point.wait_until_exit(exp_info.xpy_exp,
                                         on_loop_present=exp_info.stimuli,
                                         on_loop_callback=on_loop_callback,
                                         event_manager=exp_info.event_manager,
                                         trial_start_time=trial.start_time,
                                         session_start_time=exp_info.session_start_time,
                                         max_wait_time=trial.finger_moves_max_time)

    if exp_info.start_point.state == StartPoint.State.aborted:
        #-- Finger lifted
        show_fixation(exp_info, False)
        return RunTrialResult.Aborted, None

    elif exp_info.start_point.state == StartPoint.State.error:
        #-- Invalid start direction
        return RunTrialResult.Failed, ExperimentError("StartedSideways", "Start the trial by moving straight, not sideways!")

    elif exp_info.start_point.state == StartPoint.State.timeout:
        #-- Finger moved too late
        return RunTrialResult.Failed, ExperimentError("FingerMovedTooLate", "You moved too late")

    if trial.finger_moves_min_time is not None and u.get_time() - trial.start_time < trial.finger_moves_min_time:
        #-- Finger moved too early
        return RunTrialResult.Failed, ExperimentError("FingerMovedTooEarly", "You moved too early")

    on_finger_started_moving(exp_info, trial)

    return None


# ----------------------------------------------------------------
def show_fixation(exp_info, visible=True):

    if isinstance(exp_info.fixation, ttrk.stimuli.FixationZoom):
        exp_info.fixation.reset()

    if exp_info.fixation is not None:
        exp_info.fixation.visible = visible


# ----------------------------------------------------------------
def update_text_target_for_trial(exp_info, trial, use_numeric_target_as_default=False):
    """
    Update properties of the text stimuli according to the current trial info

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    if not trial.use_text_targets:
        # No text in this trial
        exp_info.text_target.texts = []
        return

    if "text.target" in trial.csv_data:
        # -- Set the text to show as target (or several, semicolon-separated texts, in case of RSVP)
        trial.text_target = trial.csv_data["text.target"]
    elif use_numeric_target_as_default:
        trial.text_target = str(trial.target)
    else:
        raise ttrk.BadFormatError("The input CSV file does not contain a 'text.target' column!")

    exp_info.text_target.texts = trial.text_target.split(";")

    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.font', 'text_font')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.text_size', 'text_size')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.bold', 'text_bold')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.italic', 'text_italic')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.underline', 'text_underline')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.justification',
                              'text_justification')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.text_colour', 'text_colour')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.background_colour',
                              'background_colour')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.size', 'size')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.position', 'position')
    _update_target_stimulus_position(exp_info, trial, exp_info.text_target, 'text', 'x')
    _update_target_stimulus_position(exp_info, trial, exp_info.text_target, 'text', 'y')

    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.onset_time', 'onset_time')
    update_attr_by_csv_config(exp_info, trial, exp_info.text_target, 'text.duration', 'duration')


# ----------------------------------------------------------------
def update_generic_target_for_trial(exp_info, trial):
    """
    Update properties of the generic stimuli according to the current trial info

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    if not trial.use_generic_targets:
        # No text in this trial
        exp_info.generic_target.shown_stimuli = []
        return

    trial.generic_target = trial.csv_data["genstim.target"]

    exp_info.generic_target.shown_stimuli = trial.csv_data['genstim.target'].split(";")

    update_attr_by_csv_config(exp_info, trial, exp_info.generic_target, 'genstim.position', 'position')

    _update_target_stimulus_position(exp_info, trial, exp_info.generic_target, 'genstim', 'x')
    _update_target_stimulus_position(exp_info, trial, exp_info.generic_target, 'genstim', 'y')


# ------------------------------------------------
def update_fixation_for_trial(exp_info, trial):
    """
    Update the fixation when the trial is initialized

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    """

    if exp_info.config.fixation_type == 'text':

        if 'fixation.text' in trial.csv_data:
            exp_info.fixation.text = trial.csv_data['fixation.text']

        if exp_info.fixation.text == '':
            ttrk.log_write("WARNING: No fixation text was set for trial #{:}".format(trial.trial_num))

    update_attr_by_csv_config(exp_info, trial, exp_info.fixation, 'fixation.position', 'position')

    update_obj_position(exp_info, trial, exp_info.fixation, 'fixation', 'x')
    update_obj_position(exp_info, trial, exp_info.fixation, 'fixation', 'y')


# ------------------------------------------------
def update_attr_by_csv_config(exp_info, trial, target_obj, csv_name, attr_name):
    """
    Update one attribute of an object from the corresponding entry in the config CSV file

    :param exp_info:
    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    
    :param trial:
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
     
    :param target_obj: The object containing the attribute to update
    
    :param csv_name: The column name in the CSV file
    :type csv_name: str
    
    :param attr_name: The name of the attribute to update
    :type attr_name: str
    """

    if csv_name not in trial.csv_data:
        return

    value = trial.csv_data[csv_name]
    if isinstance(target_obj, ttrk.stimuli.BaseMultiStim) and \
            isinstance(value, list) and \
            len(value) < target_obj.n_stim:
        raise Exception(
            "Invalid value for column '{:}' in the data file {:}: the column has {:} values, expecting {:}".format(
                attr_name, exp_info.config.data_source, len(value), target_obj.n_stim))

    setattr(target_obj, attr_name, value)


# ------------------------------------------------
def _update_target_stimulus_position(exp_info, trial, target_holder, col_name_prefix, x_or_y):
    """
    Update the stimulus position according to "position.x" or "position.y" columns

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    """

    if x_or_y not in ('x', 'y'):
        raise Exception("Invalid x_or_y argument ({:})".format(x_or_y))
    is_x = x_or_y == 'x'

    csv_col, coord_as_percentage = _get_x_or_y_col(trial, col_name_prefix, x_or_y)
    if csv_col is None:
        return

    n_stim = target_holder.n_stim

    # -- Get the x/y coordinates as an array
    coord = trial.csv_data[csv_col]
    if coord_as_percentage:
        coord = coord_to_pixels(coord, csv_col, exp_info.config.data_source, is_x)

    if not isinstance(coord, list):
        coord = [coord] * n_stim

    if len(coord) < n_stim:
        raise Exception(
            "Invalid value for column '{:}' in the data file {:}: the column has {:} values, expecting {:}".format(
                attr_name, exp_info.config.data_source, len(value), n_stim))

    pos = target_holder.position
    if not isinstance(pos, list):
        pos = [pos] * n_stim

    for i in range(min(len(pos), len(coord))):
        pos[i] = (coord[i], pos[i][1]) if is_x else (pos[i][0], coord[i])

    target_holder.position = pos


# ------------------------------------------------
def update_obj_position(exp_info, trial, visual_obj, col_name_prefix, x_or_y):
    """
    Update the position of a visual object according to "position.x" or "position.y" columns

    :param exp_info:
    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    
    :param trial:
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
     
    :param visual_obj: The object containing the attribute to update
    
    :param col_name_prefix: Prefix of the column name in the CSV file
    :type col_name_prefix: str
    
    :param x_or_y: 'x' or 'y', indicating which column to look for in the CSV file
    """

    if x_or_y not in ('x', 'y'):
        raise Exception("Invalid x_or_y argument ({:})".format(x_or_y))
    is_x = x_or_y == 'x'

    csv_col, coord_as_percentage = _get_x_or_y_col(trial, col_name_prefix, x_or_y)
    if csv_col is None:
        return

    coord = trial.csv_data[csv_col]
    if coord_as_percentage:
        coord = coord_to_pixels(coord, csv_col, exp_info.config.data_source, is_x)

    visual_obj.position = (coord, visual_obj.position[1]) if is_x else (visual_obj.position[0], coord)


# ------------------------------------------------
def _get_x_or_y_col(trial, col_name_prefix, x_or_y):
    """
    Get the CSV column name from which x/y coordinate should be taken

    :return: col_name(str), is_percentage(bool) 
    """

    csv_col = "{:}.position.{:}".format(col_name_prefix, x_or_y)
    if csv_col in trial.csv_data:
        return csv_col, False

    else:
        csv_col = "{:}.position.{:}%".format(col_name_prefix, x_or_y)
        if csv_col not in trial.csv_data:
            return None, None

        return csv_col, True


# ------------------------------------------------
def coord_to_pixels(coord, col_name, filename, is_x):
    """
    Convert screen coordinates, which were provided as percentage of the screen width/height,
    into pixels.

    :param coord: The coordinate, on a 0-1 scale; or a list of coordinates
    :param col_name: The column name in the CSV file (just for logging)
    :param filename: CSV file name (just for logging)
    :param is_x: (bool) whether it's an x or y coordinate
    :return: coordinate as pixels (int); or a list of coords
    """

    screen_size = ttrk.env.screen_size[0 if is_x else 1]

    coord_list = coord if isinstance(coord, list) else [coord]
    # noinspection PyTypeChecker
    if sum([not (-1.5 <= c <= 2.5) for c in coord_list]) > 0:
        # Some coordinates are way off the screen bounds
        raise ttrk.ValueError("Invalid {:} in the CSV file {:}: within-screen coordinates are in the range 0-1".
                              format(col_name, filename))

    if isinstance(coord, list):
        return [int(np.round((c - 0.5) * screen_size)) for c in coord]
    else:
        return int(np.round((coord - 0.5) * screen_size))


# ------------------------------------------------
def update_movement_in_traj_sensitive_objects(exp_info, trial):
    """
    Update the trajectory-sensitive objects about the mouse/finger movement

    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    :return: None if all is OK; or an ExperimentError object if one of the validators issued an error
    """

    curr_time = u.get_time()
    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time

    for obj in exp_info.trajectory_sensitive_objects:
        err = obj.update_xyt(ttrk.env.mouse.position, time_in_trial, time_in_session)
        if err is not None:
            return err

    exp_info.event_manager.on_frame(time_in_trial, time_in_session)

    return None


#------------------------------------------------
def save_session_file(exp_info, paradigm):
    """
    Save the session.xml file 
    """

    root = ET.Element("data")

    #-- Software version
    source_node = ET.SubElement(root, "source")
    ET.SubElement(source_node, "software", name="TrajTracker", version=ttrk.version())
    ET.SubElement(source_node, "paradigm", name=paradigm)
    ET.SubElement(source_node, "experiment", name=exp_info.config.experiment_id)

    #-- Subject info
    subj_node = ET.SubElement(root, "subject", id=exp_info.subject_id, expyriment_id=str(exp_info.xpy_exp.subject))
    ET.SubElement(subj_node, "name").text = exp_info.subject_name

    #-- Session data
    session_node = ET.SubElement(root, "session", start_time=exp_info.session_start_localtime)

    results_node = ET.SubElement(session_node, "exp_level_results")

    for key, value in exp_info.exp_data.items():
        value_type = "number" if isinstance(value, numbers.Number) else "string"
        if isinstance(value, float):
            value = "{:.6f}".format(value)
        ET.SubElement(results_node, "data", name=key, value=str(value), type=value_type)

    files_node = ET.SubElement(session_node, "files")
    ET.SubElement(files_node, "file", type="trials", name=exp_info.trials_out_filename)
    ET.SubElement(files_node, "file", type="trajectory", name=exp_info.traj_out_filename)

    indent_xml(root)
    tree = ET.ElementTree(root)
    tree.write(xpy.io.defaults.datafile_directory + "/" + exp_info.session_out_filename, encoding="UTF-8")


#------------------------------------------------------------
def indent_xml(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


#------------------------------------------------
def open_trials_file(exp_info, additional_fields):
    """
    :param exp_info:
    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
     
    :param additional_fields: List of field names in the CSV file (on top of the common fields)
    """

    all_fields = _get_trials_csv_out_common_fields() + additional_fields

    filename = xpy.io.defaults.datafile_directory + "/" + exp_info.trials_out_filename

    exp_info.trials_out_fp = open(filename, 'w')
    exp_info.trials_file_writer = csv.DictWriter(exp_info.trials_out_fp, all_fields)
    exp_info.trials_file_writer.writeheader()


#----------------------------------------------------------------
def trial_failed_common(err, exp_info, trial):
    """
    Called when the trial failed for any reason 
    (only when a strict error occurred; pointing at an incorrect location does not count as failure) 

    :type err: ExperimentError
    :type exp_info: trajtracker.paradigms.common.BaseExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    ttrk.log_write("ERROR in trial ({:}). Message shown to subject: {:}".format(err.err_code, err.message))

    curr_time = u.get_time()

    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_FAILED, time_in_trial, time_in_session)

    exp_info.errmsg_textbox.unload()
    exp_info.errmsg_textbox.text = err.message
    exp_info.errmsg_textbox.visible = True

    exp_info.sound_err.play()


#----------------------------------------------------------------
def prepare_trial_out_row(exp_info, trial, time_in_trial, success_err_code):
    """
    Get values to save in the trials.csv output file 
    
    :return: A dict with some values for the file 
    """

    if time_in_trial == 0 or 'time_started_moving' not in trial.results:
        movement_time = 0
    else:
        movement_time = time_in_trial - trial.results['time_started_moving']

    if trial.use_text_targets and trial.use_generic_targets:
        presented_target = 'text="{:}";generic="{:}"'.format(trial.text_target, trial.generic_target)
    elif trial.use_text_targets:
        presented_target = trial.text_target
    elif trial.use_generic_targets:
        presented_target = trial.generic_target
    else:
        presented_target = ""

    t_move = trial.results['time_started_moving'] if 'time_started_moving' in trial.results else -1
    t_target = trial.results['targets_t0'] if 'targets_t0' in trial.results else -1

    #todo: add custom fields? confidence?
    return {
        'trialNum': trial.trial_num,
        'LineNum': trial.file_line_num,
        'presentedTarget': presented_target,
        'status': success_err_code,
        'movementTime': "{:.3g}".format(movement_time),
        'timeInSession': "{:.3g}".format(trial.start_time - exp_info.session_start_time),
        'timeUntilFingerMoved': "{:.3g}".format(t_move),
        'timeUntilTarget': "{:.3g}".format(t_target),
    }

#----------------------------------------------------------------
def _get_trials_csv_out_common_fields():
    return ['trialNum', 'LineNum', 'presentedTarget', 'status', 'movementTime',
            'timeInSession', 'timeUntilFingerMoved', 'timeUntilTarget']
