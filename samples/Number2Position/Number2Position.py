"""

A simple version of the number-to-position experiment
This version uses random target numbers and does not save any results.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import random
import numpy as np

import expyriment as xpy
from trajtracker.utils import get_time

import trajtracker as ttrk
from trajtracker.movement import StartPoint


xpy.control.defaults.window_mode = True
ttrk.log_to_console = True

#-- Experiment constants
MAX_TRIAL_DURATION = 2
MAX_NUMBERLINE_VALUE = 100
GUIDE_ENABLED = True
N_TRIALS = 20


#------------------------------------------------
def run_trial():

    start_point.reset()
    number_line.reset()    # mark the line as yet-untouched

    all_stimuli.present()  # reset the display

    #-- Choose target
    target_box.visible = False
    target_box.unload()
    target_box.text = "{:.0f}".format(np.floor(random.random()*(MAX_NUMBERLINE_VALUE+1)))
    target_box.preload()

    #-- Wait for the participant to initiate the trial by touching the START point
    start_point.wait_until_startpoint_touched(exp, on_loop_present=all_stimuli)

    #-- Clean remains from previous trial
    feedback_arrow.visible = False
    err_textbox.visible = False
    all_stimuli.present()

    time0 = get_time()
    reset_trajectory_info(time0)

    #-- Wait for the participant to start moving the finger
    rc = start_point.wait_until_exit(exp, on_loop_present=all_stimuli)
    if rc == StartPoint.State.aborted:
        print("   Trial aborted.")
        return False
    elif rc == StartPoint.State.error:
        trial_error("Start the trial by moving upwards, not sideways!")
        return False

    #-- Movement started: show target
    target_box.visible = True
    all_stimuli.present()

    global_speed_validator.reset(get_time() - time0)   # indicate that time-counting starts now


    while True:  # This loop runs once per frame

        if not exp.mouse.check_button_pressed(0):
            trial_error("Finger lifted in mid-trial")
            return False

        err = update_trajectory(exp.mouse.position, get_time() - time0)
        if err is not None:
            trial_error(err.message)
            return False

        #-- Handle movement: Check if the number line was reached
        if number_line.touched:
            trial_succeeded()
            return True

        all_stimuli.present()  # update display


#------------------------------------------------
def reset_trajectory_info(trial_start_time):
    for obj in trajectory_sensitive_objects:
        obj.reset(trial_start_time)


#------------------------------------------------
# Run all validations for the given time point
#
def update_trajectory(finger_position, time_in_trial):

    for obj in trajectory_sensitive_objects:
        err = obj.update_xyt(finger_position[0], finger_position[1], time_in_trial)
        if err is not None:
            return err

    return None


#------------------------------------------------
# This function is called when a trial ends with an error
#
def trial_error(err):

    print("   ERROR in trial: " + err)

    err_textbox.unload()
    err_textbox.text = err
    err_textbox.visible = True

    target_box.visible = False
    speed_guide.activate(None)


#------------------------------------------------
# This function is called when a trial ends with no error
#
def trial_succeeded():

    print("   Trial ended successfully.")

    target_box.visible = False

    feedback_arrow.visible = True
    nl_pos = number_line.position
    feedback_arrow.position = (number_line.last_touched_coord + nl_pos[0], nl_pos[1] + feedback_arrow.height / 2)

    speed_guide.activate(None)


#===========================================================================================

#-- Initialize expyriment

exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#-- Initialize the objects for the number-to-position experiment
#---------------------------------------------------------------

all_stimuli = ttrk.stimuli.StimulusContainer()
trajectory_sensitive_objects = []

#-- Number line
number_line = ttrk.stimuli.NumberLine(position=(0, exp.screen.size[1] / 2 - 80),
                                      line_length=int(exp.screen.size[0] * 0.85),
                                      max_value=MAX_NUMBERLINE_VALUE,
                                      line_colour=xpy.misc.constants.C_WHITE,
                                      end_tick_height=5)
number_line.show_labels(font_name="Arial", font_size=26, box_size=(100, 30), offset=(0, 20),
                        font_colour=xpy.misc.constants.C_GREY)
all_stimuli.add(number_line)
trajectory_sensitive_objects.append(number_line)

#-- Feedback arrow
feedback_arrow = xpy.stimuli.Shape()
feedback_arrow.add_vertices([(10, 20), (-6, 0), (0, 20), (-9, 0), (0, -20), (-6, 0)])
feedback_arrow.colour = xpy.misc.constants.C_GREEN
all_stimuli.add(feedback_arrow, visible=False)

#-- "Start" area
start_area = xpy.stimuli.Rectangle(size=(40, 30))
start_area.position = (0, - (exp.screen.size[1] / 2 - start_area.size[1] / 2))
all_stimuli.add(start_area)
start_point = StartPoint(start_area)

# -- Target number
target_box = xpy.stimuli.TextBox("", (300, 80), (0, exp.screen.size[1] / 2 - 50),
                                 text_font="Arial", text_size=50, text_colour=xpy.misc.constants.C_WHITE)
all_stimuli.add(target_box, visible=False)

#-- Validators
direction_validator = \
    trajtracker.validators.MovementAngleValidator(min_angle=-90, max_angle=90, calc_angle_interval=20, enabled=True)
trajectory_sensitive_objects.append(direction_validator)

global_speed_validator = \
    trajtracker.validators.GlobalSpeedValidator(origin_coord=start_area.position[1] + start_area.size[1] / 2,
                                                end_coord=number_line.position[1],
                                                grace_period=0.3, max_trial_duration=MAX_TRIAL_DURATION,
                                                milestones=[(.5, .33), (.5, .67)], show_guide=GUIDE_ENABLED)
global_speed_validator.do_present_guide = False
trajectory_sensitive_objects.append(global_speed_validator)
speed_guide = global_speed_validator.guide.stimulus
if GUIDE_ENABLED:
    all_stimuli.add(speed_guide)

#-- Error message
err_textbox = xpy.stimuli.TextBox("", (290, 180), (0, 0),
                                  text_font="Arial", text_size=16, text_colour=xpy.misc.constants.C_RED)
all_stimuli.add(err_textbox, "err_box", visible=False)


#-- Run the experiment
n_trials_completed = 0
while n_trials_completed < N_TRIALS:
    if run_trial():
        n_trials_completed += 1


xpy.control.end()
