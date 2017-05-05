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

from _n2p_init import \
    create_errmsg_textbox, \
    create_experiment_objects, \
    create_numberline, \
    create_sounds, \
    create_start_point, \
    create_textbox_target, \
    create_traj_tracker, \
    create_validators, \
    load_data_source, \
    load_sound, \
    register_to_event_manager


from _n2p_run import \
    initialize_trial, \
    on_finger_started_moving, \
    on_finger_touched_screen, \
    play_success_sound, \
    run_full_experiment, \
    run_trial, \
    run_trials, \
    save_session_file, \
    trial_ended, \
    trial_failed, \
    trial_succeeded, \
    update_movement, \
    update_text_target_for_trial
