"""

A simple version of the number-to-position experiment: 
- 0-100 number line
- Targets are printed as "decade+unit" (provided in a CSV file)
- The decade addend appears first, and after 100 ms the unit addend
- The color of the feedback arrow changes according to the response accuracy (endpoint error), 
  and so does the acknowledgement sound.
- The correct location is shown with the feedback
 

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.paradigms import num2pos

if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True

ttrk.default_log_level = ttrk.log_info


accuracy_levels = [.05, .1]

config = num2pos.Config("Num2Pos(D+U)",
                        max_trial_duration=2,
                        max_numberline_value=100,
                        speed_guide_enabled=True,
                        data_source=[15, 30, 70, 43],  # todo "basic_0_100_b.csv",  # Read targets from this CSV file

                        post_response_target=True,         # After response was made, show the correct location
                        feedback_arrow_colors=[xpy.misc.constants.C_GREEN,
                                               xpy.misc.constants.C_EXPYRIMENT_ORANGE,
                                               xpy.misc.constants.C_RED],
                        feedback_accuracy_levels=accuracy_levels,
                        sound_by_accuracy=((accuracy_levels[0], 'feedback-accuracy-0.wav'),
                                           (accuracy_levels[1], 'feedback-accuracy-1.wav'),
                                           (1, 'feedback-accuracy-2.wav'))
                        )

#----------------------------------------------------------------

#-- Initialize Expyriment

exp = xpy.control.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrk.paradigms.general.get_subject_name_id()


#-- Run the experiment
#-- The lines below (until the "End of copied code" message) were copied here from the run_full_experiment()
#-- in the num2pos package.
#-- The reason we copied it is so we can change the default configuration of the target stimulus:
#-- We update the onset time and duration of the stimulus, which is required when presenting a changing stimulus.

#-- An alternative (and easier) solution could have been to add "onset_time" and "duration" columns to
#-- the CSV input file: the "num2pos" package can handle this configuration.

exp_info = ttrk.paradigms.num2pos.ExperimentInfo(config, exp, subj_id, subj_name)

num2pos.create_experiment_objects(exp_info)

# -- The next 2 lines are the code that was changed relatively to the default implementation
exp_info.target.onset_time = [0, 0.1]
exp_info.target.duration = [0.1, 2]

num2pos.register_to_event_manager(exp_info)

num2pos.run_trials(exp_info)

num2pos.save_session_file(exp_info)

#<< End of copied code


#-- Shutdown Expyriment
xpy.control.end()
