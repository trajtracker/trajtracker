"""
Functions to support the discrete-decision paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import numpy as np
import random

import trajtracker as ttrk
import trajtracker.utils as u
from trajtracker.validators import ExperimentError
from trajtracker.movement import StartPoint
from trajtracker.paradigms import common
from trajtracker.paradigms.common import RunTrialResult, FINGER_STARTED_MOVING

from trajtracker.paradigms.dchoice import ExperimentInfo, TrialInfo


#----------------------------------------------------------------
def run_full_experiment(config, xpy_exp, subj_id, subj_name=""):
    """
    A default implementation for running a complete experiment, end-to-end: loading the data,
    initializing all objects, running all trials, and saving the results.

    :param config:
    :type config: trajtracker.paradigms.dchoice.Config 

    :param xpy_exp: Expyriment's `active experiment <http://docs.expyriment.org/expyriment.design.Experiment.html>`_
                    object
    :param subj_id: The subject initials from the num2pos app welcome screen
    :param subj_name: The subject name from the num2pos app welcome screen (or an empty string) 
    """

    exp_info = ExperimentInfo(config, xpy_exp, subj_id, subj_name)

    common.create_experiment_objects(exp_info)

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

    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo 
    :type trial: trajtracker.paradigms.dchoice.TrialInfo

    :return: True if the trial ended successfully, False if it failed
    """

    initialize_trial(exp_info, trial)

    exp_info.start_point.wait_until_startpoint_touched(exp_info.xpy_exp,
                                                       on_loop_present=exp_info.stimuli,
                                                       event_manager=exp_info.event_manager,
                                                       trial_start_time=trial.start_time,
                                                       session_start_time=exp_info.session_start_time)
    common.on_finger_touched_screen(exp_info, trial)

    rc = common.wait_until_finger_moves(exp_info, trial)
    if rc is not None:
        if rc[1] is not None:
            trial_failed(rc[1], exp_info, trial)
        return rc[0]

    while True:  # This loop runs once per frame

        # -- Update all displayable elements
        exp_info.stimuli.present()

        if not ttrk.env.mouse.check_button_pressed(0):
            trial_failed(ExperimentError("FingerLifted", "You lifted your finger in mid-trial"), exp_info, trial)
            return RunTrialResult.Failed

        #-- Inform relevant objects (validators, trajectory tracker, event manager, etc.) of the progress
        err = common.update_movement_in_traj_sensitive_objects(exp_info, trial)
        if err is not None:
            trial_failed(err, exp_info, trial)
            return RunTrialResult.Failed

        #-- Check if a response button was reached
        user_response = get_touched_button(exp_info)
        if user_response is not None:

            movement_time = u.get_time() - trial.results['time_started_moving'] - trial.start_time
            if movement_time < exp_info.config.min_trial_duration:
                trial_failed(ExperimentError(ttrk.validators.InstantaneousSpeedValidator.err_too_fast,
                                             "Please move more slowly"),
                             exp_info, trial)
                return RunTrialResult.Failed

            trial_succeeded(exp_info, trial, user_response)
            return RunTrialResult.Succeeded

        xpy.io.Keyboard.process_control_keys()


#----------------------------------------------------------------
def get_touched_button(exp_info):
    """
    Check if any response button was touched

    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo 

    :return: The number of the touched button, or None if no button was touched
    """

    for hotspot in exp_info.response_buttons:
        if hotspot.touched:
            return hotspot.button_number

    return None


#----------------------------------------------------------------
def initialize_trial(exp_info, trial):
    """
    Initialize a trial

    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo 
    :type trial: trajtracker.paradigms.dchoice.TrialInfo 
    """

    exp_info.start_point.reset()
    for hotspot in exp_info.response_hotspots:
        hotspot.reset()

    exp_info.text_target.terminate_display()
    exp_info.generic_target.terminate_display()

    exp_info.stimuli.present()  # reset the display

    common.update_text_target_for_trial(exp_info, trial)
    common.update_generic_target_for_trial(exp_info, trial)
    if exp_info.fixation is not None:
        common.update_fixation_for_trial(exp_info, trial)

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_INITIALIZED, 0, u.get_time() - exp_info.session_start_time)

    # -- Update the display to present stuff that may have been added by the TRIAL_INITIALIZED event listeners
    exp_info.stimuli.present()

    if exp_info.config.stimulus_then_move:
        trial.results['targets_t0'] = u.get_time() - trial.start_time


#----------------------------------------------------------------
def trial_failed(err, exp_info, trial):
    """
    Called when the trial failed for any reason 
    (only when a strict error occurred; pointing at an incorrect location does not count as failure) 

    :type err: ExperimentError
    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo
    :type trial: trajtracker.paradigms.dchoice.TrialInfo 
    """
    common.trial_failed_common(err, exp_info, trial)
    trial_ended(exp_info, trial, time_in_trial, "ERR_" + err.err_code, -1)


#----------------------------------------------------------------
def trial_succeeded(exp_info, trial, user_response):


    print("   Trial ended successfully.")

    #todo: show feedback

    curr_time = u.get_time()
    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_SUCCEEDED, time_in_trial, time_in_session)

    exp_info.sounds_ok[0].play()

    trial_ended(exp_info, trial, time_in_trial, "OK", user_response)

    exp_info.trajtracker.save_to_file(trial.trial_num)


#------------------------------------------------
def trial_ended(exp_info, trial, time_in_trial, success_err_code, user_response):
    """
    This function is called whenever a trial ends, either successfully or with failure.
    It updates the result files.

    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo 
    :type trial: trajtracker.paradigms.dchoice.TrialInfo 
    :param time_in_trial: 
    :param success_err_code: A string code to write as status for this trial
    :param user_response: The number of the button that was pressed (-1 = no button)
    """

    exp_info.stimuli.present()

    if exp_info.config.save_results:
        update_trials_file(exp_info, trial, time_in_trial, success_err_code, user_response)

        #-- Save the session at the end of each trial, to make sure it's always saved - even if
        #-- the experiment software unexpectedly terminates
        common.save_session_file(exp_info, "DC")


#------------------------------------------------
def update_trials_file(exp_info, trial, time_in_trial, success_err_code, user_response):
    """
    Add an entry (line) to the trials.csv file

    :type exp_info: trajtracker.paradigms.dchoice.ExperimentInfo 
    :type trial: trajtracker.paradigms.dchoice.TrialInfo 
    :param time_in_trial: 
    :param success_err_code: A string code to write as status for this trial 
    :param user_response: The number of the button that was pressed (-1 = no button)
    """

    trial_out_row = common.prepare_trial_out_row(exp_info, trial, time_in_trial, success_err_code)

    trial_out_row['expectedResponse'] = -1 if trial.expected_response is None else trial.expected_response
    trial_out_row['UserResponse'] = user_response

    if exp_info.trials_file_writer is None:
        common.open_trials_file(exp_info, ['expectedResponse', 'UserResponse'])

    exp_info.trials_file_writer.writerow(trial_out_row)
    exp_info.trials_out_fp.flush()

