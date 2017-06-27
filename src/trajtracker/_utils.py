"""

TrajTracker - internal utilities

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

import numbers
import re
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

import expyriment as xpy
import numpy as np
from enum import Enum
from expyriment.misc import geometry

import trajtracker as ttrk


# --------------------------------------------------------------------------
class ErrMsg(object):

    _invalid_attr_type = "invalid attempt to set {0}.{1} to a non-{2} value ({3})"
    _set_to_non_positive = "invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _set_to_negative = "invalid attempt to set {0}.{1} to a negative value ({2})"
    _set_to_invalid_value = "{0}.{1} was set to an invalid value ({2})"

    @staticmethod
    def attr_invalid_type(class_name, attr_name, expected_type, arg_value):
        return "{0}.{1} was set to a non-{2} value ({3})".format(class_name, attr_name, expected_type, arg_value)

    @staticmethod
    def attr_invalid_value(class_name, attr_name, arg_value):
        "{0}.{1} was set to an invalid value ({2})".format(class_name, attr_name, arg_value)


    @staticmethod
    def invalid_method_arg_type(class_name, method_name, expected_type, arg_name, arg_value):
        return "{0}.{1}() was called with a non-{2} {3} ({4})".format(class_name, method_name, expected_type, arg_name, arg_value)


#============================================================================
#   Validate attributes
#============================================================================

NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")


#--------------------------------------
def get_type_name(t):
    """
    Get the string name of a certain type 
    
    :param t: a type, an object (whose type will be obtained), or a string describing the type  
    """

    if isinstance(t, str):
        return t

    if not isinstance(t, type):
        t = type(t)

    if isinstance(t, (list, tuple, np.ndarray)):
        return "/".join([get_type_name(tt) for tt in t])
    elif t == numbers.Number:
        return "number"
    elif t == np.ndarray:
        return "array"
    else:
        return t.__name__


#--------------------------------------
def validate_attr_type(obj, attr_name, value, attr_type, none_allowed=False, type_name=None):

    if none_allowed and value is None:
        return

    if isinstance(attr_type, (type, tuple)):
        if not isinstance(value, attr_type):
            if type_name is None:
                type_name = get_type_name(attr_type)

            raise ttrk.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, type_name, value))

    elif attr_type == ttrk.TYPE_RGB:
        validate_attr_rgb(obj, attr_name, value)

    elif attr_type == ttrk.TYPE_COORD:
        validate_attr_is_coord(obj, attr_name, value)

    elif attr_type == ttrk.TYPE_CALLABLE:
        if "__call__" not in dir(value):
            raise ttrk.TypeError(
                "{:}.{:} was set to a non-callable value ({:})".format(get_type_name(obj), attr_name, value))

    else:
        raise Exception("trajtracker internal error: unsupported type '{:}'".format(attr_type))


#--------------------------------------------------------------------------------------
def validate_attr_is_collection(obj, attr_name, value, min_length=None, max_length=None,
                                none_allowed=False, allow_set=False):

    if value is None and none_allowed:
        return ()

    if not is_collection(value, allow_set):
        raise ttrk.TypeError("{:}.{:} was set to a non-{:} value ({:})".format(
            get_type_name(obj), attr_name, "collection" if allow_set else "list", value))

    if min_length is not None and len(value) < min_length:
        raise ttrk.TypeError(
            "{:}.{:} cannot be assigned to a collection with {:} elements - a minimal of {:} elements are expected".
            format(get_type_name(obj), attr_name, len(value), min_length))

    if max_length is not None and len(value) > max_length:
        raise ttrk.TypeError(
            "{:}.{:} cannot be assigned to a collection with {:} elements - a maximum of {:} elements is allowed".
            format(get_type_name(obj), attr_name, len(value), max_length))

    return value


#--------------------------------------
def validate_attr_rgb(obj, attr_name, value, accept_single_num=False, none_allowed=False):

    new_value, is_ok = _is_rgb(value, accept_single_num, none_allowed)
    if is_ok:
        return new_value
    else:
        raise ttrk.TypeError("{:}.{:} was set to an invalid value ({:}) - expecting (red,green,blue)".format(get_type_name(obj), attr_name, value))


#--------------------------------------
def _is_rgb(value, accept_single_num=False, none_allowed=False):
    """
    Check if the value is an RGB.
     
    :return: tuple: (1) The proper value (2) whether it's valid or not  
    """

    if value is None:
        return None, none_allowed

    if accept_single_num and isinstance(value, int) and 0 <= value < 2**24:
        return (int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256), True

    if not isinstance(value, tuple):
        return None, False
    
    if len(value) != 3 or \
            not isinstance(value[0], int) or not (0 <= value[0] < 256) or \
            not isinstance(value[1], int) or not (0 <= value[1] < 256) or \
            not isinstance(value[2], int) or not (0 <= value[2] < 256):
        return None, False

    return value, True


#--------------------------------------
def validate_attr_is_coord(obj, attr_name, value, change_none_to_0=False, allow_float=False):

    if value is None and change_none_to_0:
        return 0, 0

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    validate_attr_is_collection(obj, attr_name, value, 2, 2)
    elem_type = numbers.Number if allow_float else int
    validate_attr_type(obj, "{:}[0]".format(attr_name), value[0], elem_type)
    validate_attr_type(obj, "{:}[1]".format(attr_name), value[1], elem_type)

    return value


#--------------------------------------
def validate_attr_is_stim_size(obj, attr_name, value, allow_float=False):
    validate_attr_is_coord(obj, attr_name=attr_name, value=value, allow_float=allow_float)
    if value[0] <= 0:
        raise ttrk.ValueError("{:}.{:} was set to an invalid size (width = {:})".format(get_type_name(obj), attr_name, value))
    if value[1] <= 0:
        raise ttrk.ValueError("{:}.{:} was set to an invalid size (height = {:})".format(get_type_name(obj), attr_name, value))


#--------------------------------------
def validate_attr_numeric(obj, attr_name, value, none_value=NoneValues.Invalid):
    if value is None:
        if none_value == NoneValues.Invalid:
            raise ttrk.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, "numeric", "None"))
        elif none_value == NoneValues.Valid:
            pass
        elif none_value == NoneValues.ChangeTo0:
            value = 0

    if value is not None and not isinstance(value, numbers.Number):
        raise ttrk.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, "numeric", value))

    return value


#--------------------------------------
def validate_attr_not_negative(obj, attr_name, value):
    if value is not None and value < 0:
        msg = "{:}.{:} was set to a negative value ({:})".format(get_type_name(obj), attr_name, value)
        raise ttrk.ValueError(msg)


#--------------------------------------
def validate_attr_positive(obj, attr_name, value):
    if value is not None and value <= 0:
        msg = "{:}.{:} was set to a negative/0 value ({:})".format(get_type_name(obj), attr_name, value)
        raise ttrk.ValueError(msg)


#============================================================================
#   Validate function arguments
#============================================================================

#-------------------------------------------------------------------------
def validate_func_arg_type(obj, func_name, arg_name, value, arg_type, none_allowed=False, type_name=None):

    if arg_type == ttrk.TYPE_COORD:
        validate_func_arg_is_coord(obj, func_name, arg_name, value)

    elif arg_type == ttrk.TYPE_RGB:
        validate_func_type_rgb(obj, func_name, arg_name, value)

    elif arg_type == ttrk.TYPE_CALLABLE:
        if "__call__" not in dir(value):
            raise ttrk.TypeError("{:}() was called with a non-callable {:} ({:})".format(
                _get_func_name(obj, func_name), arg_name, value))

    elif (value is None and not none_allowed) or (value is not None and not isinstance(value, arg_type)):
        if type_name is None:
            type_name = get_type_name(arg_type)

        raise ttrk.TypeError("{:}() was called with a non-{:} {:} ({:})".format(
            _get_func_name(obj, func_name), type_name, arg_name, value))


#--------------------------------------------------------------------------------------
def validate_func_arg_not_negative(obj, func_name, arg_name, value):

    if value is not None and value < 0:
        raise ttrk.ValueError("Argument '{:}' of {:}() has a negative value ({:})".format(arg_name, _get_func_name(obj, func_name), value))


#--------------------------------------------------------------------------------------
def validate_func_arg_is_collection(obj, func_name, arg_name, value, min_length=None, max_length=None,
                                    none_allowed=False, allow_set=False):

    if value is None and none_allowed:
        value = ()

    if not is_collection(value, allow_set):
        raise ttrk.TypeError("{:}() was called with a non-{:} {:} ({:})".format(
            _get_func_name(obj, func_name), "collection" if allow_set else "list", arg_name, value))

    if min_length is not None and len(value) < min_length:
        raise ttrk.TypeError("Argument {:} of {:}() cannot be set to a collection with {:} elements - a minimal of {:} elements are expected".
                                    format(arg_name, _get_func_name(obj, func_name), len(value), min_length))
    if max_length is not None and len(value) > max_length:
        raise ttrk.TypeError("Argument {:} of {:}() cannot be set to a collection with {:} elements - a maximum of {:} elements is allowed".
                                    format(arg_name, _get_func_name(obj, func_name), len(value), max_length))

    return value


#--------------------------------------------------------------------------------------
def validate_func_arg_positive(obj, func_name, arg_name, value):
    if value is not None and value <= 0:
        raise ttrk.ValueError("Argument {:} of {:}() has a negative/0 value ({:})".format(arg_name, _get_func_name(obj, func_name), value))


#--------------------------------------------------------------------------------------
def validate_func_arg_is_coord(obj, func_name, arg_name, value, change_none_to_0=False, allow_float=False):

    if value is None and change_none_to_0:
        return 0, 0

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    elem_type = numbers.Number if allow_float else int
    validate_func_arg_is_collection(obj, func_name, arg_name, value, 2, 2)
    validate_func_arg_type(obj, func_name, "{:}[0]".format(arg_name), value[0], elem_type)
    validate_func_arg_type(obj, func_name, "{:}[1]".format(arg_name), value[1], elem_type)

    return value


#--------------------------------------------------------------------------------------
def validate_func_arg_is_stim_size(obj, func_name, arg_name, value, allow_float=False):
    validate_func_arg_is_coord(obj, func_name, arg_name, value=value, allow_float=allow_float)
    if value[0] <= 0:
        raise ttrk.TypeError("Argument {:} of {:}() is a stimulus size and cannot be set to a non-positive width ({:})".
                             format(arg_name, _get_func_name(obj, func_name), value[0]))
    if value[1] <= 0:
        raise ttrk.TypeError("Argument {:} of {:}() is a stimulus size and cannot be set to a non-positive height ({:})".
                             format(arg_name, _get_func_name(obj, func_name), value[1]))


#--------------------------------------
def validate_func_type_rgb(obj, func_name, arg_name, value, accept_single_num=False, none_allowed=False):

    new_value, is_ok = _is_rgb(value, accept_single_num, none_allowed)
    if is_ok:
        return new_value
    else:
        raise ttrk.TypeError("{:}.{:}(): argument {:} was set to an invalid value ({:}) - expecting (red,green,blue)".
                                    format(get_type_name(obj), func_name, arg_name, value))


#--------------------------------------------------------------------------------------
DONT_VALIDATE = "DONT_VALIDATE"
def update_xyt_validate_and_log(self, position, time_in_trial=DONT_VALIDATE, time_in_session=DONT_VALIDATE):

    self._log_func_enters("update_xyt", [position, time_in_trial, time_in_session])

    validate_func_arg_is_coord(self, "update_xyt", "position", position, allow_float=True)

    if time_in_trial != DONT_VALIDATE:
        validate_func_arg_type(self, "update_xyt", "time_in_trial", time_in_trial, numbers.Number)
        validate_func_arg_not_negative(self, "update_xyt", "time_in_trial", time_in_trial)

    if time_in_session != DONT_VALIDATE:
        validate_func_arg_type(self, "update_xyt", "time_in_session", time_in_session, numbers.Number)
        validate_func_arg_not_negative(self, "update_xyt", "time_in_session", time_in_session)


#============================================================================
#   Misc
#============================================================================


#--------------------------------------
def is_collection(value, allow_set=True):
    val_methods = dir(value)
    return "__len__" in val_methods and "__iter__" in val_methods and \
           (allow_set or "__getitem__" in val_methods) and not isinstance(value, str)


#--------------------------------------
def is_coord(value, allow_float=False):

    if isinstance(value, geometry.XYPoint):
        return True

    if not is_collection(value) or len(value) != 2:
        return False

    elem_type = numbers.Number if allow_float else int
    return isinstance(value[0], elem_type) and isinstance(value[1], elem_type)


#--------------------------------------
def _get_func_name(obj, func_name):
    if obj is None:
        return func_name
    else:
        return "{:}.{:}".format(get_type_name(obj), func_name)


# ============================================================================
#   Display
# ============================================================================

#--------------------------------------
def display_clear():
    """
    Clear previous objects that were drawn on the display buffer
    """
    # noinspection PyProtectedMember
    if xpy._internals.active_exp is not None and xpy._internals.active_exp.screen is not None:
        xpy._internals.active_exp.screen.clear()


def display_update():
    """
    Update the display buffer - i.e., flip
    This shows all recent items that were displayed with present(update=False) 
    """
    # noinspection PyProtectedMember
    if xpy._internals.active_exp is not None and xpy._internals.active_exp.screen is not None:
        xpy._internals.active_exp.screen.update()


#============================================================================
#  Parse strings into values (this is used mainly for configuring objects via XML)
#============================================================================


#--------------------------------------------------------------------
def parse_coord(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise ttrk.TypeError('Invalid coordinates "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise ttrk.ValueError('Invalid coordinates "{:}"'.format(value))

    return int(m.group(1)), int(m.group(2))


#--------------------------------------------------------------------
def parse_rgb(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise ttrk.TypeError('Invalid RGB "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise ttrk.ValueError('Invalid RGB "{:}"'.format(value))

    return int(m.group(1)), int(m.group(2)), int(m.group(3))


#--------------------------------------------------------------------
def parse_rgb_or_num(value):

    if isinstance(value, str):
        m = re.match('^\s*\d+\s*$', value)
        if m is not None:
            return int(m.group(1))

    return parse_rgb(value)


#--------------------------------------------------------------------
def parse_rgb_list(xml):

    if not isinstance(xml, ET.Element):
        raise ttrk.TypeError('Invalid RGB list "{:}" - expecting an XML object'.format(xml))

    colors = []

    for child in xml:
        if child.tag != "color":
            raise ttrk.TypeError('Invalid XML format for a list of colors - expecting an XML block with several <color>...</color> blocks under it'.format(value))
        colors.append(parse_rgb(child.text.strip()))

    return colors


#--------------------------------------------------------------------
def _parse_list_of(value, converter):

    if re.match("^\[.*\]$", value):
        elems = value[1:-1].split(";")
        return [converter(e) for e in elems]
    else:
        return converter(value)


#--------------------------------------------------------------------
def parse_scalar_or_list(converter):
    return lambda value: _parse_list_of(value, converter)
