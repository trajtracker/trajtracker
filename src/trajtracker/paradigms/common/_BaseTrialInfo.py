"""
The information of one trial

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


from trajtracker.io import CSVLoader


class BaseTrialInfo(object):

    #---------------------------------------------------------
    def __init__(self, trial_num, csv_row, exp_config):

        #: The trial number
        self.trial_num = trial_num

        #: The time when the trial started
        self.start_time = None

        #: The time, relatively to self.start_time, that counts as t=0 for targets.
        #: In "move-then-stimulus" mode, this is the frame right after the finger started moving
        #: In "stimulus-then-move" mode, this is the time when the finger touched the screen
        self.targets_t0 = None

        #: results collected during the experiment
        self.results = {}

        #: The line number (in the CSV file) that corresponds with this trial
        self.file_line_num = csv_row[CSVLoader.FLD_LINE_NUM]

        #: The data loaded from the CSV file (dict)
        self.csv_data = csv_row

        #: Whether text targets should be presented in this trial
        self.use_text_targets = csv_row['use_text_targets'] if exp_config.use_text_targets is None else exp_config.use_text_targets

        #: Whether non-text (generic) targets should be presented in this trial
        self.use_generic_targets = csv_row['use_generic_targets'] if exp_config.use_generic_targets is None else exp_config.use_generic_targets

        #: The earliest time (relatively to the touch-screen time) when the finger can move
        self.finger_moves_min_time = csv_row['finger_moves_min_time'] if 'finger_moves_min_time' in csv_row else exp_config.finger_moves_min_time

        #: The latest time (relatively to the touch-screen time) when the finger must move
        self.finger_moves_max_time = csv_row['finger_moves_max_time'] if 'finger_moves_max_time' in csv_row else exp_config.finger_moves_max_time

        #: Whether the FINGER_STOPPED_MOVING event was already dispatched
        self.stopped_moving_event_dispatched = False

        #: Movement time of this trial
        self.movement_time = None
