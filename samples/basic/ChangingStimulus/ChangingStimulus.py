"""

An example for using the "StimulusSelector" class:

A dot moves in a trajectory using a StimulusAnimator, and its color changes every now and then.
The StimulusAnimator expects a single stimulus. By using a StimulusSelector, we can have 
several underlying stimuli and switch them occasionally, all this without the StimulusAnimator
knowing that it's actually moving several stimuli.  

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np
import random

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.utils import get_time

xpy.control.defaults.window_mode = True
ttrk.log_to_console = True


#-- Initialize Expyriment
xpy.control.set_develop_mode(1)
exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#===========================================================================================
#              Prepare stimuli
#===========================================================================================

#-- Create stimuli
selector = ttrk.stimuli.StimulusSelector()
selector.add_stimulus("red", xpy.stimuli.Circle(radius=10, colour=xpy.misc.constants.C_RED))
selector.add_stimulus("green", xpy.stimuli.Circle(radius=10, colour=xpy.misc.constants.C_GREEN))

#-- Move them in circles
path_generator = ttrk.movement.CircularTrajectoryGenerator(center=(0,0), radius=200, full_rotation_duration=5)
animator = ttrk.movement.StimulusAnimator(animated_object=selector, trajectory_generator=path_generator)


#===========================================================================================
#              Run the example
#===========================================================================================

red = True
selector.activate("red")


start_time = get_time()
last_color_change_time = start_time

#-- This loop runs once per frame
while get_time() - start_time < 30:  # continue for 30 seconds

    #-- Change color in random times
    if get_time() - last_color_change_time > (0.5 + 2 * random.random()):
        red = not red
        selector.activate("red" if red else "green")
        last_color_change_time = get_time()

    #-- Move the stimulus
    animator.update(get_time() - start_time)

    #-- Update the display
    selector.present()

    xpy.io.Keyboard.process_control_keys()

xpy.control.end()
