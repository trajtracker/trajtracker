"""
The TrajTracker interface for the mouse input device

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
