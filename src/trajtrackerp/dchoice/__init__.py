"""
This module has functions to support the discrete-choice paradigm

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
