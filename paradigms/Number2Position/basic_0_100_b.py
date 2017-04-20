"""

A simple version of the number-to-position experiment: 
- 0-100 number line
- Targets are printed as "decade+unit" (provided in a CSV file)
- The decade addend appears first, and after 100 ms the unit addend  
- Show correct location in feedback
 

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
                        data_source="basic_0_100_b.csv",  # Read targets from this CSV file

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
# This function was copied to here from the "num2pos" package so we can change the
# configuration of the exp_info.target (which is a MultiTextBox object) after it was created.
#
def run_full_experiment(config):

    exp_info = num2pos.initialize_exp(config)

    num2pos.create_experiment_objects(exp_info, config)

    #-- The next 2 lines are the code that was changed relatively to the default implementation
    exp_info.target.onset_time = [0, 0.1]
    exp_info.target.duration = [0.1, 2]

    num2pos.register_to_event_manager(exp_info)

    num2pos.run_trials(exp_info, config)

    num2pos.save_session_file(exp_info)

    xpy.control.end()


#----------------------------------------------------------------

run_full_experiment(config)
