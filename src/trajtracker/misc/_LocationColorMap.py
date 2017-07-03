"""

Given a BMP image, translate a coordinate into the color code in that coordinate.

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

try:
    from scipy import misc
    scipy_loaded = True
except ImportError:
    scipy_loaded = False

import trajtracker
import trajtracker._utils as _u
from trajtracker.utils import color_rgb_to_num, color_num_to_rgb


# noinspection PyAttributeOutsideInit
class LocationColorMap(trajtracker.TTrkObject):

    #-------------------------------------------------
    def __init__(self, image, position=None, use_mapping=False, colormap=None):
        """
        Constructor - invoked when you create a new object by writing LocationColorMap()

        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param position: See :attr:`~trajtracker.misc.LocationColorMap.position`
        :param use_mapping: See :attr:`~trajtracker.misc.LocationColorMap.use_mapping`
        :param colormap: See :attr:`~trajtracker.misc.LocationColorMap.colormap`
        """
        if not scipy_loaded:
            raise ImportError("To use TrajTracker's {:} class, you must install the scipy package".format(_u.get_type_name(self)))

        super(LocationColorMap, self).__init__()

        if isinstance(image, list) and isinstance(image[0], list):
            self._image = image
            self._filename = None
        else:
            self._image = misc.imread(image, mode='RGB')
            self._filename = image

        self._height = len(self._image)
        self._width = len(self._image[0])

        self._to_tuples()
        self._find_available_colors()

        self.position = position
        self.colormap = colormap
        self._use_mapping = use_mapping


    #-------------------------------------------------
    def _find_available_colors(self):

        self._available_colors = set()

        for row in self._image:
            for cell in row:
                self._available_colors.add(cell)


    # -------------------------------------------------
    def _to_tuples(self):

        self._image = list(self._image)
        for row in range(len(self._image)):
            self._image[row] = list(self._image[row])
            for col in range(len(self._image[0])):
                self._image[row][col] = tuple(self._image[row][col])


    #====================================================================================
    #  Configure
    #====================================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The coordinate of the image provided in the constructor (middle of the image) - an (x,y) tuple/list
        If position=(a,b), then :func:`~trajtracker.misc.LocationColorMap.get_color_at` with arguments (a,b) will
        return the color of the middle of the image.
        """
        return self._position

    @position.setter
    def position(self, value):

        if value is None:
            value = (0, 0)

        _u.validate_attr_is_collection(self, "position", value, 2, 2)
        _u.validate_attr_type(self, "position[0]", value[0], numbers.Number)
        _u.validate_attr_type(self, "position[1]", value[1], numbers.Number)

        self._position = (value[0], value[1])
        self._log_property_changed("position")

        #-- Find top-left coordinates. The rounding is done in the same way as Expyriment does.
        self._top_left_x = value[0] - int(np.floor((self._width-1)/2))
        self._top_left_y = value[1] - int(np.floor((self._height-1)/2))


    #-------------------------------------------------
    @property
    def use_mapping(self):
        """
        The default value of the 'use_mapping' argument in get_color_at()

        :type: bool
        """
        return self._use_mapping

    @use_mapping.setter
    def use_mapping(self, value):
        _u.validate_attr_type(self, "use_mapping", value, bool)
        self._use_mapping = value
        self._log_property_changed("use_mapping")


    #-------------------------------------------------
    @property
    def colormap(self):
        """
        Mapping of each color in the image to another value. This mapping will be used when calling get_color_at(use_mapping=True)

        Valid values:

        - None (default): no mapping; calling get_color_at(use_mapping=True)
        - "RGB": Each color is assigned the RGB code - a number between 0 and 65535 (0xFFFFFF)
        - "DEFAULT": Each color is assigned a unique code (0, 1, 2, etc.). Codes are assigned by order of RGB codes.
        - or a dictionary that maps each color in the image (RGB tuple) to a value
        """
        return self._color_to_code

    @colormap.setter
    def colormap(self, value):

        if value is None:
            #-- No mapping: use default colors
            self._color_to_code = None

        elif isinstance(value, str) and value.lower() == "default":
            #-- Use arbitrary coding
            self._color_to_code = {}
            n = 0
            for color in sorted(list(self._available_colors)):
                self._color_to_code[color] = n
                n += 1

        elif isinstance(value, str) and value.lower() == "rgb":
            # Translate each triplet to an RGB code
            self._color_to_code = { color: color_rgb_to_num(color) for color in self._available_colors }

        elif isinstance(value, dict):
            #-- Use this mapping; but make sure that all colors from the image were defined
            missing_colors = set()
            for color in self._available_colors:
                if color not in value:
                    missing_colors.add(color)
            if len(missing_colors) > 0:
                raise trajtracker.ValueError("Invalid value for {:}.color_codes - some colors are missing: {:}".format(
                    _u.get_type_name(self), missing_colors))

            self._color_to_code = value.copy()

        elif isinstance(value, type(lambda:1)):
            #-- A function that maps each color to a code
            self._color_to_code = { color: value(color) for color in self._available_colors }

        else:
            raise trajtracker.ValueError(
                "{:}.color_codes can only be set to None, 'default', or a dict. Invalid value: {:}".format(
                    _u.get_type_name(self), value))

        self._log_property_changed("colormap", value)


    #====================================================================================
    #  Access colors
    #====================================================================================

    #-------------------------------------------------
    @property
    def available_colors(self):
        """
        Return a set with all colors that exist in the image
        """
        return frozenset(self._available_colors)


    #-------------------------------------------------
    def get_color_at(self, x_coord, y_coord, use_mapping=None):
        """
        Return the color at a given coordinate

        :param x_coord:
        :param y_coord:
        :param use_mapping:
        :return: The color in the given place, or None if the coordinate is out of the image range
        """

        _u.validate_func_arg_type(self, "get_color_at", "x_coord", x_coord, int)
        _u.validate_func_arg_type(self, "get_color_at", "y_coord", y_coord, int)
        _u.validate_func_arg_type(self, "get_color_at", "use_mapping", use_mapping, numbers.Number, none_allowed=True)

        if use_mapping is None:
            use_mapping = self._use_mapping

        if self._color_to_code is None and use_mapping:
            raise trajtracker.ValueError("a call to %s.get_color_at(use_mapping=True) is invalid because color_codes were not specified" % self.__class__)

        if x_coord < self._top_left_x or x_coord >= self._top_left_x+self._width or \
               y_coord < self._top_left_y or y_coord >= self._top_left_y + self._height:
            return None

        x_coord -= self._top_left_x
        y_coord -= self._top_left_y
        #y_coord = len(self._image) - 1 - y_coord   # reverse up/down

        v = self._image[-(y_coord+1)][x_coord]

        return self._color_to_code[v] if use_mapping else v
