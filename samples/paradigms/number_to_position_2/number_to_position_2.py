"""

A simple version of the number-to-position experiment: 
- 0-100 number line
- Targets are printed as "decade+unit" (provided in a CSV file)
- The decade addend appears first, and after 100 ms the unit addend
- The color of the feedback arrow changes according to the response accuracy (endpoint error), 
  and so does the acknowledgement sound.
- The correct location is shown with the feedback
- Support both stimulus-then-move and move-then-stimulus modes

Changing during the trial (first decade, then decade+unit) is acheived by defining TWO stimuli per trial.
Both are defined in a single MultiTextBox object (exp_info.target). To define when one stimulus changes
into the other, the MultiTextBox defines "onset_time" and "duration" for each of the two per-trial stimuli.

Defining onset_time and duration could have been done by adding two columns with this name to the
number_to_position_2.csv file. However, here I used a different method: I defined MultiTextBox.onset_time and
MultiTextBox.duration in advance, only once, when initializing the experiment. To allow this, I had to 
copy the trajtracker.paradigms.num2pos.run_full_experiment() function and make a small modification.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.paradigms import num2pos, common


#-- Change this to True to switch into stimulus-then-move mode
STIMULUS_THEN_MOVE = False

if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True

ttrk.env.default_log_level = ttrk.log_info


accuracy_levels = [.05, .1]

config = num2pos.Config("Num2Pos(D+U)",
                        stimulus_then_move=STIMULUS_THEN_MOVE,
                        max_trial_duration=2,
                        speed_guide_enabled=True,
                        max_numberline_value=100,
                        data_source="number_to_position_2.csv",  # Read targets from this CSV file
                        text_target_height=0.5,

                        post_response_target=True,         # After response was made, show the correct location
                        feedback_arrow_colors=[xpy.misc.constants.C_GREEN,
                                               xpy.misc.constants.C_EXPYRIMENT_ORANGE,
                                               xpy.misc.constants.C_RED],
                        feedback_accuracy_levels=accuracy_levels,
                        sound_by_accuracy=((accuracy_levels[0], 'feedback-accuracy-0.wav'),
                                           (accuracy_levels[1], 'feedback-accuracy-1.wav'),
                                           (1, 'feedback-accuracy-2.wav')),
                        sounds_dir="../sounds"
                        )

if STIMULUS_THEN_MOVE:
    config.finger_moves_min_time = 0.6
    config.finger_moves_max_time = 1.5

#----------------------------------------------------------------

#-- Initialize & start the Expyriment
exp = ttrk.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- Get subject info
(subj_id, subj_name) = ttrk.paradigms.common.get_subject_name_id()


#-- Run the experiment

# The lines below (until the "End of copied code" comment) were copied here from
# trajtracker.paradigms.num2pos.run_full_experiment()

exp_info = num2pos.ExperimentInfo(config, exp, subj_id, subj_name)
num2pos.create_experiment_objects(exp_info)

#-- These 5 lines were not in the original version of run_full_experiment(), I added them only here.
#-- Making this small modification is the reason that I copied run_full_experiment()
if STIMULUS_THEN_MOVE:
    exp_info.text_target.onset_time = [0.5, 0.6]
else:
    exp_info.text_target.onset_time = [0, 0.1]
exp_info.text_target.duration = [0.1, 2]

common.register_to_event_manager(exp_info)
num2pos.run_trials(exp_info)

#End of copied code


#-- Shutdown Expyriment
xpy.control.end()
