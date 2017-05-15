"""
A + shaped fixation

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy
import trajtracker as ttrk


def FixationCross(radius):

    fixation = xpy.stimuli.Canvas((radius*2+1, radius*2+1))

    h_line = xpy.stimuli.Line((-radius, 0), (radius, 0), line_width=2, colour=xpy.misc.constants.C_WHITE)
    v_line = xpy.stimuli.Line((0, -radius), (0, radius), line_width=2, colour=xpy.misc.constants.C_WHITE)
    h_line.plot(fixation)
    v_line.plot(fixation)

    return fixation
