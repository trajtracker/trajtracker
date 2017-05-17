"""

An example for how to animate a shape along a predefined path.

The program presents a white square moving.
When you touch the screen, a green circle appears; you can drag the circle, and you need to "catch" 
the square.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
from trajtracker.utils import get_time
from expyriment.misc.geometry import XYPoint

import trajtracker as ttrk
from trajtracker.movement import *


xpy.control.defaults.window_mode = False
ttrk.log_to_console = True

#===========================================================================================
#              Prepare stimuli
#===========================================================================================

# The object that moves: a rectangle
square = xpy.stimuli.Rectangle(size=(10, 10), colour=(255,255,255))

#-- The movement path (shaped like a rotated 8; it's composed of two straight lines and two half-circles)
#-- The generator can tell the shape's (x,y) coordinates for each given time point
path_generator = SegmentedTrajectoryGenerator(cyclic=True)
path_generator.add_segment(LineTrajectoryGenerator(start_point=(-200, 100), end_point=(200, -100), duration=1), duration=1)
path_generator.add_segment(CircularTrajectoryGenerator(center=(200, 0), radius=100, full_rotation_duration=2, degrees_at_t0=180, clockwise=False), duration=1)
path_generator.add_segment(LineTrajectoryGenerator(start_point=(200, 100), end_point=(-200, -100), duration=1), duration=1)
path_generator.add_segment(CircularTrajectoryGenerator(center=(-200, 0), radius=100, full_rotation_duration=2, degrees_at_t0=180), duration=1)

#-- The "animator" object moves the rectangle along the path defined above
animator = ttrk.movement.StimulusAnimator(animated_object=square, trajectory_generator=path_generator)

#-- The circle will follows the finger/mouse
circle = xpy.stimuli.Circle(radius=20, colour=(0,255,0))

#-- This text will appear whenever the circle "catches" the square
msg = xpy.stimuli.TextBox("Good!", (100, 50), (-300, 200), text_font="Arial", text_size=20,
                          text_colour=(0, 255, 0))
MAX_DISTANCE_FOR_POSITIVE_FEEDBACK = 50


#===========================================================================================
#              Run the example
#===========================================================================================

#-- Initialize Expyriment
exp = ttrk.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()

#-- This loop runs once per frame
start_time = get_time()
while get_time() - start_time < 30:  # continue the game for 30 seconds

    #-- Move the square
    animator.update(get_time() - start_time)

    # Stimuli are redrawn on every frame. The first stimulus that we present will clear the screen -
    # this is done by calling stim.present(clear=True).
    # For the remaining stimuli, we will call stim.present(clear=False).
    # i.e. we should remember whether we already cleared the screen or not
    screen_cleared = False

    #-- If the finger is touching the screen, display the circle in the finger's position
    if ttrk.env.mouse.check_button_pressed(0):
        circle.position = ttrk.env.mouse.position
        circle.present(update=False)   # this updates the circle position, but doesn't update the display yet
        screen_cleared = True

        # if circle and square are close to each other, display the "Good!" message
        if XYPoint(xy=circle.position).distance(XYPoint(xy=square.position)) <= MAX_DISTANCE_FOR_POSITIVE_FEEDBACK:
            msg.present(clear=False, update=False)

    square.present(clear=not screen_cleared) # update the square's position; and update the display (wait 1 frame)

    xpy.io.Keyboard.process_control_keys()

xpy.control.end()
