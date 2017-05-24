"""

TrajTracker - general stuff for all paradigms

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from ._BaseConfig import BaseConfig, FINGER_STARTED_MOVING
from ._BaseExperimentInfo import BaseExperimentInfo
from ._BaseTrialInfo import BaseTrialInfo

from ._common_funcs_init import \
    create_errmsg_textbox, \
    create_fixation, \
    create_fixation_cross, \
    create_generic_target, \
    create_start_point, \
    create_textbox_fixation, \
    create_textbox_target, \
    create_traj_tracker, \
    create_validators, \
    get_subject_name_id, \
    load_sound, \
    register_to_event_manager

from ._common_funcs_run import \
    init_experiment, \
    on_finger_started_moving, \
    open_trials_file, \
    save_session_file, \
    show_fixation, \
    update_attr_by_csv_config, \
    update_fixation_for_trial, \
    update_generic_target_for_trial, \
    update_movement_in_traj_sensitive_objects, \
    update_text_target_for_trial, \
    update_obj_position, \
    RunTrialResult
