"""

An example for speed & direction monitoring.

Touch the screen and move your finger around. 
The finger speed and direction is monitored.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.utils import get_time


xpy.control.defaults.window_mode = True
ttrk.log_to_console = True



#-- Initialize Expyriment
exp = xpy.control.initialize()
xpy.control.start(exp)
if not xpy.misc.is_android_running():
    exp.mouse.show_cursor()


#===========================================================================================
#              Prepare objects
#===========================================================================================

#-- monitor speed & direction
speed_monitor = ttrk.movement.SpeedMonitor(1)
direction_monitor = ttrk.movement.DirectionMonitor(min_distance=10, min_angle_change_per_curve=5)



screen_width = exp.screen.size[0]
screen_height = exp.screen.size[1]

def create_textbox(distance_from_top):
    box = xpy.stimuli.TextBox("", size=(300, 50), text_font="Arial", text_size=20,
                              text_colour=xpy.misc.constants.C_WHITE, text_justification=0)
    box.position = (-(screen_width - box.size[0]) / 2, (screen_height - box.size[1]) / 2 - distance_from_top)
    return box

tb_xspeed = create_textbox(10)
tb_yspeed = create_textbox(70)
tb_angle = create_textbox(130)
tb_curves = create_textbox(190)


#------------------------------------------------
#-- Update the information in the text boxes according to the monitors
def update_textboxes():
    tb_xspeed.unload()
    tb_yspeed.unload()
    tb_angle.unload()
    tb_curves.unload()

    tb_xspeed.text = "X Speed: {:04d} c/s".format(0 if speed_monitor.xspeed is None else int(speed_monitor.xspeed))
    tb_yspeed.text = "Y Speed: {:04d} c/s".format(0 if speed_monitor.yspeed is None else int(speed_monitor.yspeed))
    tb_angle.text = "Direction: {:03d} deg".format(0 if direction_monitor.curr_angle is None else int(direction_monitor.curr_angle))
    tb_curves.text = "Turns: {:}".format(direction_monitor.n_curves)


#------------------------------------------------
def update_display():
    tb_xspeed.present(update=False)
    tb_yspeed.present(clear=False, update=False)
    tb_angle.present(clear=False, update=False)
    tb_curves.present(clear=False)

#===========================================================================================
#              Run the task
#===========================================================================================

update_textboxes()
update_display()

speed_monitor.reset(0)
direction_monitor.reset()

start_time = get_time()
last_updated_texts_time = 0.0

while get_time() - start_time < 60:   # continue for 60 sec

    curr_time = get_time()

    if exp.mouse.check_button_pressed(0):
        #-- Finger is touching the screen

        #-- Update the monitors on each frame, so they can continuously track the speed
        #-- and direction of movement
        speed_monitor.update_xyt(exp.mouse.position[0], exp.mouse.position[1], curr_time - start_time)
        direction_monitor.update_xyt(exp.mouse.position[0], exp.mouse.position[1], curr_time - start_time)

        # Update the text information only every 100 ms (because this is time consuming)
        if get_time() - last_updated_texts_time >= 0.1:
            update_textboxes()

    else:
        #-- Finger not touching the screen
        speed_monitor.reset(0)
        direction_monitor.reset()

    update_display()
