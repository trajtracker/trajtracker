"""
The information of one trial

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


from trajtracker.paradigms.common import BaseTrialInfo


class TrialInfo(BaseTrialInfo):

    #---------------------------------------------------------
    def __init__(self, trial_num, csv_row, exp_config):

        super(TrialInfo, self).__init__(trial_num, csv_row, exp_config)

        #: The target location
        self.target = csv_row['target']
