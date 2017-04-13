"""

A simple version of the number-to-position experiment: 0-100 number line, each target appears twice

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk
from trajtracker.paradigms import num2pos


if not xpy.misc.is_android_running():
    xpy.control.defaults.window_mode = True
    ttrk.log_to_console = True


config = num2pos.Config("Num2Pos(0-100*2)", max_trial_duration=2, max_numberline_value=100,
                        speed_guide_enabled=True, data_source=range(101) * 2)

num2pos.run_full_experiment(config)
