"""
 Allow mouse to be only in specific pixels, as defined by a BMP file

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

# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
import trajtracker.validators
from trajtracker.misc import LocationColorMap
from trajtracker.misc import EnabledDisabledObj



class LocationsValidator(trajtracker.TTrkObject, EnabledDisabledObj):

    err_invalid_coordinates = "InvalidCoords"
    arg_color = 'color'  # ExperimentError argument: the color in the invalid location


    #------------------------------------------------------------
    def __init__(self, image, enabled=True, position=None, default_valid=False):
        """
        Constructor - invoked when you create a new object by writing LocationsValidator()

        :param image: Name of a BMP file, or the actual image (rectangular matrix of colors)
        :param enabled: See :attr:`~trajtracker.validators.LocationsValidator.enabled`
        :param position: See :attr:`~trajtracker.validators.LocationsValidator.position`
        :param default_valid: See :attr:`~trajtracker.validators.LocationsValidator.default_valid`
        """
        trajtracker.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

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
        The position is used to align the image's coordinate space with that of update_xyt()
        """
        return self._lcm.position

    @position.setter
    def position(self, value):
        self._lcm.position = value
        self._log_property_changed("position")


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
        self._log_property_changed("default_valid")


    #-------------------------------------------------
    @property
    def valid_colors(self):
        return self._valid_colors

    @valid_colors.setter
    def valid_colors(self, value):
        self._valid_colors = self._get_colors_as_ints(value, "valid_colors")
        self._log_property_changed("valid_colors")


    #-------------------------------------------------
    @property
    def invalid_colors(self):
        return self._invalid_colors

    @invalid_colors.setter
    def invalid_colors(self, value):
        self._invalid_colors = self._get_colors_as_ints(value, "valid_colors")
        self._log_property_changed("invalid_colors")


    def _get_colors_as_ints(self, value, attr_name):
        if u.is_rgb(value):
            value = (value,)

        _u.validate_attr_is_collection(self, attr_name, value, allow_set=True)

        colors = set()
        for c in value:
            if not u.is_rgb(c):
                raise trajtracker.ValueError(_u.ErrMsg.attr_invalid_type(type(self), attr_name, "color", value))
            colors.add(u.color_rgb_to_num(c))

        return colors


    #======================================================================
    #   Validate
    #======================================================================

    #----------------------------------------------------------
    def reset(self, time0=None):
        pass


    #----------------------------------------------------------
    def update_xyt(self, position, time_in_trial=None, time_in_session=None):
        """
        Check whether the given coordinate is a valid one

        :param time_in_trial: ignored
        :param time_in_session: ignored
        :return: None if all OK, ExperimentError if error
        """
        _u.update_xyt_validate_and_log(self, position)

        if not self._enabled:
            return None

        color = self._lcm.get_color_at(position[0], position[1])
        if self._default_valid:
            ok = color not in self._invalid_colors
        else:
            ok = color in self._valid_colors

        if ok:
            return None

        else:
            return trajtracker.validators.create_experiment_error(self, self.err_invalid_coordinates, "You moved to an invalid location",
                                                                  {self.arg_color: color})


