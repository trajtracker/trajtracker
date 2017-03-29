"""

A simple number-to-position experiment, using the TrajTracker infra

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import csv, random
from enum import Enum
import numpy as np

import expyriment as xpy
from expyriment.misc._timer import get_time

import trajtracker as ttrk
from trajtracker.movement import StartPoint, TrajectoryTracker
from trajtracker.validators import *


MAX_TRIAL_DURATION = 2
GUIDE_ENABLED = False


class NumberLineObjects:

    def __init__(self):
        self.nl = None
        self.start_area = None
        self.target = None
        self.tracker = None
        self.trials_file = None
        self.global_speed_validator = None
        self.validators = []
        self.stimuli = ttrk.stimuli.StimulusContainer()


#------------------------------------------------
def main():

    #-- Initialize expyriment
    exp = xpy.control.initialize()
    xpy.control.start(exp)
    exp.mouse.show_cursor()  # todo: not on tablet

    #-- Initialize the number-to-position experiment
    exp_objects = prepare_objects()
    targets = load_stimuli_from_csv()

    show_instructions(exp, exp_objects.stimuli)

    #-- Show trials
    trial_num = 0
    while len(targets) > 0:
        trial_num += 1
        if run_trial(exp, trial_num, targets[0], exp_objects):
            #-- OK
            targets.pop(0)
        else:
            #-- Trial did not finish successfully
            random.shuffle(targets)

    #-- Experiment ended
    show_end_msg(exp)
    xpy.control.end()


#------------------------------------------------
def load_stimuli_from_csv():  #todo: this function should be replaced by a class

    in_file = "Number2Position.csv"
    fp = open(in_file)

    try:
        reader = csv.DictReader(fp)
        targets = [int(row['target']) for row in reader]
    finally:
        fp.close()

    print("Read {:} targets from {:}".format(len(targets), in_file))

    random.shuffle(targets)

    return targets

#------------------------------------------------
def prepare_objects():

    exp_objects = NumberLineObjects()

    screen_width = xpy._active_exp.screen.size[0]
    screen_height = xpy._active_exp.screen.size[1]

    #-- Number line
    nl = ttrk.stimuli.NumberLine((0, screen_height/2 - 80), int(screen_width*0.85), 100,
                                 line_colour=xpy.misc.constants.C_WHITE, end_tick_height=5)
    nl.show_labels(font_name="Arial", font_size=26, box_size=(100, 30),
                   font_colour=xpy.misc.constants.C_GREY, offset=(0, 20))
    exp_objects.stimuli.add('nl', nl)
    exp_objects.nl = nl

    #-- "Start" area
    start_area = xpy.stimuli.Rectangle(size=(40, 30))
    start_area.position = (0, - (screen_height/2 - start_area.size[1]/2))
    exp_objects.start_area = StartPoint(start_area)
    exp_objects.stimuli.add('start', start_area)

    #-- Target number
    exp_objects.target = xpy.stimuli.TextBox("", (300, 80), (0, screen_height/2 - 50),
                               text_font="Arial", text_size=50, text_colour=xpy.misc.constants.C_WHITE)
    exp_objects.stimuli.add("target", exp_objects.target, visible=False)

    #-- Trajectory tracker
    subj_id = xpy._active_exp.subject
    tracker = TrajectoryTracker(xpy.io.defaults.datafile_directory + "/trajectory_{:}.csv".format(subj_id))
    tracker.tracking_active = True
    tracker.init_output_file()
    exp_objects.tracker = tracker

    #-- Trials file
    exp_objects.trials_file = xpy.io.defaults.datafile_directory + "/trials_{:}.csv".format(subj_id)

    #-- Validators
    val1 = MovementAngleValidator(1, min_angle=-90, max_angle=90, calc_angle_interval=20, enabled=True)
    exp_objects.validators.append(val1)

    val2 = GlobalSpeedValidator(origin_coord=start_area.position[1] + start_area.size[1]/2,
                                end_coord=nl.position[1],
                                grace_period=0.3, max_trial_duration=MAX_TRIAL_DURATION,
                                milestones=[(.5, .33), (.5, .67)], show_guide=GUIDE_ENABLED)
    exp_objects.validators.append(val2)
    exp_objects.global_speed_validator = val2

    return exp_objects


#------------------------------------------------
def show_instructions(exp, stim_container):

    msg = "Touch the rectangle at the bottom of the screen to start a trial. " + \
          "When you start moving the finger, a target number will appear. " + \
          "Drag your finger to the position corresponding with the target number." + \
          "\n\nIf you use the mouse, start a trial by clicking on the 'start' rectangle, and " + \
          "release the mouse button only after you reach the number line." + \
          "\n\nNow, touch the screen (or click the mouse) to start the experiment."

    message_box = xpy.stimuli.TextBox(msg, (1000, 400), (0, 0),
                                      text_font="Arial", text_size=20, text_colour=xpy.misc.constants.C_WHITE)

    stim_container.present(update=False)
    message_box.present(clear=False)

    exp.mouse.wait_press()
    stim_container.present()

#------------------------------------------------
def show_end_msg(exp):

    message_box = xpy.stimuli.TextBox("Thank you for your participation.", (800, 80), (0, 0),
                                      text_font="Arial", text_size=20, text_colour=xpy.misc.constants.C_WHITE)

    message_box.present(clear=False)
    exp.mouse.wait_press()


#------------------------------------------------
# Run a single trial.
# Returns True/False to indicate whether the trial was presented properly and finished
#
def run_trial(exp, trial_num, target, exp_objects):

    print("Starting trial #{:}, target={:}".format(trial_num, target))

    #-- Initialize trial
    exp_objects.target.text = str(target)
    exp_objects.target.visible = False
    exp_objects.tracker.reset()

    time0 = get_time()
    reset_validators(exp_objects, time0)

    wait_until_touching_start_area(exp, exp_objects)
    exp_objects.stimuli.present()
    print("   Subject touched the starting point")

    err = wait_until_leaving_start_area(exp, exp_objects)
    if err != None:
        trial_error(exp_objects, trial_num, err)
        return False

    print("   Subject started moving")

    #-- Movement started
    exp_objects.target.visible = True
    exp_objects.stimuli.present()
    time_in_trial = get_time() - time0

    exp_objects.global_speed_validator.reset(time_in_trial)
    prev_finger_pos = None

    while True:

        finger_pos = exp.mouse.position
        still_touching_screen = exp.mouse.check_button_pressed(0)

        if not still_touching_screen:
            trial_error(exp_objects, trial_num,
                        ValidationFailed("finger-lifted", "Finger lifted in mid-trial", None))
            return False

        err = apply_validations(exp_objects, finger_pos, time_in_trial)
        if err is not None:
            trial_error(exp_objects, trial_num, err)
            return False

        #-- Handle movement
        if finger_pos != prev_finger_pos:

            # -- track the trajectory
            exp_objects.tracker.update_xyt(finger_pos[0], finger_pos[1], time_in_trial)

            #-- Check if the number line was reached
            if exp_objects.nl.update_xy(finger_pos[0], finger_pos[1]):
                trial_succeeded(exp_objects, trial_num)
                return True

        #-- Go to next frame
        exp_objects.stimuli.present()
        time_in_trial = get_time() - time0
        prev_finger_pos = finger_pos


#------------------------------------------------
def reset_validators(exp_objects, time0):

    for validator in exp_objects.validators:
        validator.reset(time0)

#------------------------------------------------
def apply_validations(exp_objects, pos, time):

    for validator in exp_objects.validators:
        err = validator.check_xyt(pos[0], pos[1], time)
        if err is not None:
            return err

    return None

#------------------------------------------------
def wait_until_touching_start_area(exp, exp_objects):

    state = StartPoint.State.reset
    while state != StartPoint.State.init:
        btn_id, moved, pos, rt = exp.mouse.wait_event(wait_button=True, wait_motion=False, buttons=0, wait_for_buttonup=False)
        state = exp_objects.start_area.check_xy(pos[0], pos[1])

#------------------------------------------------
def wait_until_leaving_start_area(exp, exp_objects):

    #-- Wait
    state = None
    while state not in [StartPoint.State.start, StartPoint.State.error]:
        btn_id, moved, pos, rt = exp.mouse.wait_event(wait_motion=True, buttons=0, wait_for_buttonup=True)
        if btn_id is not None:
            #-- Finger lifted up
            return False
        if moved:
            state = exp_objects.start_area.check_xy(pos[0], pos[1])

    if state == StartPoint.State.error:
        return ValidationFailed("started-sideways", "Start the trial by moving upwards, not sideways!", None)

    return  None


#------------------------------------------------
def trial_ended(exp_objects, trial_num, success_err_code):
    exp_objects.target.visible = False
    exp_objects.stimuli.present()
    #todo: write trials.csv entry

#------------------------------------------------
def trial_error(exp_objects, trial_num, err):
    print("   ERROR in trial: " + err.err_code + "  - " + err.message)
    trial_ended(exp_objects, trial_num, err.err_code)
    #todo: show error message; make it hide after some time



#------------------------------------------------
def trial_succeeded(exp_objects, trial_num):

    print("   Trial ended successfully.")
    trial_ended(exp_objects, trial_num, "OK")
    exp_objects.tracker.save_to_file(trial_num)
    #todo: show feedback arrow, play sound
    # exp_objects.stimuli["feedback_arrow"].visible = False  #todo but don't present: this will be done on the next trial


main()
