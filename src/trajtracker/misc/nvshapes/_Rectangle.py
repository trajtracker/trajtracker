"""
Non-visual rectangle

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

from __future__ import division

import numbers
import numpy as np

import trajtracker as ttrk
import trajtracker._utils as _u


class Rectangle(object):

    #---------------------------------------------------
    @staticmethod
    def clone(rect):
        """
        Clone an existing rectangle 
        :param rect: A rectangle object (can also be an Expyriment rectangle)
        """
        rotation = rect.rotation if "rotation" in dir(rect) else 0
        return Rectangle(size=rect.size, position=rect.position, rotation=rotation)


    #---------------------------------------------------
    def __init__(self, size, position=(0, 0), rotation=0):
        """
        Constructor - invoked when you create a new object by writing Rectangle()

        :param size: the rectangle's size (width, height)
        :param position: the rectangle's center (x, y)
        :param rotation: Its rotation (0=straight; positive=clockwise)
        """

        self.size = size
        self.position = position
        self.rotation = rotation


    #---------------------------------------------------
    def overlapping_with_position(self, pos):

        _u.validate_func_arg_is_collection(self, "overlapping_with_position", "pos", pos, 2, 2)
        _u.validate_func_arg_type(self, "overlapping_with_position", "pos[0]", pos[0], numbers.Number)
        _u.validate_func_arg_type(self, "overlapping_with_position", "pos[1]", pos[1], numbers.Number)

        x = pos[0] - self._position[0]
        y = pos[1] - self._position[1]

        height = self._size[1]
        width = self._size[0]

        if self._rotation != 0:
            #-- Instead of rotating the rectangle - rotate the point in the opposite direction

            # Get the point's position relatively to the rectangle's center as r, alpha.
            # alpha=0 means that the point is to the right of the rectangle center
            r = np.sqrt(x ** 2 + y ** 2)
            if (x == 0):
                alpha = np.pi/2 if y > 0 else np.pi*3/2
            else:
                alpha = np.arctan(y / x)

            alpha += self._rotation_radians

            x = np.cos(alpha) * r
            y = np.sin(alpha) * r

        return - (width / 2) <= x <= width / 2 and - (height / 2) <= y <= height / 2

    #-----------------------------------------------------
    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        _u.validate_attr_is_coord(self, "size", value)
        _u.validate_attr_positive(self, "size[0]", value[0])
        _u.validate_attr_positive(self, "size[1]", value[1])
        self._size = (value[0], value[1])


    #-----------------------------------------------------
    def extend(self, extend_by):
        """
        Extend the rectangle by the given value
        
        :param extend_by: If a pair of values, the mean (w, h): extend the rectangle's width by w and its height by h.
                          If this is a single value, it is used for extending the width as well as the height.
        """

        if isinstance(extend_by, numbers.Number):
            extend_by = extend_by, extend_by
        else:
            _u.validate_func_arg_type(self, "extend", "extend_by", extend_by, ttrk.TYPE_SIZE)

        self.size = self._size[0] + extend_by[0], self._size[1] + extend_by[1]


    #-----------------------------------------------------
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        _u.validate_attr_is_coord(self, "position", value, allow_float=True)
        self._position = (value[0], value[1])


    #-------------------------------------------------
    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        _u.validate_attr_numeric(self, "rotation", value)
        value = value % 360
        self._rotation = value
        self._rotation_radians = value / 180 * np.pi


    #-------------------------------------------------
    def __str__(self):
        return "NV-Rectangle(size={:}, position={:}, rotation={:})".format(self._size, self._position, self._rotation)
