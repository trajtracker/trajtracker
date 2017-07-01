"""

A simple two-choice task. Stimuli = left/right arrows.

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

config = dchoice.Config("ChooseArrowDir", max_movement_time=3, data_source="choice_2.csv",
                        use_generic_targets=True, use_text_targets=False,
                        feedback_stim_type='rectangle', feedback_select_by='accuracy',
                        feedback_place='middle',
                        speed_guide_enabled=True)
stimuli = {
    'L': xpy.stimuli.Picture("arrow-left.bmp"),
    'R': xpy.stimuli.Picture("arrow-right.bmp")
}


#-- Initialize Expyriment
exp = ttrk.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrkp.common.get_subject_name_id()

#-- Initialize the experiment objects

exp_info = dchoice.initialize_experiment(config, exp, subj_id, subj_name)
exp_info.generic_target.available_stimuli = stimuli

exp_info.generic_target.onset_time = [0, 0.3, 0.6, 0.9, 1.2, 1.5]
exp_info.generic_target.duration = 0.1

#-- Run the experiment
dchoice.run_trials(exp_info)

#-- Shutdown Expyriment
xpy.control.end()
