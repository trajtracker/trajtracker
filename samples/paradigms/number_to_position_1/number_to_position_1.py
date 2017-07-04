"""

A simple version of the number-to-position experiment:
- 0-100 number line
- Each target appears twice

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy

import trajtracker as ttrk
import trajtrackerp as ttrkp
from trajtrackerp import num2pos


if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True


config = num2pos.Config("Num2Pos(0-100*2)", max_movement_time=2, max_numberline_value=100,
                        speed_guide_enabled=True, data_source=range(101) * 2)


#-- Initialize Expyriment

exp = ttrk.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrkp.common.get_subject_name_id()

#-- Run the experiment
exp_info = ExperimentInfo(config, xpy_exp, subj_id, subj_name)
num2pos.create_experiment_objects(exp_info)
common.register_to_event_manager(exp_info)
num2pos.run_trials(exp_info)

#-- Shutdown Expyriment
xpy.control.end()
