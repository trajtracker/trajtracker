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


from trajtrackerp.common import BaseTrialInfo


class TrialInfo(BaseTrialInfo):

    #---------------------------------------------------------
    def __init__(self, trial_num, csv_row, exp_config):

        super(TrialInfo, self).__init__(trial_num, csv_row, exp_config)

        #: The target location
        self.target = csv_row['target']
