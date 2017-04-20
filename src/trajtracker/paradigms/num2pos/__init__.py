"""
This module has functions to support the number-to-position paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


def version():
    return "1.0"


from _Config import Config, FINGER_STARTED_MOVING
from _TrialInfo import TrialInfo
from _ExperimentInfo import ExperimentInfo
from _Arrow import Arrow

import CsvConfigFields

from _n2p_init import create_experiment_objects, create_numberline, create_start_point, \
    create_traj_tracker, create_validators, create_textbox_target, create_errmsg_textbox, \
    register_to_event_manager, create_sounds, load_sound, load_data_source

from _n2p_run import run_full_experiment, run_trials, run_trial, \
    initiate_trial, initialize_trial, on_finger_touched_screen, on_finger_started_moving, \
    update_target_stimulus, update_movement, trial_failed, trial_succeeded, trial_ended, play_success_sound, \
    save_session_file
