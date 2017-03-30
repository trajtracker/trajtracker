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



xpy.control.defaults.window_mode = True
xpy.control.defaults.goodbye_text = "Thank you for your participation"


MAX_TRIAL_DURATION = 2
GUIDE_ENABLED = False

TRIAL_NUM = "@@TrialNumber@@"


class NumberLineObjects:

    def __init__(self):
        self.nl = None
        self.start_area = None
        self.target = None
        self.tracker = None
        self.trials_file = None
        self.trials_writer = None
        self.global_speed_validator = None
        self.validators = []
        self.stimuli = ttrk.stimuli.StimulusContainer()


global_inf = {}

#------------------------------------------------
def main():

    #-- Initialize expyriment
    exp = xpy.control.initialize()
    xpy.control.start(exp)
    exp.mouse.show_cursor()  # todo: not on tablet

    #-- Initialize the number-to-position experiment
    exp_objects = prepare_objects(exp)
    trials = load_trials_from_csv()

    show_instructions(exp, exp_objects.stimuli)

    global_inf['session_start_time'] = get_time()

    #-- Show trials
    trial_num = 1
    while len(trials) > 0:
        trials[0][TRIAL_NUM] = trial_num
        go_to_next_stim, increase_trial_num = run_trial(exp, trials[0], exp_objects)

        if increase_trial_num:
            trial_num += 1

        if go_to_next_stim:
            trials.pop(0)
        else:
            random.shuffle(trials)

    #-- Experiment ended
    exp_objects.trials_fp.close()
    xpy.control.end()


#------------------------------------------------
def load_trials_from_csv():

    in_file = "Number2Position.csv"

    loader = ttrk.data.CSVLoader()
    trials = loader.load_file(in_file)
    print("Read {:} trials from {:}".format(len(trials), in_file))

    random.shuffle(trials)

    return trials


#------------------------------------------------
def prepare_objects(exp):

    exp_objects = NumberLineObjects()

    screen_width = xpy._active_exp.screen.size[0]
    screen_height = xpy._active_exp.screen.size[1]

    #-- Number line
    nl = ttrk.stimuli.NumberLine((0, screen_height/2 - 200), int(screen_width*0.85), 100,
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

    exp._event_file_log("Setup,start_area,pos={:},size={:}".format(start_area.position, start_area.size), 1)

    #-- Target number
    target = xpy.stimuli.TextBox("", (300, 80), (0, screen_height/2 - 50),
                                 text_font="Arial", text_size=50, text_colour=xpy.misc.constants.C_WHITE)
    exp_objects.target = target
    exp_objects.stimuli.add("target", exp_objects.target, visible=False)
    exp._event_file_log("Setup,target_number,pos={:},size={:},font={:},text_size={:}".format(
        target.position, target.size, target.text_font, target.text_size), 1)

    #-- Trajectory tracker
    subj_id = xpy._active_exp.subject
    tracker = TrajectoryTracker(xpy.io.defaults.datafile_directory + "/trajectory_{:}.csv".format(subj_id))
    tracker.tracking_active = True
    tracker.init_output_file()
    exp_objects.tracker = tracker

    #-- Trials file
    exp_objects.trials_file = xpy.io.defaults.datafile_directory + "/trials_{:}.csv".format(subj_id)
    exp._event_file_log("Setup,trials_file,{:}".format(exp_objects.trials_file), 1)

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
def show_instructions(exp, stim_container): #TODO: have a generic function for this? in utils perhaps?

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
# Run a single trial.
# Returns True/False to indicate whether the trial was presented properly and finished
#
def run_trial(exp, trial, exp_objects):

    trial_info = {}

    target = trial['target']
    print("Starting trial #{:}, target={:}".format(trial[TRIAL_NUM], target))

    #-- Initialize trial

    exp_objects.start_area.reset()
    exp_objects.nl.reset()

    exp_objects.target.visible = False
    exp_objects.target.unload()
    exp_objects.target.text = target
    exp_objects.target.preload()

    exp_objects.tracker.reset()

    reset_validators(exp_objects, 0)

    #-- Wait for the participant to initiate the trial

    exp_objects.start_area.wait_until_touched(exp, exp_objects.stimuli)
    print("   Subject touched the starting point")

    exp_objects.stimuli.present()
    time0 = get_time()

    reset_validators(exp_objects, time0)
    trial_info['time_in_session'] = time0 - global_inf['session_start_time']

    #-- Wait for the participant to start moving the finger

    rc = exp_objects.start_area.wait_until_exit(exp, on_loop=exp_objects.stimuli)
    if rc == StartPoint.State.aborted:
        print("   Trial aborted.")
        return False, False  # finger lifted
    elif rc == StartPoint.State.error:
        trial_error(exp_objects, trial, trial_info, 0,
                    ValidationFailed("started-sideways", "Start the trial by moving upwards, not sideways!", None))
        return False, True

    trial_info['time_started_moving'] = get_time() - time0

    print("   Subject started moving")

    #-- Movement started: initialize stuff
    exp_objects.target.visible = True
    exp_objects.stimuli.present()
    time_in_trial = get_time() - time0
    trial_info['time_target_shown'] = time_in_trial

    #-- Trial loop

    exp_objects.global_speed_validator.reset(time_in_trial)
    prev_finger_pos = None

    while True:

        finger_pos = exp.mouse.position
        still_touching_screen = exp.mouse.check_button_pressed(0)

        if not still_touching_screen:
            trial_error(exp_objects, trial, trial_info, time_in_trial,
                        ValidationFailed("finger-lifted", "Finger lifted in mid-trial", None))
            return False, True

        err = apply_validations(exp_objects, finger_pos, time_in_trial)
        if err is not None:
            trial_error(exp_objects, trial, trial_info, time_in_trial, err)
            return False, True

        #-- Handle movement
        if finger_pos != prev_finger_pos:

            # -- track the trajectory
            exp_objects.tracker.update_xyt(finger_pos[0], finger_pos[1], time_in_trial)

            #-- Check if the number line was reached
            if exp_objects.nl.update_xy(finger_pos[0], finger_pos[1]):
                trial_succeeded(exp_objects, trial, trial_info, time_in_trial)
                return True, True

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
def trial_ended(exp_objects, trial, trial_info, end_time, success_err_code):
    exp_objects.target.visible = False
    exp_objects.stimuli.present()

    endpoint = exp_objects.nl.last_touched_value

    #-- Save data to trials file
    trial_data = {
        'trialNum': trial[TRIAL_NUM],
        'LineNum': trial[ttrk.data.CSVLoader.FLD_LINE_NUM],
        'target': trial['target'],
        'presentedTarget': trial['target'],
        'endPoint': "" if endpoint is None else "{:.3g}".format(endpoint),
        'status' : success_err_code,
        'movementTime' : 0 if end_time == 0 else "{:.3f}".format(end_time - trial_info['time_target_shown']),
        'timeInSession': "{:.3f}".format(trial_info['time_in_session']),
        'timeUntilFingerMoved': "{:.3f}".format(trial_info['time_started_moving']),
        'timeUntilTarget': "{:.3f}".format(trial_info['time_target_shown']),
    }

    if exp_objects.trials_writer is None:
        fields = ['trialNum', 'LineNum', 'target', 'presentedTarget', 'status', 'endPoint', 'movementTime',
                  'timeInSession', 'timeUntilFingerMoved', 'timeUntilTarget']
        exp_objects.trials_fp = open(exp_objects.trials_file, 'w')
        exp_objects.trials_writer = csv.DictWriter(exp_objects.trials_fp, fields)
        exp_objects.trials_writer.writeheader()

    exp_objects.trials_writer.writerow(trial_data)
    exp_objects.trials_fp.flush()


#------------------------------------------------
def trial_error(exp_objects, trial, trial_info, end_time, err):
    print("   ERROR in trial: " + err.err_code + "  - " + err.message)
    trial_ended(exp_objects, trial, trial_info, end_time, err.err_code)
    #todo: show error message; make it hide after some time (or when clicking anywhere)


#------------------------------------------------
def trial_succeeded(exp_objects, trial, trial_info, end_time):

    print("   Trial ended successfully.")
    trial_ended(exp_objects, trial, trial_info, end_time, "OK")

    exp_objects.tracker.save_to_file(trial[TRIAL_NUM])

    #todo: show feedback arrow, play sound
    # exp_objects.stimuli["feedback_arrow"].visible = False  #todo but don't present: this will be done on the next trial


main()
