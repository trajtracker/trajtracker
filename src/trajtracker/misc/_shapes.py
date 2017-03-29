"""

 Shapes that can't be drawn, but we can know their size, location, etc.

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np
import trajtracker.utils as u
import trajtracker._utils as _u


class shapes:
    """
    Various geometrical shapes: they cannot be drawn on screen, but we can run some calculations over them
    """

    # ----------------------------------------------------
    class Rectangle(object):

        def __init__(self, x, y, width, height):
            """
            Constructor

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
            return x >= self.x - self.width/2 and \
                   x <= self.x + self.width/2 and \
                   y >= self.y - self.height/2 and \
                   y <= self.y + self.height/2

        @property
        def position(self):
            return self.x, self.y


    # ----------------------------------------------------
    class Circle(object):

        def __init__(self, x, y, radius):
            """
            Constructor

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


        def overlapping_with_position(self, pos):
            x, y = pos
            distance_from_center = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
            return distance_from_center <= self.radius

        @property
        def position(self):
            return self.x, self.y


    # ----------------------------------------------------
    class Sector(object):
        """
        A sector of a circle
        """

        def __init__(self, x, y, radius, from_angle, to_angle):
            """
            Constructor

            :param x: the circle's center
            :param y: the circle's center
            :param radius:
            :param from_angle: Left end of the sector (degrees)
            :param to_angle: Right end of the sector (degrees)
            """

            _u.validate_func_arg_type(self, "__init__", "x", x, int)
            _u.validate_func_arg_type(self, "__init__", "y", y, int)
            _u.validate_func_arg_type(self, "__init__", "radius", radius, int)
            _u.validate_func_arg_type(self, "__init__", "from_angle", from_angle, int)
            _u.validate_func_arg_type(self, "__init__", "to_angle", to_angle, int)
            _u.validate_func_arg_positive(self, "__init__", "radius", radius)

            self.x = x
            self.y = y
            self.radius = radius
            self.from_angle = from_angle % 360
            self.to_angle = to_angle % 360


        def overlapping_with_position(self, pos):
            x, y = pos
            distance_from_center = np.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
            if distance_from_center > self.radius:
                return False

            angle = u.get_angle((self.x, self.y), (x, y), as_degrees=True) % 360
            if self.from_angle < self.to_angle:
                return self.from_angle <= angle <= self.to_angle
            else:
                return not (self.to_angle <= angle <= self.from_angle)

        @property
        def position(self):
            return self.x, self.y
