"""

TrajTracker - movement package - public utilities

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

import decimal
import numbers

import numpy as np
# noinspection PyProtectedMember
from expyriment.misc import _timer as xpy_timer
from expyriment.misc import geometry, find_font
from pygame import freetype
from pygame.ftfont import Font

# noinspection PyProtectedMember
from trajtracker._utils import is_collection, _is_rgb
from trajtracker import ValueError


#--------------------------------------------------------------------------
def get_angle(xy1, xy2, as_degrees=False):
    """
    Get the direction of finger movement, in radians. 0 = upwards.

    :param xy1: Coordinates in time point #1
    :param xy2: Coordinates in a later time point
    :param as_degrees: Whether the angle should be returned as degrees or radians
    :type as_degrees: bool
    """

    dx = xy2[0] - xy1[0]
    dy = xy2[1] - xy1[1]

    if dx == 0:
        # up=0, down=pi
        angle = 0 if dy > 0 else np.pi

    elif dx > 0:
        # Right movement; return angles from 0 to pi
        angle = np.arctan(- dy / dx) + np.pi / 2

    else:
        # Left movement; return angles from pi to pi*2
        angle = np.arctan(- dy / dx) + np.pi * 3 / 2


    if as_degrees:
        angle *= 360 / (np.pi*2)

    return angle


#--------------------------------------------------------------------------
def color_rgb_to_num(rgb):
    """
    Convert an RGB color (3 integers, each 0-255) to a single int value (between 0 and 0xFFFFFF)
    """
    if not is_rgb(rgb):
        raise ValueError("invalid argument to color_rgb_to_num(), expecting a 3*integer list/tuple")
    return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]


def color_num_to_rgb(value):
    """
    Convert an int value (between 0 and 0xFFFFFF) to RGB color (3 integers, each 0-255)
    """
    if isinstance(value, int) and 0 <= value <= 0xFFFFFF:
        return int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256
    else:
        raise ValueError("invalid argument to color_num_to_rgb(), expecting a 3*integer list/tuple")


#--------------------------------------------------------------------------
def is_rgb(rgb):
    """
    Check if the given value is a valid RGB color (3 integers, each 0-255)
    """
    return _is_rgb(rgb)


#--------------------------------------
# noinspection PyIncorrectDocstring
def is_coord(value, allow_float=False):
    """
    Check whether the given value is valid as (x,y) coordinates
    :param allow_float: 
    """

    if isinstance(value, geometry.XYPoint):
        return True

    if not is_collection(value) or len(value) != 2:
        return False

    elem_type = numbers.Number if allow_float else int
    return isinstance(value[0], elem_type) and isinstance(value[1], elem_type)


#--------------------------------------------------------------------------
def rotate_coord(coord, angle, origin=(0, 0), is_radians=False):
    """
    Rotate the given coordinate about the origin

    :param coord: The x,y coordinate to rotate
    :param angle: The rotation angle (positive = clockwise)
    :param origin: The point to rotate around (default=0,0)
    :param is_radians: whether angle is provided as radians (True) or degrees (False)
    :return: The new x,y coordinates
    """

    if not is_radians:
        angle = angle / 360 * np.pi*2

    x = coord[0] - origin[0]
    y = coord[1] - origin[1]

    x1 = x * np.cos(angle) + y * np.sin(angle)
    y1 = y * np.cos(angle) - x * np.sin(angle)

    return x1 + origin[0], y1 + origin[1]


#--------------------------------------------------------------------------
def get_time():
    """
    Get the current time (in seconds).
    This is a wrapper to Expyriment's get_time function
    :return: float
    """
    return xpy_timer.get_time()


#--------------------------------------------------------------------------
def get_font_height_to_size_ratio(font_name):
    """
    Find the ratio between a font size and the corresponding textbox height in pixels.
    The returned ratio is height/size
    
    :type font_name: str 
    """

    freetype.init()
    font = Font(find_font(font_name), size=100)
    size = font.size("hfbpqgXQ,")
    return size[1] / 100.0


#--------------------------------------------------------------------------
# noinspection PyShadowingBuiltins
def round(x):
    """
    Round deicmal numbers to the nearest integer. This is different from Python's numpy.round()
    in two ways:
    
    - Python rounds halves to the nearest even number (2.5 rounds to 2, and 3.5 rounds to 4).
      This method rounds halves to the higher integer, as done in most programming languages:
      round(2.5) == 3, round(3.5) == 4, round(-2.5) == -3
    - Python's round() method returns a float, this method returns an int
    """
    return int(decimal.Decimal(x).to_integral(decimal.ROUND_HALF_UP))
