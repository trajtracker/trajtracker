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
        self.results = {}       # results collected during the experiment

        self.file_line_num = csv_row[CSVLoader.FLD_LINE_NUM]
        self.csv_data = csv_row

        s_target = csv_row['target']
        self.target = int(s_target) if s_target.isdigit() else float(s_target)

        self.use_text_targets = csv_row['use_text_targets'] if exp_config.use_text_targets is None else exp_config.use_text_targets
        self.use_generic_targets = csv_row['use_generic_targets'] if exp_config.use_generic_targets is None else exp_config.use_generic_targets
