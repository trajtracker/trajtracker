"""

A simple two-choice task. Stimuli = the words "left" and "right"

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
import trajtrackerp as ttrkp
from trajtrackerp import dchoice

if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True

config = dchoice.Config("ChooseDir", max_movement_time=2, data_source="choice_1.csv",
                        use_text_targets=True,
                        feedback_stim_type='rectangle', feedback_select_by='response',
                        feedback_place='button',
                        speed_guide_enabled=True)

#-- Initialize Expyriment
exp = ttrk.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrkp.common.get_subject_name_id()

#-- Run the experiment
exp_info = dchoice.initialize_experiment(config, exp, subj_id, subj_name)
dchoice.run_trials(exp_info)

#-- Shutdown Expyriment
xpy.control.end()
