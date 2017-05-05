"""
The information of one trial

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


from trajtracker.data import CSVLoader


class TrialInfo(object):

    #---------------------------------------------------------
    def __init__(self, trial_num, csv_row, exp_config):

        self.trial_num = trial_num
        self.start_time = None
        self.targets_t0 = None  # The time, relatively to self.start_time, that counts as t=0 for targets.
                                # In "move-then-stimulus" mode, this is the frame right after the finger started moving
                                # In "stimulus-then-move" mode, this is the time when the finger touched the screen
        self.results = {}       # results collected during the experiment

        self.file_line_num = csv_row[CSVLoader.FLD_LINE_NUM]
        self.csv_data = csv_row

        s_target = csv_row['target']
        self.target = int(s_target) if s_target.isdigit() else float(s_target)

        self.use_text_targets = csv_row['use_text_targets'] if exp_config.use_text_targets is None else exp_config.use_text_targets
        self.use_generic_targets = csv_row['use_generic_targets'] if exp_config.use_generic_targets is None else exp_config.use_generic_targets

        if 'finger_moves_min_time' in csv_row:
            self.finger_moves_min_time = float(csv_row['finger_moves_min_time'])
        else:
            self.finger_moves_min_time = exp_config.finger_moves_min_time

        if 'finger_moves_max_time' in csv_row:
            self.finger_moves_max_time = float(csv_row['finger_moves_max_time'])
        else:
            self.finger_moves_max_time = exp_config.finger_moves_max_time
