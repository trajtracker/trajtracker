"""

Example for using image-based validation.

The subject's goal is to move clockwise inside the ring.
The ring displayed is the image ring.bmp
The image gradient.bmp is the same shape; it is not presented, but is used for validation.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
from trajtracker.utils import get_time

import trajtracker as ttrk
from trajtracker.validators import *


xpy.control.defaults.window_mode = True
ttrk.log_to_console = True


exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#-- The ring stimulus
ring = xpy.stimuli.Picture("ring.bmp", position=(0,0))

#-- Movement validators
in_ring_validator = LocationsValidator("gradient.bmp", position=(0, 0), default_valid=True)
in_ring_validator.invalid_colors = ((255, 255, 255))

direction_validator = \
    MoveByGradientValidator("gradient.bmp", position=(0, 0), cyclic=True, max_valid_back_movement=5)
direction_validator.single_color = "B"   # use only the blue scale
direction_validator.log_level = ttrk.log_debug

#-- Messages shown to subject

messages_x = exp.screen.size[0] / 2 - 100
messages_y = exp.screen.size[1] / 2 - 50

instruction = xpy.stimuli.TextBox("Move clockwise inside the ring", size=(200, 50),
                                  position=(-messages_x, messages_y), text_font="Arial",
                                  text_size=20, text_colour=(255, 255, 255))

location_err = xpy.stimuli.TextBox("Out of ring", size=(200, 50),
                                   position=(messages_x, messages_y), text_font="Arial",
                                   text_size=20, text_colour=(255, 0, 0))

direction_err = xpy.stimuli.TextBox("Wrong direction", size=(200, 50),
                                   position=(messages_x, messages_y), text_font="Arial",
                                   text_size=20, text_colour=(255, 0, 0))


#====================================================

ring.present(update=False)
instruction.present(clear=False)

button_was_pressed = False

start_time = get_time()
time = 0

while time < 30000:  # continue for 30 seconds

    ring.present(update=False) # to clear previous stuff

    if exp.mouse.check_button_pressed(0):

        finger_pos = exp.mouse.position

        if button_was_pressed:
            # Check movement
            if in_ring_validator.update_xyt(finger_pos[0], finger_pos[1], time):
                location_err.present(update=False, clear=False)
                print("Location error")
            elif direction_validator.update_xyt(finger_pos[0], finger_pos[1], time):
                direction_err.present(update=False, clear=False)
                print("Direction error")

        else:
            # first touch: update it
            button_was_pressed = True
            in_ring_validator.reset(time)
            direction_validator.reset(time)

    else:
        # Finger lifted
        button_was_pressed = False

    instruction.present(clear=False) # Go to next frame


xpy.control.end()