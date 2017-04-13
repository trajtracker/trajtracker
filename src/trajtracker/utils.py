"""

TrajTracker - movement package - public utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division
from numpy import pi
import numpy as np

from expyriment.misc import _timer as xpy_timer

#--------------------------------------------------------------------------
def get_angle(xy1, xy2, as_degrees=False):
    """
    Get the direction of finger movement, in radians. 0 = upwards.

    :param xy1: Coordinates in time point #1
    :param xy2: Coordinates in a later time point
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
        raise trajtracker.ValueError("invalid argument to color_rgb_to_num(), expecting a 3*integer list/tuple")
    return (rgb[0]<<16) + (rgb[1]<<8) + rgb[2]


def color_num_to_rgb(value):
    """
    Convert an int value (between 0 and 0xFFFFFF) to RGB color (3 integers, each 0-255)
    """
    if isinstance(value, int) and 0 <= value <= 0xFFFFFF:
        return (int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256)
    else:
        raise trajtracker.ValueError("invalid argument to color_num_to_rgb(), expecting a 3*integer list/tuple")


#--------------------------------------------------------------------------
def is_rgb(rgb):
    """
    Check if the given value is a valid RGB color (3 integers, each 0-255)
    """
    try:
        return isinstance(rgb, (list, tuple, np.ndarray)) and len(rgb) == 3 \
               and 0 <= rgb[0] <= 255 and 0 <= rgb[1] <= 255 and 0 <= rgb[2] <= 255
    except:
        return False


#--------------------------------------------------------------------------
def rotate_coord(coord, angle, origin=(0,0), is_radians=False):
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
