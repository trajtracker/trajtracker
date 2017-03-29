"""

A simple number-to-position experiment, using the TrajTracker infra

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np

import expyriment as xpy
import trajtracker as ttrk


#------------------------------------------------
def load_stimuli_from_csv():
    pass


#------------------------------------------------
def prepare_experiment():

    data_dir = xpy.io.defaults.datafile_directory

    pass


#------------------------------------------------
def prepare_screen():

    nl = ttrk.stimuli.NumberLine()

    pass


def main():
    exp = xpy.control.initialize()


    xpy.control.start(exp)
    exp.mouse.hide_cursor()

    xpy.stimuli.BlankScreen().present()

    # trial loop


    xpy.control.end()



main()
