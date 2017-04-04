"""

 Allow mouse to move only according to a given image - from light color to a darker color (or vice versa)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numpy as np

import trajtracker._utils as _u
import trajtracker.utils as u
import trajtracker.validators
from trajtracker.misc import LocationColorMap
from trajtracker.validators import _BaseValidator
from trajtracker.data import fromXML



class MoveByGradientValidator(_BaseValidator):

    err_gradient = "GradientViolation"


    def __init__(self, image, position=(0, 0), rgb_should_ascend=True, max_valid_back_movement=0,
                 cyclic=False, enabled=True):
        """
        Constructor

        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param position: See :attr:`~trajtracker.movement.MoveByGradientValidator.enabled`
        :param position: See :attr:`~trajtracker.movement.MoveByGradientValidator.position`
        :param rgb_should_ascend: See :attr:`~trajtracker.movement.MoveByGradientValidator.rgb_should_ascend`
        :param max_valid_back_movement: See :attr:`~trajtracker.movement.MoveByGradientValidator.max_valid_back_movement`
        :param cyclic: See :attr:`~trajtracker.movement.MoveByGradientValidator.cyclic`
        """
        super(MoveByGradientValidator, self).__init__(enabled=enabled)

        self._lcm = LocationColorMap(image, position=position, use_mapping=True, colormap="RGB")
        self.rgb_should_ascend = rgb_should_ascend
        self.max_valid_back_movement = max_valid_back_movement
        self.cyclic = cyclic
        self.color_filter = None
        self.reset()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the image: (x,y) tuple/list, indicating the image center
        For even-sized images, use the Expyriment standard.
        The position is used to align the image's coordinate space with that of update_xyt()
        """
        return self._lcm.position

    @position.setter
    @fromXML(_u.parse_coord)
    def position(self, value):
        self._lcm.position = value


    #-------------------------------------------------
    @property
    def rgb_should_ascend(self):
        """
        Whether the valid movement is from lower RGB codes to higher RGB codes (True) or vice versa (False)
        """
        return self._rgb_should_ascend


    @rgb_should_ascend.setter
    @fromXML(bool)
    def rgb_should_ascend(self, value):
        _u.validate_attr_type(self, "rgb_should_ascend", value, bool)
        self._rgb_should_ascend = value
        self._log_setter("rgb_should_ascend")


    #-------------------------------------------------
    @property
    def max_valid_back_movement(self):
        """
        The maximal valid delta of color-change in the opposite direction that would still be allowed
        """
        return self._max_valid_back_movement


    @max_valid_back_movement.setter
    @fromXML(float)
    def max_valid_back_movement(self, value):
        _u.validate_attr_numeric(self, "max_valid_back_movement", value)
        _u.validate_attr_not_negative(self, "max_valid_back_movement", value)
        self._max_valid_back_movement = value
        self._log_setter("max_valid_back_movement")


    #-------------------------------------------------
    @property
    def color_filter(self):
        """
        Define which colors should be used by this validator. Other colors are ignored. If the finger/mouse
        steps over them, the validation is temporarily suspended. Possible values are:

        - A list/tuple/set of valid colors
        - A filtering function - gets an RGB color as tuple, returns a bool
        - A mask - only matching colors (and 0=black) will be included
        """
        return self._color_filter

    @color_filter.setter
    def color_filter(self, filter):

        if filter is None:
            self._color_filter = None
            self._lcm.colormap = "RGB"
            self._get_min_max_colors()
            return

        _u.validate_attr_type(self, "color_filter", filter, (list, tuple, set, type(lambda:1), int))

        if isinstance(filter, (list, tuple, set)):
            used_values = set(filter)
            sample_value = list(used_values)[0]
            if isinstance(sample_value, int):
                filter = lambda color: u.color_rgb_to_num(color) in used_values
            elif isinstance(sample_value, tuple):
                filter = lambda color: color in used_values

        elif isinstance(filter, int):
            mask = filter
            def filter_func(color):
                color_num = u.color_rgb_to_num(color)
                return color_num == 0 or (color_num & ~mask) == 0
            filter = filter_func

        self._color_filter = filter
        self._lcm.colormap = lambda color: u.color_rgb_to_num(color) if filter(color) else None
        self._get_min_max_colors()


    #-------------------------------------------------
    @property
    def cyclic(self):
        """
        Whether the gradient is cyclic, i.e., allows moving between the darkest to the lightest color
        """
        return self._cyclic

    @cyclic.setter
    @fromXML(bool)
    def cyclic(self, value):
        _u.validate_attr_type(self, "cyclic", value, bool)
        self._cyclic = value


    #-------------------------------------------------
    def _get_min_max_colors(self):
        filter = (lambda c: True) if self._color_filter is None else self._color_filter
        colors = [u.color_rgb_to_num(c) for c in self._lcm.available_colors if filter(c)]
        self._min_available_color = min(colors)
        self._max_available_color = max(colors)


    #======================================================================
    #   Validate
    #======================================================================

    #-----------------------------------------------------------------
    def reset(self, time0=None):
        """
        Reset the movement validation
        """

        self._log_func_enters("reset", [time0])

        self._last_color = None


    #-----------------------------------------------------------------
    def update_xyt(self, x_coord, y_coord, time=None):
        """
        Validate the movement

        :return: None if all OK, ExperimentError if error
        """

        if not self._enabled:
            return None

        _u.update_xyt_validate_and_log(self, x_coord, y_coord, time, False)

        color = self._lcm.get_color_at(x_coord, y_coord)
        if color is None:  # color N/A -- can't validate
            self._last_color = None
            return None

        if self._last_color is None:
            #-- Nothing to validate
            self._last_color = color
            return None

        expected_direction = 1 if self._rgb_should_ascend else -1
        rgb_delta = (color - self._last_color) * expected_direction
        print "RGB delta = %d  (%d --> %d)" % (rgb_delta, self._last_color, color)
        if rgb_delta >= 0:
            #-- All is OK
            self._last_color = color
            return None

        if rgb_delta >= -self._max_valid_back_movement:
            #-- The movement was in the opposite color diredction, but only slightly:
            #-- Don't issue an error, but also don't update "last_color" - remember the previous one
            return None

        if self._cyclic:
            range = self._max_available_color - self._min_available_color
            if np.abs(rgb_delta) >= 8 * (range - np.abs(rgb_delta)):
                # It's much more likely to interpret this movement as a "cyclic" movement - i.e., one that crossed
                # the boundary of lightest-to-darkest (or the other way around, depending on the ascend/descend direction)
                self._last_color = color
                return None

        if self._should_log(self.log_debug):
            self._log_write("InvalidDirection,last_color={:},curr_color={:}".format(self._last_color, color), True)

        return trajtracker.validators.create_experiment_error(self, self.err_gradient, "You moved in an invalid direction")


