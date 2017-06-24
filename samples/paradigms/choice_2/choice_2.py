"""

A simple two-choice task. Stimuli = left/right arrows.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.paradigms import dchoice

if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True

config = dchoice.Config("ChooseArrowDir", max_trial_duration=2, data_source="choice_2.csv",
                        use_generic_targets=True, use_text_targets=False,
                        feedback_stim_type='rectangle', feedback_select_by='accuracy',
                        feedback_place='middle',
                        speed_guide_enabled=True, sounds_dir="../sounds")

stimuli = {
    'left': xpy.stimuli.Picture("arrow-left.bmp"),
    'right': xpy.stimuli.Picture("arrow-right.bmp")
}


#-- Initialize Expyriment

exp = ttrk.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrk.paradigms.common.get_subject_name_id()

#-- Run the experiment
exp_info = dchoice.initialize_experiment(config, exp, subj_id, subj_name)
exp_info.generic_target.available_stimuli = stimuli
dchoice.run_trials(exp_info)

#-- Shutdown Expyriment
xpy.control.end()
