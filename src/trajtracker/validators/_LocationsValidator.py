"""

 Allow mouse to be only in specific pixels, as defined by a BMP file

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.misc import LocationColorMap
from trajtracker.validators import _BaseValidator



class LocationsValidator(_BaseValidator):
    """
    This validator gets an image, and validates that the mouse/finger would be placed
    only on pixels of certain color(s).
    You can define either the valid colors or the invalid colors.
    """

    err_invalid_coordinates = "InvalidCoords"
    arg_color = 'color'  # ValidationFailed exception argument: the color in the invalid location


    #------------------------------------------------------------
    def __init__(self, image, enabled=True, position=None, default_valid=False):
        """
        Constructor

        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param enabled: See :attr:`~trajtracker.validators.LocationsValidator.enabled`
        :param position: See :attr:`~trajtracker.validators.LocationsValidator.position`
        :param default_valid: See :attr:`~trajtracker.validators.LocationsValidator.default_valid`
        """
        super(LocationsValidator, self).__init__(enabled=enabled)

        self._lcm = LocationColorMap(image, position=position, use_mapping=True, colormap="RGB")
        self.default_valid = default_valid
        self.valid_colors = set()
        self.invalid_colors = set()


    #======================================================================
    #   Properties
    #======================================================================

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the image: (x,y) tuple/list, indicating the image center
        For even-sized images, use the Expyriment standard.
        The position is used to align the image's coordinate space with that of check_xyt()
        """
        return self._lcm.position

    @position.setter
    def position(self, value):
        self._lcm.position = value
        self._log_setter("position")


    #-------------------------------------------------
    @property
    def default_valid(self):
        """
        Indicates whether by default, all points are valid or not.
        If True: use :func:`~trajtracker.misc.LocationColorMap.invalid_colors` to indicate exceptions
        If False: use :func:`~trajtracker.misc.LocationColorMap.valid_colors` to indicate exceptions
        """
        return self._default_valid


    @default_valid.setter
    def default_valid(self, value):
        _u.validate_attr_type(self, "default_valid", value, bool)
        self._default_valid = value
        self._log_setter("default_valid")


    #-------------------------------------------------
    @property
    def valid_colors(self):
        return self._valid_colors

    @valid_colors.setter
    def valid_colors(self, value):
        self._valid_colors = self._get_colors_as_ints(value, "valid_colors")
        self._log_setter("valid_colors")


    #-------------------------------------------------
    @property
    def invalid_colors(self):
        return self._invalid_colors

    @invalid_colors.setter
    def invalid_colors(self, value):
        self._invalid_colors = self._get_colors_as_ints(value, "valid_colors")
        self._log_setter("invalid_colors")


    def _get_colors_as_ints(self, value, attr_name):
        if u.is_rgb(value):
            value = (value,)

        _u.validate_attr_type(self, attr_name, value, (list, tuple, set))

        colors = set()
        for c in value:
            if not u.is_rgb(c):
                raise ValueError(_u.ErrMsg.attr_invalid_type(type(self), attr_name, "color", value))
            colors.add(u.color_rgb_to_num(c))

        return colors


    #======================================================================
    #   Validate
    #======================================================================

    def reset(self, time0=None):
        pass


    def check_xyt(self, x_coord, y_coord, time=None):
        """
        Check whether the given coordinate is a valid one

        :param time: ignored
        :return: None if all OK, ValidationFailed if error
        """
        self._check_xyt_validate_and_log(x_coord, y_coord, time, False)

        if not self._enabled:
            return None

        color = self._lcm.get_color_at(x_coord, y_coord)
        if self._default_valid:
            ok = color not in self._invalid_colors
        else:
            ok = color in self._valid_colors

        if ok:
            return None

        else:
            return self._create_validation_error(self.err_invalid_coordinates, "You moved to an invalid location",
                                                 {self.arg_color: color})


