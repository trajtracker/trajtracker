"""

A simple quantity-to-position experiment. This is identical with digital_0_100_b.py, 
except that the stimuli are dot clouds rather than symbolic numbers, and they do not change
during a trial.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
import numpy as np
import random

import expyriment as xpy

import trajtracker as ttrk
import trajtrackerp as ttrkp
from trajtrackerp import num2pos

#----------------------------------------------------------------

if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True

ttrk.env.default_log_level = ttrk.log_info


#-----------------------------------
#    Basic configuration
#-----------------------------------

accuracy_levels = [.05, .1]

config = num2pos.Config("Q2Pos(D+U)",
                        max_movement_time=2,
                        speed_guide_enabled=True,
                        max_numberline_value=100,
                        data_source="quantity_to_position.csv",  # Read targets from this CSV file
                        text_target_height=0.5,

                        use_text_targets=False,
                        use_generic_targets=True,

                        post_response_target=True,         # After response was made, show the correct location
                        feedback_arrow_colors=[xpy.misc.constants.C_GREEN,
                                               xpy.misc.constants.C_EXPYRIMENT_ORANGE,
                                               xpy.misc.constants.C_RED],
                        feedback_accuracy_levels=accuracy_levels,
                        sound_by_accuracy=((accuracy_levels[0], 'feedback-accuracy-0.wav'),
                                           (accuracy_levels[1], 'feedback-accuracy-1.wav'),
                                           (1, 'feedback-accuracy-2.wav'))
                        )

#=================================================================================
#  Functions for creating the visual stimuli - one dot cloud per target number
#=================================================================================

#----------------------------------------------------------------
# Create stimuli: grey circle with dots in random positions
#
def create_stimuli(min_value, max_value):

    stimuli = {}

    for n in range(min_value, max_value):
        main_circle = xpy.stimuli.Circle(radius=35, colour=xpy.misc.constants.C_GREY)
        dots = []

        for i in range(n):
            dot = xpy.stimuli.Circle(radius=2, colour=xpy.misc.constants.C_BLACK)
            randomize_dot_position(dots, dot, main_circle.radius-3, "%d(dot#%d)" % (n, i))
            dot.radius = 1
            dot.plot(main_circle)

        stimuli[str(n)] = main_circle

    return stimuli


#----------------------------------------------------------------
# Find a random position for a dot, which does not overlap with any of the previous dots
#
def randomize_dot_position(other_dots, new_dot, radius, dot_desc):

    for i in range(10000):
        new_pos = get_random_pos(radius)
        is_overlap = sum([d.overlapping_with_position(new_pos) for d in other_dots]) > 0
        if not is_overlap:
            new_dot.position = new_pos
            return

    raise Exception("Can't find position for stimuls %s" % dot_desc)


#----------------------------------------------------------------
# Select a random position for the dot.
def get_random_pos(radius):

    # Random distance from the middle (to get even dot distribution, the probability is
    # proportional to distance**2)
    r = np.sqrt(random.random() * radius**2)

    alpha = random.random() * np.pi * 2  # Random angle

    x = int(r * np.cos(alpha))
    y = int(r * np.sin(alpha))

    return (x,y)


#=================================================================================
#           Run experiment
#=================================================================================

#-- Initialize Expyriment

exp = xpy.control.initialize()
xpy.control.start(exp)

if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


stimuli = create_stimuli(0, 100)

#-- Get subject info
(subj_id, subj_name) = ttrkp.common.get_subject_name_id()


#-- Run the experiment

exp_info = ttrkp.num2pos.ExperimentInfo(config, exp, subj_id, subj_name)
ttrkp.num2pos.create_experiment_objects(exp_info)
exp_info.generic_target.available_stimuli = stimuli

ttrkp.num2pos.register_to_event_manager(exp_info)
ttrkp.num2pos.run_trials(exp_info)
ttrkp.num2pos.save_session_file(exp_info)

#-- Shutdown Expyriment
xpy.control.end()
