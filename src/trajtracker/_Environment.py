"""
Contains environment data (trajtracker.env)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy


class Environment(object):

    #------------------------------------------
    def __init__(self):
        self._mouse = None
        self._default_log_level = 4

    #------------------------------------------
    @property
    def mouse(self):
        """
        Provides access to the mouse.
        
        TrajTracker will always access the mouse (position and button presses) via this object.
        By default, this object is a :class:`~trajtracker.io.Mouse`, which connects with your computer's mouse.
        You can replace this object by another class (with the same interface) in order to use 
        alternative input source.
        """
        return self._mouse

    @mouse.setter
    def mouse(self, value):
        self._mouse = value


    #------------------------------------------
    @property
    def default_log_level(self):
        """
        The default logging level for all trajtracker objects.
        If you change this, only objects created from now on will be affected.
        
        :type: one of the log_xxx constants defined in the "trajtracker" module 
        """
        return self._default_log_level

    @default_log_level.setter
    def default_log_level(self, value):
        if not isinstance(value, int):
            raise Exception("trajtracker error: Invalid default_log_level ({:})".format(value))
        self._default_log_level = value


    #------------------------------------------
    # noinspection PyProtectedMember
    @property
    def screen_size(self):
        """
        Get the screen size (width, height)
        """
        if xpy._internals is None or xpy._internals.active_exp is None or xpy._internals.active_exp.screen is None:
            return None
        else:
            return xpy._internals.active_exp.screen.size
