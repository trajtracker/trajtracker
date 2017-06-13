"""
Functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import numpy as np
import random

import trajtracker as ttrk
from trajtracker.utils import get_time
from trajtracker.validators import ExperimentError
from trajtracker.movement import StartPoint
from trajtracker.paradigms import common
from trajtracker.paradigms.common import RunTrialResult, FINGER_STARTED_MOVING

from trajtracker.paradigms.num2pos import ExperimentInfo, TrialInfo, create_experiment_objects


#----------------------------------------------------------------
def run_full_experiment(config, xpy_exp, subj_id, subj_name=""):
    """
    A default implementation for running a complete experiment, end-to-end: loading the data,
    initializing all objects, running all trials, and saving the results.
    
    :param config:
    :type config: trajtracker.paradigms.num2pos.Config 

    :param xpy_exp: Expyriment's `active experiment <http://docs.expyriment.org/expyriment.design.Experiment.html>`_
                    object
    :param subj_id: The subject initials from the num2pos app welcome screen
    :param subj_name: The subject name from the num2pos app welcome screen (or an empty string) 
    """

    exp_info = ExperimentInfo(config, xpy_exp, subj_id, subj_name)

    create_experiment_objects(exp_info)

    common.register_to_event_manager(exp_info)

    run_trials(exp_info)


#----------------------------------------------------------------
def run_trials(exp_info):

    common.init_experiment(exp_info)

    trial_num = 1

    while len(exp_info.trials) > 0:

        trial_config = exp_info.trials.pop(0)

        ttrk.log_write("====================== Starting trial #{:} =====================".format(trial_num))

        run_trial_rc = run_trial(exp_info, TrialInfo(trial_num, trial_config, exp_info.config))
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
            if exp_info.config.shuffle_trials:
                random.shuffle(exp_info.trials)

        else:
            raise Exception("Invalid result from run_trial(): {:}".format(run_trial_rc))


#----------------------------------------------------------------
def run_trial(exp_info, trial):
    """
    Run a single trial
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
     
    :return: True if the trial ended successfully, False if it failed
    """

    initialize_trial(exp_info, trial)

    exp_info.start_point.wait_until_startpoint_touched(exp_info.xpy_exp,
                                                       on_loop_present=exp_info.stimuli,
                                                       event_manager=exp_info.event_manager,
                                                       trial_start_time=trial.start_time,
                                                       session_start_time=exp_info.session_start_time)
    on_finger_touched_screen(exp_info, trial)

    rc = wait_until_finger_moves(exp_info, trial)
    if rc is not None:
        return rc

    while True:  # This loop runs once per frame

        #-- Update all displayable elements
        exp_info.stimuli.present()

        if not ttrk.env.mouse.check_button_pressed(0):
            trial_failed(ExperimentError("FingerLifted", "You lifted your finger in mid-trial"), exp_info, trial)
            return RunTrialResult.Failed

        #-- Inform relevant objects (validators, trajectory tracker, event manager, etc.) of the progress
        err = common.update_movement_in_traj_sensitive_objects(exp_info, trial)
        if err is not None:
            trial_failed(err, exp_info, trial)
            return RunTrialResult.Failed

        #-- Check if the number line was reached
        if exp_info.numberline.touched:

            movement_time = get_time() - trial.results['time_started_moving'] - trial.start_time
            if movement_time < exp_info.config.min_trial_duration:
                trial_failed(ExperimentError(ttrk.validators.InstantaneousSpeedValidator.err_too_fast,
                                             "Please move more slowly"),
                             exp_info, trial)
                return RunTrialResult.Failed

            trial_succeeded(exp_info, trial)
            return RunTrialResult.Succeeded

        xpy.io.Keyboard.process_control_keys()


#----------------------------------------------------------------
def on_finger_touched_screen(exp_info, trial):
    """
    This function should be called when the finger touches the screen

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    """

    exp_info.errmsg_textbox.visible = False
    exp_info.target_pointer.visible = False

    common.show_fixation(exp_info)
    update_numberline_for_trial(exp_info, trial)

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_STARTED, 0,
                                          get_time() - exp_info.session_start_time)

    exp_info.stimuli.present()

    trial.start_time = get_time()

    #-- Reset all trajectory-sensitive objects
    for obj in exp_info.trajectory_sensitive_objects:
        obj.reset(0)


#----------------------------------------------------------------
def wait_until_finger_moves(exp_info, trial):
    """
    The function returns after the finger started moving (or on error)

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 

    :return: None if all OK, RunTrialResult.xxx if trial should terminate
    """

    # -- Wait for the participant to start moving the finger
    if exp_info.config.is_fixation_zoom:
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
        # -- Finger lifted
        common.show_fixation(exp_info, False)
        return RunTrialResult.Aborted

    elif exp_info.start_point.state == StartPoint.State.error:
        # -- Invalid start direction
        trial_failed(ExperimentError("StartedSideways", "Start the trial by moving straight, not sideways!"),
                     exp_info, trial)
        return RunTrialResult.Failed

    elif exp_info.start_point.state == StartPoint.State.timeout:
        # -- Finger moved too late
        trial_failed(ExperimentError("FingerMovedTooLate", "You moved too late"), exp_info, trial)
        return RunTrialResult.Failed

    if trial.finger_moves_min_time is not None and get_time() - trial.start_time < trial.finger_moves_min_time:
        # -- Finger moved too early
        trial_failed(ExperimentError("FingerMovedTooEarly", "You moved too early"), exp_info, trial)
        return RunTrialResult.Failed

    common.on_finger_started_moving(exp_info, trial)

    return None


#----------------------------------------------------------------
def initialize_trial(exp_info, trial):
    """
    Initialize a trial
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    exp_info.start_point.reset()
    exp_info.numberline.reset()    # mark the line as yet-untouched

    exp_info.text_target.terminate_display()
    exp_info.generic_target.terminate_display()

    exp_info.stimuli.present()  # reset the display

    common.update_text_target_for_trial(exp_info, trial)
    common.update_generic_target_for_trial(exp_info, trial)
    if exp_info.fixation is not None:
        common.update_fixation_for_trial(exp_info, trial)

    exp_info.numberline.target = trial.target

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_INITIALIZED, 0, get_time() - exp_info.session_start_time)

    #-- Update the display to present stuff that may have been added by the TRIAL_INITIALIZED event listeners
    exp_info.stimuli.present()

    if exp_info.config.stimulus_then_move:
        trial.results['targets_t0'] = get_time() - trial.start_time


#------------------------------------------------
def update_numberline_for_trial(exp_info, trial):
    """
    Update the number line when the trial is initialized

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo
    """

    common.update_attr_by_csv_config(exp_info, trial, exp_info.numberline, 'nl.position', 'position')

    common.update_obj_position(exp_info, trial, exp_info.numberline, 'nl', 'x')
    common.update_obj_position(exp_info, trial, exp_info.numberline, 'nl', 'y')


#------------------------------------------------
# This function is called when a trial ends with an error
#
def trial_failed(err, exp_info, trial):
    """
    Called when the trial failed for any reason 
    (only when a strict error occurred; pointing at an incorrect location does not count as failure) 

    :type err: ExperimentError
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    ttrk.log_write("ERROR in trial ({:}). Message shown to subject: {:}".format(err.err_code, err.message))

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
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    print("   Trial ended successfully.")

    if exp_info.config.post_response_target:
        c = exp_info.numberline.value_to_coords(trial.target)
        exp_info.target_pointer.position = c[0], c[1] + exp_info.target_pointer_height / 2
        exp_info.target_pointer.visible = True

    curr_time = get_time()
    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_SUCCEEDED, time_in_trial, time_in_session)

    play_success_sound(exp_info, trial)

    trial_ended(exp_info, trial, time_in_trial, "OK")

    exp_info.trajtracker.save_to_file(trial.trial_num)


#------------------------------------------------
def trial_ended(exp_info, trial, time_in_trial, success_err_code):
    """
    This function is called whenever a trial ends, either successfully or with failure.
    It updates the result files.
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    :param time_in_trial: 
    :param success_err_code: A string code to write as status for this trial 
    """

    exp_info.stimuli.present()

    if exp_info.config.save_results:
        update_trials_file(exp_info, trial, time_in_trial, success_err_code)

        #-- Save the session at the end of each trial, to make sure it's always saved - even if
        #-- the experiment software unexpectedly terminates
        common.save_session_file(exp_info, "NL")


#------------------------------------------------
def update_trials_file(exp_info, trial, time_in_trial, success_err_code):
    """
    Add an entry (line) to the trials.csv file
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    :param time_in_trial: 
    :param success_err_code: A string code to write as status for this trial 
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

    endpoint = exp_info.numberline.response_value
    t_move = trial.results['time_started_moving'] if 'time_started_moving' in trial.results else -1
    t_target = trial.results['targets_t0'] if 'targets_t0' in trial.results else -1

    # -- Save data to trials file
    trial_out_row = {
        'trialNum': trial.trial_num,
        'LineNum': trial.file_line_num,
        'target': trial.target,
        'presentedTarget': presented_target,
        'endPoint': "" if endpoint is None else "{:.3g}".format(endpoint),
        'status': success_err_code,
        'movementTime': "{:.3g}".format(movement_time),
        'timeInSession': "{:.3g}".format(trial.start_time - exp_info.session_start_time),
        'timeUntilFingerMoved': "{:.3g}".format(t_move),
        'timeUntilTarget': "{:.3g}".format(t_target),
    }

    if exp_info.trials_file_writer is None:
        open_trials_file(exp_info)

    exp_info.trials_file_writer.writerow(trial_out_row)
    exp_info.trials_out_fp.flush()


#------------------------------------------------
def open_trials_file(exp_info):
    """
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    """

    fields = ['trialNum', 'LineNum', 'target', 'presentedTarget', 'status', 'endPoint', 'movementTime',
              'timeInSession', 'timeUntilFingerMoved', 'timeUntilTarget']

    return common.open_trials_file(exp_info, fields)


# ------------------------------------------------
def play_success_sound(exp_info, trial):
    """
    Play a "trial succeeded" sound. If required in the configuration, we select here the sound
    depending on the endpoint error.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.common.BaseTrialInfo 
    """

    endpoint_err = np.abs(exp_info.numberline.response_value - trial.target)
    endpoint_err_ratio = min(1, endpoint_err / (exp_info.numberline.max_value - exp_info.numberline.min_value))
    sound_ind = np.where(endpoint_err_ratio <= exp_info.sounds_ok_max_ep_err)[0][0]
    exp_info.sounds_ok[sound_ind].play()


