"""

A simple version of the number-to-position experiment
This version uses random target numbers (not from CSV), and does not save any results.

It may be useful for training.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import random
import numpy as np

import expyriment as xpy
from expyriment.misc._timer import get_time

import trajtracker as ttrk
from trajtracker.movement import StartPoint
from trajtracker.validators import *


xpy.control.defaults.window_mode = True


MAX_TRIAL_DURATION = 2
MAX_NUMBERLINE_VALUE = 100
GUIDE_ENABLED = True


#------------------------------------------------
def create_feedback_arrow(color):
    arrow = xpy.stimuli.Shape()
    # noinspection PyTypeChecker
    arrow.add_vertices([(10, 20), (-6, 0), (0, 20), (-9, 0), (0, -20), (-6, 0)])
    arrow.colour = color
    return arrow


#------------------------------------------------
def load_sound(filename):
    sound = xpy.stimuli.Audio("sounds/" + filename)
    sound.preload()
    return sound


#------------------------------------------------
def run_trial():

    target = "{:.0f}".format(np.floor(random.random()*(MAX_NUMBERLINE_VALUE+1)))
    print("Starting trial, target={:}".format(target))

    init_trial(target)

    #-- Wait for the participant to initiate the trial

    start_point.wait_until_touched(exp, all_stimuli)

    feedback_arrow.visible = False
    err_textbox.visible = False

    all_stimuli.present()
    time0 = get_time()

    reset_validators(time0)

    #-- Wait for the participant to start moving the finger

    rc = start_point.wait_until_exit(exp, on_loop=all_stimuli)
    if rc == StartPoint.State.aborted:
        print("   Trial aborted.")
        return
    elif rc == StartPoint.State.error:
        trial_error(ExperimentError("StartedSideways", "Start the trial by moving upwards, not sideways!", None))
        return

    #-- Movement started: initialize stuff
    target_box.visible = True
    all_stimuli.present()
    time_in_trial = get_time() - time0

    #-- Trial loop

    global_speed_validator.reset(time_in_trial)
    prev_finger_pos = None

    while True:

        finger_pos = exp.mouse.position
        still_touching_screen = exp.mouse.check_button_pressed(0)

        if not still_touching_screen:
            trial_error(ExperimentError("FingerLifted", "Finger lifted in mid-trial", None))
            return

        err = apply_validations(finger_pos, time_in_trial)
        if err is not None:
            trial_error(err)
            return

        #-- Handle movement: Check if the number line was reached
        if finger_pos != prev_finger_pos and number_line.update_xyt(finger_pos[0], finger_pos[1]):
            trial_succeeded()
            return

        #-- Go to next frame
        all_stimuli.present()
        time_in_trial = get_time() - time0
        prev_finger_pos = finger_pos


#------------------------------------------------
def init_trial(target):

    start_point.reset()
    number_line.reset()

    target_box.visible = False
    target_box.unload()
    target_box.text = target
    target_box.preload()

    reset_validators(0)


#------------------------------------------------
def reset_validators(trial_start_time):
    for validator in validators:
        validator.reset(trial_start_time)


#------------------------------------------------
# Run all validations for the given time point
#
def apply_validations(finger_position, time_in_trial):

    for validator in validators:
        err = validator.check_xyt(finger_position[0], finger_position[1], time_in_trial)
        if err is not None:
            return err

    return None


#------------------------------------------------
# This function is called when a trial ends with an error
#
def trial_error(err):
    print("   ERROR in trial: " + err.err_code + "  - " + err.message)

    sound_err.play()
    err_textbox.unload()
    err_textbox.text = err.message
    err_textbox.visible = True

    trial_ended()


#------------------------------------------------
# This function is called when a trial ends with no error
#
def trial_succeeded():

    print("   Trial ended successfully.")

    target_box.visible = False

    feedback_arrow.visible = True
    nl_pos = number_line.position
    feedback_arrow.position = (number_line.last_touched_coord + nl_pos[0], nl_pos[1] + feedback_arrow.height / 2)

    all_stimuli.present()
    sound_ok.play()

    trial_ended()


#------------------------------------------------
# This function is called whenever a trial ends - both for successful trials and for error trials
#
def trial_ended():
    target_box.visible = False
    all_stimuli["speed_guide"].activate(None)
    all_stimuli.present()



#===========================================================================================


#-- Initialize expyriment --
#---------------------------
exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#-- Initialize the objects for the number-to-position experiment --
#------------------------------------------------------------------

all_stimuli = ttrk.stimuli.StimulusContainer()
validators = []

screen_width = exp.screen.size[0]
screen_height = exp.screen.size[1]

# -- Number line
number_line = ttrk.stimuli.NumberLine((0, screen_height / 2 - 80), int(screen_width * 0.85), MAX_NUMBERLINE_VALUE,
                                      line_colour=xpy.misc.constants.C_WHITE, end_tick_height=5)
number_line.show_labels(font_name="Arial", font_size=26, box_size=(100, 30),
                        font_colour=xpy.misc.constants.C_GREY, offset=(0, 20))
all_stimuli.add("nl", number_line)

# -- Feedback arrow
feedback_arrow = create_feedback_arrow(xpy.misc.constants.C_GREEN)
all_stimuli.add("feedback_arrow", feedback_arrow, False)

# -- "Start" area
start_area = xpy.stimuli.Rectangle(size=(40, 30))
start_area.position = (0, - (screen_height / 2 - start_area.size[1] / 2))
all_stimuli.add('start', start_area)
start_point = StartPoint(start_area)

# -- Target number
target_box = xpy.stimuli.TextBox("", (300, 80), (0, screen_height / 2 - 50),
                             text_font="Arial", text_size=50, text_colour=xpy.misc.constants.C_WHITE)
all_stimuli.add("target", target_box, visible=False)

# -- Validators
validators.append(MovementAngleValidator(min_angle=-90, max_angle=90, calc_angle_interval=20, enabled=True))

global_speed_validator = GlobalSpeedValidator(origin_coord=start_area.position[1] + start_area.size[1] / 2,
                                              end_coord=number_line.position[1],
                                              grace_period=0.3, max_trial_duration=MAX_TRIAL_DURATION,
                                              milestones=[(.5, .33), (.5, .67)], show_guide=GUIDE_ENABLED)
global_speed_validator.do_present_guide = False
validators.append(global_speed_validator)
if GUIDE_ENABLED:
    all_stimuli.add("speed_guide", global_speed_validator.guide.stimulus)

#-- Sounds
sound_ok = load_sound("click.wav")
sound_err = load_sound("error.wav")

#-- Error messages
err_textbox = xpy.stimuli.TextBox("", (290, 180), (0, 0),
                                  text_font="Arial", text_size=16, text_colour=xpy.misc.constants.C_RED)
all_stimuli.add("err_box", err_textbox, visible=False)


#-- Run the experiment --
#------------------------

all_stimuli.present()

while True:
    run_trial()

xpy.control.end()
