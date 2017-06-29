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

import expyriment as xpy
import numpy as np
import random

import trajtracker as ttrk
import trajtracker.utils as u
from trajtracker.movement import StartPoint
from trajtrackerp import common
from trajtrackerp.common import RunTrialResult, FINGER_STARTED_MOVING, FINGER_STOPPED_MOVING
from trajtracker.validators import ExperimentError

from trajtrackerp.num2pos import ExperimentInfo, TrialInfo, create_experiment_objects


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

    next_trial_already_initiated = False

    while len(exp_info.trials) > 0:

        trial_config = exp_info.trials.pop(0)

        ttrk.log_write("====================== Starting trial #{:} =====================".format(trial_num))

        run_trial_rc = run_trial(exp_info, TrialInfo(trial_num, trial_config, exp_info.config), next_trial_already_initiated)
        next_trial_already_initiated = False
        if run_trial_rc == RunTrialResult.Aborted:
            print("   Trial aborted.")
            continue

        trial_num += 1

        exp_info.exp_data['nTrialsCompleted'] += 1

        if run_trial_rc in (RunTrialResult.Succeeded, RunTrialResult.SucceededAndProceed):

            exp_info.exp_data['nTrialsSucceeded'] += 1
            next_trial_already_initiated = (run_trial_rc == RunTrialResult.SucceededAndProceed)

        elif run_trial_rc == RunTrialResult.Failed:

            exp_info.exp_data['nTrialsFailed'] += 1
            exp_info.trials.append(trial_config)
            if exp_info.config.shuffle_trials:
                random.shuffle(exp_info.trials)

        else:
            raise Exception("Invalid result from run_trial(): {:}".format(run_trial_rc))


#----------------------------------------------------------------
def run_trial(exp_info, trial, trial_already_initiated):
    """
    Run a single trial
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo
    :param trial_already_initiated: Indicates if the "start" point was already touched
    
    :return: RunTrialResult
    """

    initialize_trial(exp_info, trial)

    if trial_already_initiated:
        exp_info.start_point.mark_as_initialized()

    else:
        exp_info.start_point.wait_until_startpoint_touched(exp_info.xpy_exp,
                                                           on_loop_present=exp_info.stimuli,
                                                           event_manager=exp_info.event_manager,
                                                           trial_start_time=trial.start_time,
                                                           session_start_time=exp_info.session_start_time)
    on_finger_touched_screen(exp_info, trial)

    rc = common.wait_until_finger_moves(exp_info, trial)
    if rc is not None:
        if rc[1] is not None:
            trial_failed(rc[1], exp_info, trial)
        return rc[0]

    nl = exp_info.numberline

    while True:  # This loop runs once per frame

        #-- Update all displayable elements
        exp_info.stimuli.present()
        curr_time = u.get_time()

        #-- Validate that finger still touches the screen
        if not ttrk.env.mouse.check_button_pressed(0):
            trial_failed(ExperimentError("FingerLifted", "You lifted your finger in mid-trial"), exp_info, trial)
            return RunTrialResult.Failed

        #-- Inform relevant objects (validators, trajectory tracker, event manager, etc.) of the progress
        err = common.update_movement_in_traj_sensitive_objects(exp_info, trial)
        if err is not None:
            trial_failed(err, exp_info, trial)
            return RunTrialResult.Failed

        #-- Check if the number line was reached
        if nl.touched:

            common.on_response_made(exp_info, trial, curr_time)

            #-- Validate that the response wasn't too far
            max_excess = exp_info.config.max_response_excess
            if max_excess is not None and (nl.response_value < nl.min_value or nl.response_value > nl.max_value):
                excess = (nl.min_value - nl.response_value) if (nl.response_value < nl.min_value) \
                    else (nl.response_value - nl.max_value)
                excess /= (nl.max_value - nl.min_value)
                if excess > max_excess:
                    trial_failed(ExperimentError("ResponseTooFar", "Please point at the number line"),
                                 exp_info, trial)
                    return RunTrialResult.Failed

            #-- Validate that the response wasn't too fast
            if trial.movement_time < exp_info.config.min_trial_duration:
                trial_failed(ExperimentError(ttrk.validators.InstantaneousSpeedValidator.err_too_fast,
                                             "Please move more slowly"),
                             exp_info, trial)
                return RunTrialResult.Failed

            play_success_sound(exp_info, trial)

            #-- Optionally, run additional stages
            run_trial_result = common.run_post_trial_operations(exp_info, trial)
            if run_trial_result in (RunTrialResult.Succeeded, RunTrialResult.SucceededAndProceed):
                trial_succeeded(exp_info, trial)

            return run_trial_result

        xpy.io.Keyboard.process_control_keys()


#----------------------------------------------------------------
def on_finger_touched_screen(exp_info, trial):
    """
    This function should be called when the finger touches the screen

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo
    """

    exp_info.target_pointer.visible = False
    update_numberline_for_trial(exp_info, trial)
    common.on_finger_touched_screen(exp_info, trial)


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

    common.update_text_target_for_trial(exp_info, trial, use_numeric_target_as_default=True)
    common.update_generic_target_for_trial(exp_info, trial)
    if exp_info.fixation is not None:
        common.update_fixation_for_trial(exp_info, trial)

    exp_info.numberline.target = trial.target

    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_INITIALIZED, 0, u.get_time() - exp_info.session_start_time)

    #-- Update the display to present stuff that may have been added by the TRIAL_INITIALIZED event listeners
    exp_info.stimuli.present()

    if exp_info.config.stimulus_then_move:
        trial.results['targets_t0'] = u.get_time() - trial.start_time


#------------------------------------------------
def update_numberline_for_trial(exp_info, trial):
    """
    Update the number line when the trial is initialized

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo
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
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """
    common.trial_failed_common(err, exp_info, trial)
    trial_ended(exp_info, trial, "ERR_" + err.err_code)


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

    if exp_info.config.post_response_target:
        c = exp_info.numberline.value_to_coords(trial.target)
        exp_info.target_pointer.position = c[0], c[1] + exp_info.target_pointer_height / 2
        exp_info.target_pointer.visible = True

    curr_time = u.get_time()
    time_in_trial = curr_time - trial.start_time
    time_in_session = curr_time - exp_info.session_start_time
    exp_info.event_manager.dispatch_event(ttrk.events.TRIAL_SUCCEEDED, time_in_trial, time_in_session)

    trial_ended(exp_info, trial, "OK")

    exp_info.trajtracker.save_to_file(trial.trial_num)


#------------------------------------------------
def trial_ended(exp_info, trial, success_err_code):
    """
    This function is called whenever a trial ends, either successfully or with failure.
    It updates the result files.
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    :param success_err_code: A string code to write as status for this trial 
    """

    exp_info.stimuli.present()

    if exp_info.config.save_results:
        update_trials_file(exp_info, trial, success_err_code)

        #-- Save the session at the end of each trial, to make sure it's always saved - even if
        #-- the experiment software unexpectedly terminates
        common.save_session_file(exp_info, "NL")


#------------------------------------------------
def update_trials_file(exp_info, trial, success_err_code):
    """
    Add an entry (line) to the trials.csv file
    
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo 
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    :param success_err_code: A string code to write as status for this trial 
    """

    trial_out_row = common.prepare_trial_out_row(exp_info, trial, success_err_code)

    endpoint = exp_info.numberline.response_value
    trial_out_row['endPoint'] = "" if endpoint is None else "{:.3g}".format(endpoint)
    trial_out_row['target'] = trial.target

    if exp_info.trials_file_writer is None:
        common.open_trials_file(exp_info, ['target', 'endPoint'])

    exp_info.trials_file_writer.writerow(trial_out_row)
    exp_info.trials_out_fp.flush()


#------------------------------------------------
def play_success_sound(exp_info, trial):
    """
    Play a "trial succeeded" sound. If required in the configuration, we select here the sound
    depending on the endpoint error.

    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    :type trial: trajtracker.paradigms.num2pos.TrialInfo 
    """

    endpoint_err = np.abs(exp_info.numberline.response_value - trial.target)
    endpoint_err_ratio = min(1, endpoint_err / (exp_info.numberline.max_value - exp_info.numberline.min_value))
    sound_ind = np.where(endpoint_err_ratio <= exp_info.sounds_ok_max_ep_err)[0][0]
    exp_info.sounds_ok[sound_ind].play()

