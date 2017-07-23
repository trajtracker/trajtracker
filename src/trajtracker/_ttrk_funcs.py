"""

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

import time

import expyriment as xpy
import trajtracker as ttrk


#-------------------------------------------------
def log_write(msg, print_to_console=False):
    """
    Write a message to the log file
    
    :param msg: Text message 
    :param print_to_console: If true, print the message also to console 
    """

    # noinspection PyProtectedMember
    xpy._internals.active_exp._event_file_log(msg, 1)

    if ttrk.log_to_console or print_to_console:
        t = time.time()
        stime = time.strftime('%H:%m:%S', time.localtime(t)) + "{:.3f}".format(t % 1)[1:]
        print(stime + ": " + msg)


#-------------------------------------------------
def initialize():
    """
    Initialize TrajTracker; and initialize Expyriment by calling
    `expyriment.control.initialize() <http://docs.expyriment.org/expyriment.control.html>`_
    
    :return: Expyriment's `Experiment <http://docs.expyriment.org/expyriment.design.Experiment.html>`_ object 
    """

    exp = xpy.control.initialize()
    ttrk.env.mouse = ttrk.io.Mouse(exp.mouse)

    return exp


#-------------------------------------------------
def deprecated(func):
    # This is a decorator which can be used to mark functions
    # as deprecated. It will result in a warning being emitted
    # when the function is used.'''

    def new_func(*args, **kwargs):
        log_write("WARNING: function {:} is deprecated and may be removed in next TrajTracker versions".format(func.__name__), True)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)

    return new_func
