"""
A feedback arrow for the number-line experiments

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy


class FeedbackArrow(xpy.stimuli.Shape):

    def __init__(self, colour=xpy.misc.constants.C_GREEN):
        super(FeedbackArrow, self).__init__()
        # noinspection PyTypeChecker
        self.add_vertices([(10, 20), (-6, 0), (0, 20), (-9, 0), (0, -20), (-6, 0)])
        self.colour = colour

