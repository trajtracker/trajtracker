"""
Non-visual rectangle

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import trajtracker._utils as _u


class Rectangle(object):

    def __init__(self, x, y, width, height):
        """
        Constructor - invoked when you create a new object by writing Rectangle()

        :param x: the rectangle's center
        :param y: the rectangle's center
        :param width:
        :param height:
        """
        _u.validate_func_arg_type(self, "__init__", "x", x, int)
        _u.validate_func_arg_type(self, "__init__", "y", y, int)
        _u.validate_func_arg_type(self, "__init__", "width", width, int)
        _u.validate_func_arg_type(self, "__init__", "height", height, int)
        _u.validate_func_arg_positive(self, "__init__", "width", width)
        _u.validate_func_arg_positive(self, "__init__", "height", height)

        self.x = x
        self.y = y
        self.width = width
        self.height = height


    def overlapping_with_position(self, pos):
        x, y = pos
        return x >= self.x - self. width /2 and \
               x <= self.x + self. width /2 and \
               y >= self.y - self. height /2 and \
               y <= self.y + self. height /2


    @property
    def position(self):
        return self.x, self.y

