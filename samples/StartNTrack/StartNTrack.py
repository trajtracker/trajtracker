"""

An example for a simple trajectory-tracking experiment, which demonstrates the use
of StartPoint and TrajectoryTracker classes.

Start a trial by touching the rectangle. 
Without lifting the finger, move it upwards, and drag it up to the circle.

The finger trajectory is saved to data/trajectory_##.csv

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np
import random

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.movement import StartPoint
from trajtracker.utils import get_time

xpy.control.defaults.window_mode = True
ttrk.log_to_console = True


#-- Initialize Expyriment
exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#===========================================================================================
#              Prepare stimuli
#===========================================================================================

N_TRIALS = 20

screen_width = exp.screen.size[0]
screen_height = exp.screen.size[1]

#-- The START point
start_point = ttrk.movement.RectStartPoint(size=(40, 30), position=(0, -(screen_height-30)/2))

#-- The target point that you should reach
target_point = xpy.stimuli.Circle(radius=20, colour=xpy.misc.constants.C_GREEN)
target_point.position = (-50, screen_height/2 - target_point.radius * 1.5)

#-- Message displaying no. of completed trials
progress_msg = xpy.stimuli.TextBox("Completed: 0/%d" % N_TRIALS, size=(300, 50), text_font="Arial", text_size=20,
                                   text_colour=xpy.misc.constants.C_WHITE, text_justification=2)
progress_msg.position = ((screen_width - progress_msg.size[0]) / 2, (screen_height - progress_msg.size[1]) / 2)

#-- Shows an error when the finger/mouse leaves the start point in the wrong direction
err_msg = xpy.stimuli.TextBox("Please move UPWARDS from the start point!", size=(300, 50),
                              text_font="Arial", text_size=20,
                              text_colour=xpy.misc.constants.C_RED)

#-- Tracks & saves the finger trajectory
traj_tracker = ttrk.movement.TrajectoryTracker("data/trajectory_%d.csv" % exp.subject)

#-----------------------------------------------------------
#-- Update the display.
def present_stimuli(show_error=False):

    start_point.start_area.present(update=False)

    target_point.present(clear=False, update=False)

    if show_error:
        err_msg.present(clear=False, update=False)

    progress_msg.present(clear=False)


#===========================================================================================
#              Run task
#===========================================================================================

traj_tracker.init_output_file()

present_stimuli()

n_completed = 0

while n_completed < N_TRIALS:

    start_point.reset()

    trial_start_time = get_time()
    traj_tracker.reset(trial_start_time)

    # Wait for mouse/finger to click / touch screen
    start_point.wait_until_startpoint_touched(exp)
    present_stimuli()

    # Wait for mouse/finger to start moving
    state = start_point.wait_until_exit(exp)
    if state == StartPoint.State.aborted:
        # Finger lifted (trial aborted)
        continue

    elif state == StartPoint.State.error:
        # Finger moved sideways rather than upwards: show an error message
        present_stimuli(show_error=True)
        continue

    # good! Mouse/finger started moving upwards. Now we wait for it to reach the target
    traj_tracker.enabled = True

    while True:  # The loop runs once per frame

        if not exp.mouse.check_button_pressed(0):
            # Finger lifted / mouse unclicked: abort the trial
            break

        # The mouse/finger moves

        mouse_pos = exp.mouse.position

        # save trajectory data
        traj_tracker.update_xyt(mouse_pos[0], mouse_pos[1], get_time() - trial_start_time)

        if target_point.overlapping_with_position(mouse_pos):
            n_completed += 1
            traj_tracker.save_to_file(n_completed)
            progress_msg.unload()
            progress_msg.text = "Completed: %d/%d" % (n_completed, N_TRIALS)
            present_stimuli()
            break
