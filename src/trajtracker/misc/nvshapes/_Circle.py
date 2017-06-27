"""
Non-visual circle

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

import trajtracker as ttrk
import trajtracker._utils as _u


class Circle(object):
    def __init__(self, x, y, radius):
        """
        Constructor - invoked when you create a new object by writing Circle()

        :param x: the circle's center
        :param y: the circle's center
        :param radius:
        """

        _u.validate_func_arg_type(self, "__init__", "x", x, int)
        _u.validate_func_arg_type(self, "__init__", "y", y, int)
        _u.validate_func_arg_type(self, "__init__", "radius", radius, int)
        _u.validate_func_arg_positive(self, "__init__", "radius", radius)
        self.x = x
        self.y = y
        self.radius = radius


    #-------------------------------------------------
    def overlapping_with_position(self, pos):
        x, y = pos
        distance_from_center = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return distance_from_center <= self.radius


    #-------------------------------------------------
    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, value):
        _u.validate_attr_type(self, "position", value, ttrk.TYPE_COORD)
        self.x = value[0]
        self.y = value[1]


    #-------------------------------------------------
    def __str__(self):
        return "NV-Circle(radius={:}, position={:})".format(self.radius, (self.x, self.y))
