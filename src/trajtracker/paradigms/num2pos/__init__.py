"""
This module has functions to support the number-to-position paradigm

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
from ._DownArrow import DownArrow

from ._n2p_init import \
    create_experiment_objects, \
    create_numberline, \
    create_sounds, \
    load_data_source

from ._n2p_run import \
    initialize_trial, \
    on_finger_touched_screen, \
    play_success_sound, \
    run_full_experiment, \
    run_trial, \
    run_trials, \
    trial_ended, \
    trial_failed, \
    trial_succeeded
