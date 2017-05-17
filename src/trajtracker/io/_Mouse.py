"""
The TrajTracker interface for the mouse input device

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import trajtracker
import trajtracker._utils as  _u


class Mouse(trajtracker.TTrkObject):

    #-----------------------------------------------------
    def __init__(self, xpy_mouse):
        """
        Create a Mouse object
        
        :param xpy_mouse: Expyriment's mouse object (from  
        """
        super(Mouse, self).__init__()
        self._xpy_mouse = xpy_mouse


    #-----------------------------------------------------
    def check_button_pressed(self, button_number):
        """
        Check whether a mouse button is currently pressed.
        
        :param button_number: 0 = main (left) button 
        :return: bool
        """
        return self._xpy_mouse.check_button_pressed(button_number)

    # -----------------------------------------------------
    def show_cursor(self, show):
        """
        Show/hide the mouse pointer

        :param: show
        :type show: bool 
        """
        _u.validate_func_arg_type(self, "show_cursor", "show", show, bool)
        if show:
            self._xpy_mouse.show_cursor()
        else:
            self._xpy_mouse.hide_cursor()


    #-----------------------------------------------------
    @property
    def position(self):
        """
        Get the current position of the mouse pointer
        
        :return: (x, y) coordinates 
        """
        return self._xpy_mouse.position
