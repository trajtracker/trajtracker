"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
import random
import csv
import numpy as np
from enum import Enum

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.utils import get_time
from trajtracker.validators import ExperimentError
from trajtracker.movement import StartPoint
from trajtracker.paradigms.num2pos import *


RunTrialResult = Enum('RunTrialResult', 'Succeeded Failed Aborted')



# todo: add min-trial-duration validation
# todo: handle stimulus-then-move, including FingerMovedTooEarly,FingerMovedTooLate errors
# todo: support image target (+RSVP), arrow target
# todo: escape button
# todo: optionally get subject name and initials
# todo: StartPoint should require LIFTING the finger before touching down (make this optional?)

# todo: delete XML support?
# todo: organize documentation. Have a "using this class" section for each complex class.
# todo: add logging to all trajtracker functions? Decide on logging policy (trace=enter/exit, detailed flow trace; debug=potentially interesting data, stages within functions; info=configuration, major operations, important data, validation errors)
# todo later: VOX detector

#----------------------------------------------------------------
def run_full_experiment(config):
    """
    A default implementation for running a complete experiment, end-to-end
    
    :type config: trajtracker.paradigms.num2pos.Config 
    """

    exp_info = initialize_exp(config)

    create_experiment_objects(exp_info, config)

    register_to_event_manager(exp_info)

    # todo: ask for subject initials and name?

    run_trials(exp_info, config)

    save_session_file(exp_info)

    xpy.control.end()


#----------------------------------------------------------------
def initialize_exp(config):
    """
    Initialize everything for the experiment
    
    :return: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    xpy_exp = xpy.control.initialize()
    expdata = ttrk.paradigms.num2pos.ExperimentInfo(xpy_exp, config)

    xpy.control.start(xpy_exp)
    if not xpy.misc.is_android_running():
        xpy_exp.mouse.show_cursor()

    return expdata


#----------------------------------------------------------------
def run_trials(exp_info, config):

    exp_info.trajtracker.init_output_file()

    exp_info.session_start_time = get_time()

    trial_num = 1

    while len(exp_info.trials) > 0:

        trial_config = exp_info.trials.pop(0)

        run_trial_rc = run_trial(exp_info, config, TrialInfo(trial_num, trial_config))
        if run_trial_rc == RunTrialResult.Aborted:
            print("   Trial aborted.")
            continue

        trial_num += 1

        exp_info.exp_data['nTrialsCompleted'] += 1

        if run_trial_rc == RunTrialResult.Succeeded:

            exp_info.exp_data['nTrialsSucceeded'] += 1

        elif run_trial_rc == RunTrialResult.Failed:

            exp_info.exp_data['nTrialsFailed'] += 1
            exp_info.trials.append(trial_config)
            if config.shuffle_trials:
                random.shuffle(exp_info.trials)

        else:
            raise Exception("Invalid result from run_trial(): {:}".format(run_trial_rc))


#----------------------------------------------------------------
def run_trial(exp_info, config, trial):
    """
    Run a single trial
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type config: trajtracker.paradigms.num2pos.Config 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo
     
    :return: True if the trial ended successfully, False if it failed
    """

    initialize_trial(exp_info, trial)

    exp_info.start_point.wait_until_startpoint_touched(exp_info.xpy_exp, on_loop_present=exp_info.stimuli)
    on_finger_touched_screen(exp_info, trial)

    rc = initiate_trial(exp_info, config, trial)
    if rc is not None:
        return rc

    while True:  # This loop runs once per frame

        if not exp_info.xpy_exp.mouse.check_button_pressed(0):
            trial_failed(ExperimentError("FingerLifted", "You lifted your finger in mid-trial"), exp_info, trial)
            return RunTrialResult.Failed

        #-- Inform relevant objects (validators, trajectory tracker, event manager, etc.) of the progress
        err = update_movement(exp_info, trial)
        if err is not None:
            trial_failed(err, exp_info, trial)
            return RunTrialResult.Failed

        #-- Check if the number line was reached
        if exp_info.numberline.touched:
            trial_succeeded(exp_info, trial)
            return RunTrialResult.Succeeded


#----------------------------------------------------------------
def initiate_trial(exp_info, config, trial):
    """
    Make the trial start - either by the subject, or by the software.
    The function returns after the finger started moving (or on error)

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    
    :return: None if all OK, RunTrialResult.xxx if trial should terminate
    """

    if config.stimulus_then_move:

        raise Exception("TBD") #todo

    else:
        #-- Wait for the participant to start moving the finger
        rc = exp_info.start_point.wait_until_exit(exp_info.xpy_exp, on_loop_present=exp_info.stimuli)
        if rc == StartPoint.State.aborted:
            return RunTrialResult.Aborted

        elif rc == StartPoint.State.error:
            trial_failed(ExperimentError("StartedSideways", "Start the trial by moving straight, not sideways!"), exp_info, trial)
            return RunTrialResult.Failed

    on_finger_started_moving(exp_info, config, trial)
    return None


#----------------------------------------------------------------
def initialize_trial(exp_info, trial):
    """
    Initialize a trial
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    exp_info.start_point.reset()
    exp_info.numberline.reset()    # mark the line as yet-untouched

    exp_info.stimuli.present()  # reset the display

    update_target(exp_info, trial)

    exp_info.trial_data = {}

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_INITIALIZED, 0, get_time() - exp_info.session_start_time)


#----------------------------------------------------------------
def on_finger_touched_screen(exp_info, trial):
    """
    This function should be called when the finger touches the screen

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    exp_info.numberline.feedback_stim.visible = False
    exp_info.errmsg_textbox.visible = False

    trial.start_time = get_time()

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_STARTED, 0, trial.start_time - exp_info.session_start_time)

    exp_info.stimuli.present()

    #-- Reset all trajectory-sensitive objects
    for obj in exp_info.trajectory_sensitive_objects:
        obj.reset(0)


#----------------------------------------------------------------
def on_finger_started_moving(exp_info, config, trial):
    """
    This function should be called when the finger leaves the "start" area and starts moving

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type config: trajtracker.paradigms.num2pos.Config 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    t = get_time()
    time_in_trial = t - trial.start_time
    time_in_session = t - exp_info.session_start_time
    trial.results['time_started_moving'] = time_in_trial

    exp_info.event_manager.dispatch_event(FINGER_STARTED_MOVING, time_in_trial, time_in_session)

    exp_info.stimuli.present()

    if not config.stimulus_then_move:
        trial.results['time_target_shown'] = get_time() - trial.start_time


#----------------------------------------------------------------
def update_target(exp_info, trial):
    """
    Update the target objects when the trial is initialized

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    if 'target_text' in trial.csv_data:
        target_text = trial.csv_data['target_text']
    else:
        target_text = str(trial.target)

    if exp_info.config.target_type == 'rsvp_text':
        exp_info.target.text = target_text.split(";")
        if 'onset_time' in trial.csv_data:
            exp_info.target.onset_time = [float(s) for s in trial.csv_data['onset_time'].split(";")]
        if 'duration' in trial.csv_data:
            exp_info.target.onset_time = [float(s) for s in trial.csv_data['duration'].split(";")]

    elif exp_info.config.target_type == 'text':
        exp_info.target.text = [target_text]


#------------------------------------------------
def update_movement(exp_info, trial):
    """
    Update the trajectory-sensitive objects about the mouse/finger movement
        
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :return: None if all is OK; or an ExperimentError object if one of the validators issued an error
    """

    finger_position = exp_info.xpy_exp.mouse.position

    curr_time = get_time()
    time_in_trial = curr_time - trial.start_time

    for obj in exp_info.trajectory_sensitive_objects:
        err = obj.update_xyt(finger_position[0], finger_position[1], time_in_trial)
        if err is not None:
            return err

    exp_info.event_manager.on_frame(time_in_trial, curr_time - exp_info.session_start_time)

    return None


#------------------------------------------------
# This function is called when a trial ends with an error
#
def trial_failed(err, exp_info, trial):
    """
    Called when the trial failed for any reason 
    (only when a strict error occurred; pointing at an incorrect location does not count as failure) 

    :type err: ExperimentError
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    print("   ERROR in trial: " + err.message)

    curr_time = get_time()

    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_FAILED, time_in_trial, time_in_session)

    exp_info.errmsg_textbox.unload()
    exp_info.errmsg_textbox.text = err.message
    exp_info.errmsg_textbox.visible = True

    exp_info.sound_err.play()

    trial_ended(exp_info, trial, time_in_trial, "ERR_" + err.err_code)


#------------------------------------------------
# This function is called when a trial ends with no error
#
def trial_succeeded(exp_info, trial):
    """
    Called when the trial ends successfully (i.e. the finger touched the numberline - doesn't matter where)
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    print("   Trial ended successfully.")

    #todo: show the correct location?

    curr_time = get_time()
    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_SUCCEEDED, time_in_trial, time_in_session)

    play_success_sound(exp_info, trial)

    trial_ended(exp_info, trial, time_in_trial, "OK")

    exp_info.trajtracker.save_to_file(trial.trial_num)


#------------------------------------------------
def play_success_sound(exp_info, trial):
    """
    Play a "trial succeeded" sound. If required in the configuration, we select here the sound
    depending on the endpoint error.
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    endpoint_err = np.abs(exp_info.numberline.last_touched_value - trial.target)
    endpoint_err_ratio = min(1, endpoint_err / (exp_info.numberline.max_value - exp_info.numberline.min_value))
    sound_ind = np.where(endpoint_err_ratio <= exp_info.sounds_ok_max_ep_err)[0][0]
    exp_info.sounds_ok[sound_ind].play()


#------------------------------------------------
def trial_ended(exp_info, trial, time_in_trial, success_err_code):
    """
    This function is called whenever a trial ends, either successfully or with failure.
    
    Its main role is to write a row to the trials.csv file.
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    :param time_in_trial: 
    :param success_err_code: A string code to write as status for this trial 
    :return: 
    """

    exp_info.stimuli.present()

    if exp_info.config.save_results:

        endpoint = exp_info.numberline.last_touched_value
        t_move = trial.results['time_started_moving'] if 'time_started_moving' in trial.results else -1
        t_target = trial.results['time_target_shown'] if 'time_target_shown' in trial.results else -1

        if time_in_trial == 0 or 'time_target_shown' not in trial.results:
            movement_time = 0
        else:
            movement_time = time_in_trial - trial.results['time_target_shown']

        #-- Save data to trials file
        trial_out_row = {
            'trialNum':             trial.trial_num,
            'LineNum':              trial.file_line_num,
            'target':               trial.target,
            'presentedTarget':      trial.csv_data['target'], #todo: what about target_text? what about displaying images?
            'endPoint':             "" if endpoint is None else "{:.3g}".format(endpoint),
            'status':               success_err_code,
            'movementTime':         "{:.3g}".format(movement_time),
            'timeInSession':        "{:.3g}".format(trial.start_time - exp_info.session_start_time),
            'timeUntilFingerMoved': "{:.3g}".format(t_move),
            'timeUntilTarget':      "{:.3g}".format(t_target),
        }

        if exp_info.trials_file_writer is None:
            fields = ['trialNum', 'LineNum', 'target', 'presentedTarget', 'status', 'endPoint', 'movementTime',
                      'timeInSession', 'timeUntilFingerMoved', 'timeUntilTarget']
            filename = xpy.io.defaults.datafile_directory + "/" + exp_info.trials_out_filename
            exp_info.trials_out_fp = open(filename, 'w')
            exp_info.trials_file_writer = csv.DictWriter(exp_info.trials_out_fp, fields)
            exp_info.trials_file_writer.writeheader()

        exp_info.trials_file_writer.writerow(trial_out_row)
        exp_info.trials_out_fp.flush()


#------------------------------------------------
def save_session_file(exp_info):
    pass
    #todo
