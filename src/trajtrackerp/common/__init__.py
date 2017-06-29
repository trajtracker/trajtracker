"""

TrajTracker - general stuff for all paradigms

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

from ._BaseConfig import BaseConfig, FINGER_STARTED_MOVING, FINGER_STOPPED_MOVING
from ._BaseExperimentInfo import BaseExperimentInfo
from ._BaseTrialInfo import BaseTrialInfo

from ._common_funcs_init import \
    create_common_experiment_objects, \
    create_csv_loader, \
    create_errmsg_textbox, \
    create_fixation, \
    create_fixation_cross, \
    create_generic_target, \
    create_confidence_slider, \
    create_start_point, \
    create_textbox_fixation, \
    create_textbox_target, \
    create_traj_tracker, \
    create_validators, \
    get_parser_for, \
    get_subject_name_id, \
    load_sound, \
    register_to_event_manager, \
    xy_to_pixels, \
    validate_config_param_type, \
    validate_config_param_values

from ._common_funcs_run import \
    acquire_confidence_rating, \
    init_experiment, \
    on_finger_started_moving, \
    on_finger_touched_screen, \
    on_response_made, \
    open_trials_file, \
    prepare_trial_out_row, \
    run_post_trial_operations, \
    save_session_file, \
    show_fixation, \
    trial_failed_common, \
    update_attr_by_csv_config, \
    update_fixation_for_trial, \
    update_generic_target_for_trial, \
    update_movement_in_traj_sensitive_objects, \
    update_text_target_for_trial, \
    update_obj_position, \
    wait_until_finger_moves, \
    RunTrialResult
