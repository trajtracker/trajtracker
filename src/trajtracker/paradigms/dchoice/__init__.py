"""
This module has functions to support the discrete-choice paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from ._Config import Config
from ._ExperimentInfo import ExperimentInfo
from ._TrialInfo import TrialInfo


from ._dc_init import \
    create_experiment_objects, \
    create_feedback_stimuli, \
    create_response_buttons, \
    create_sounds, \
    hide_feedback_stimuli, \
    initialize_experiment, \
    load_data_source

from ._dc_run import \
    initialize_trial, \
    get_touched_button, \
    run_trials, \
    run_trial, \
    trial_ended, \
    trial_failed, \
    trial_succeeded, \
    update_trials_file
