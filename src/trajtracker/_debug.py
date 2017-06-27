"""

TrajTracker - utilities for debugging

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

This file is part of TrajTracker.

TrajTracker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TrajTracker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TrajTracker.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np

import expyriment as xpy
import trajtracker as ttrk


#----------------------------------------------------------------------------------------
def print_is_preloaded(stim_id, visual_obj):
    """
    Print whether a stimulus (and all its contained stimuli) is preloaded or not
    
    :param stim_id: The ID of the visual object (just for printing) 
    :param visual_obj: The visual object
    """

    if "is_preloaded" in dir(visual_obj):
        print("Stimulus {:} is {:}preloaded".format(stim_id, "" if visual_obj.is_preloaded else "not "))

    elif isinstance(visual_obj, ttrk.stimuli.StimulusContainer):
        for inner_id, stim in visual_obj._stimuli.items():
            print_is_preloaded(stim_id + "." + str(inner_id), stim['stimulus'])

    elif isinstance(visual_obj, ttrk.stimuli.StimulusSelector):
        for inner_id, stim in visual_obj._stimuli.items():
            print_is_preloaded(stim_id + "." + str(inner_id), stim)

    elif isinstance(visual_obj, ttrk.stimuli.BaseMultiStim):
        stimuli = visual_obj._stimuli
        for i in range(len(stimuli)):
            print_is_preloaded("{:}#{:}".format(stim_id, i), stimuli[i])

    elif isinstance(visual_obj, ttrk.stimuli.NumberLine):
        if visual_obj._canvas is None:
            print("Stimulus {:} is not preloaded".format(stim_id))
        else:
            print_is_preloaded(stim_id, visual_obj._canvas)

    else:
        print("No preload info for {:}".format(stim_id))
