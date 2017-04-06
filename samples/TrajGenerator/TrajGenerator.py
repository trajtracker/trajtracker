"""

An example for an experiment with movement generation:

Present a white square moving; you need to catch it with your finger/mouse, which is shown
as a green circle.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
from trajtracker.utils import get_time
from expyriment.misc.geometry import XYPoint

import trajtracker as ttrk
from trajtracker.movement import *


xpy.control.defaults.window_mode = False
ttrk._TTrkObject.log_to_console = True

MAX_DISTANCE_FOR_POSITIVE_FEEDBACK = 50

#===========================================================================================

#----- A white square that moves in circles

# The object that moves
square = xpy.stimuli.Rectangle(size=(10, 10), colour=(255,255,255))

# The movement path
generator = SegmentedTrajectoryGenerator(cyclic=True)
generator.add_segment(LineTrajectoryGenerator(start_point=(-200, 100), end_point=(200, -100), duration=1), duration=1)
generator.add_segment(CircularTrajectoryGenerator(center=(200, 0), radius=100, full_rotation_duration=2, degrees_at_t0=180, clockwise=False), duration=1)
generator.add_segment(LineTrajectoryGenerator(start_point=(200, 100), end_point=(-200, -100), duration=1), duration=1)
generator.add_segment(CircularTrajectoryGenerator(center=(-200, 0), radius=100, full_rotation_duration=2, degrees_at_t0=180), duration=1)

# The animator moves the object according to the path
animator = ttrk.movement.StimulusAnimator(animated_object=square, trajectory_generator=generator)


#----- A second shape follows the finger/mouse
circle = xpy.stimuli.Circle(radius=20, colour=(0,255,0))


msg = xpy.stimuli.TextBox("Good!", (100, 50), (-300, 200), text_font="Arial", text_size=20,
                          text_colour=(0, 255, 0))


#===========================================================================================

exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


start_time = get_time()


while get_time() - start_time < 30000:  # continue for 30 seconds

    animator.update(get_time() - start_time)

    screen_cleared = False

    if exp.mouse.check_button_pressed(0):
        circle.position = exp.mouse.position
        circle.present(update=False)
        screen_cleared = True

        # check if circle and square are close enough
        if XYPoint(xy=circle.position).distance(XYPoint(xy=square.position)) <= MAX_DISTANCE_FOR_POSITIVE_FEEDBACK:
            msg.present(clear=False, update=False)


    square.present(clear=not screen_cleared)


xpy.control.end()