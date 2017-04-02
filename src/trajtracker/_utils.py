"""

TrajTracker - movement package - private utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from enum import Enum
import numbers, re
import numpy as np
import xml.etree.ElementTree as ET

from expyriment.misc import geometry


#--------------------------------------------------------------------------
class ErrMsg(object):

    _invalid_attr_type = "trajtracker error: invalid attempt to set {0}.{1} to a non-{2} value ({3})"
    _set_to_non_positive = "trajtracker error: invalid attempt to set {0}.{1} to a non-positive value ({2})"
    _set_to_negative = "trajtracker error: invalid attempt to set {0}.{1} to a negative value ({2})"
    _set_to_invalid_value = "trajtracker error: {0}.{1} was set to an invalid value ({2})"

    @staticmethod
    def attr_invalid_type(class_name, attr_name, expected_type, arg_value):
        return "trajtracker error: {0}.{1} was set to a non-{2} value ({3})".format(class_name, attr_name, expected_type, arg_value)

    @staticmethod
    def attr_invalid_value(class_name, attr_name, arg_value):
        "trajtracker error: {0}.{1} was set to an invalid value ({2})".format(class_name, attr_name, arg_value)


    @staticmethod
    def invalid_method_arg_type(class_name, method_name, expected_type, arg_name, arg_value):
        return "trajtracker error: {0}.{1}() was called with a non-{2} {3} ({4})".format(class_name, method_name, expected_type, arg_name, arg_value)


#============================================================================
#   Validate attributes
#============================================================================

NoneValues = Enum("NoneValues", "Invalid Valid ChangeTo0")


#--------------------------------------
def _get_type_name(t):

    if not isinstance(t, type):
        t = type(t)

    if isinstance(t, (list, tuple, np.ndarray)):
        return "/".join([_get_type_name(tt) for tt in t])
    elif t == numbers.Number:
        return "number"
    elif t == np.ndarray:
        return "array"
    else:
        return t.__name__


#--------------------------------------
def validate_attr_type(obj, attr_name, value, attr_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, attr_type)):
        if type_name is None:
            type_name = _get_type_name(attr_type)

        raise TypeError(ErrMsg.attr_invalid_type(_get_type_name(obj), attr_name, type_name, value))

#--------------------------------------
def validate_attr_anylist(obj, attr_name, value, min_length=None, max_length=None, none_allowed=False):

    if value is None and none_allowed:
        value = ()

    validate_attr_type(obj, attr_name, value, (list, tuple, np.ndarray), type_name="list/tuple")
    if min_length is not None and len(value) < min_length:
        raise TypeError(
            "trajtracker error: {:}.{:} cannot be assigned to a collection with {:} elements - a minimal of {:} elements are expected".
            format(_get_type_name(obj), attr_name, len(value), min_length))

    if max_length is not None and len(value) > max_length:
        raise TypeError(
            "trajtracker error: {:}.{:} cannot be assigned to a collection with {:} elements - a maximum of {:} elements is allowed".
            format(_get_type_name(obj), attr_name, len(value), max_length))

    return value


#--------------------------------------
def validate_attr_rgb(obj, attr_name, value, accept_single_num=False):

    if accept_single_num and isinstance(value, int) and 0 <= value < 2**24:
        return (int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256)

    validate_attr_type(obj, attr_name, value, tuple, type_name="(red,green,blue)")
    if len(value) != 3 or \
            not isinstance(value[0], int) or not (0 <= value[0] < 256) or \
            not isinstance(value[1], int) or not (0 <= value[1] < 256) or \
            not isinstance(value[2], int) or not (0 <= value[2] < 256):
        raise TypeError("trajtracker error: {:}.{:} was set to an invalid value ({:}) - expecting (red,green,blue)".format(_get_type_name(obj), attr_name, value))

    return value

#--------------------------------------
def validate_attr_is_coord(obj, attr_name, value, change_none_to_0=False):

    if value is None and change_none_to_0:
        return (0, 0)

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    validate_attr_anylist(obj, attr_name, value, 2, 2)
    validate_attr_type(obj, "{:}[0]".format(attr_name), value[0], int)
    validate_attr_type(obj, "{:}[1]".format(attr_name), value[1], int)

    return value


#--------------------------------------
def validate_attr_numeric(obj, attr_name, value, none_value=NoneValues.Invalid):
    if value is None:
        if none_value == NoneValues.Invalid:
            raise TypeError(ErrMsg.attr_invalid_type(_get_type_name(obj), attr_name, "numeric", "None"))
        elif none_value == NoneValues.Valid:
            pass
        elif none_value == NoneValues.ChangeTo0:
            value = 0

    if value is not None and not isinstance(value, numbers.Number):
        raise TypeError(ErrMsg.attr_invalid_type(_get_type_name(obj), attr_name, "numeric", value))

    return value

#--------------------------------------
def validate_attr_not_negative(obj, attr_name, value):
    if value is not None and value < 0:
        msg = "trajtracker error: {0}.{1} was set to a negative value ({2})".format(_get_type_name(obj), attr_name, value)
        raise ValueError(msg)

#--------------------------------------
def validate_attr_positive(obj, attr_name, value):
    if value is not None and value <= 0:
        msg = "trajtracker error: {0}.{1} was set to a negative/0 value ({2})".format(_get_type_name(obj), attr_name, value)
        raise ValueError(msg)


#============================================================================
#   Validate function arguments
#============================================================================

#-------------------------------------------------------------------------
def validate_func_arg_type(obj, func_name, arg_name, value, arg_type, none_allowed=False, type_name=None):

    if (value is None and not none_allowed) or (value is not None and not isinstance(value, arg_type)):
        if type_name is None:
            type_name = _get_type_name(arg_type)

        raise TypeError("trajtracker error: {:}() was called with a non-{:} {:} ({:})".format(
            _get_func_name(obj, func_name), type_name, arg_name, value))

#--------------------------------------
def validate_func_arg_not_negative(obj, func_name, arg_name, value):

    if value is not None and value < 0:
        raise ValueError("trajtracker error: Argument '{:}' of {:}() has a negative value ({:})".format(arg_name, _get_func_name(obj, func_name), value))

#--------------------------------------
def validate_func_arg_anylist(obj, func_name, arg_name, value, min_length=None, max_length=None, none_allowed=False):

    if value is None and none_allowed:
        value = ()

    validate_func_arg_type(obj, func_name, arg_name, value, (list, tuple, np.ndarray), type_name="list/tuple")
    if min_length is not None and len(value) < min_length:
        raise TypeError("trajtracker error: Argument {:} of {:}() cannot be set to a collection with {:} elements - a minimal of {:} elements are expected".
                         format(arg_name, _get_func_name(obj, func_name), len(value), min_length))
    if max_length is not None and len(value) > max_length:
        raise TypeError("trajtracker error: Argument {:} of {:}() cannot be set to a collection with {:} elements - a maximum of {:} elements is allowed".
                         format(arg_name, _get_func_name(obj, func_name), len(value), max_length))

    return value

#--------------------------------------
def validate_func_arg_positive(obj, func_name, arg_name, value):
    if value is not None and value <= 0:
        raise ValueError("trajtracker error: Argument {:} of {:}() has a negative/0 value ({:})".format(arg_name, _get_func_name(obj, func_name), value))


#--------------------------------------
def _get_func_name(obj, func_name):
    if obj is None:
        return func_name
    else:
        return "{:}.{:}".format(_get_type_name(obj), func_name)



#--------------------------------------------------------------------
def parse_coord(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise TypeError('Invalid coordinates "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise ValueError('Invalid coordinates "{:}"'.format(value))

    return (int(m.group(1)), int(m.group(2)))

#--------------------------------------------------------------------
def parse_rgb(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise TypeError('Invalid RGB "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise ValueError('Invalid RGB "{:}"'.format(value))

    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


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
        raise TypeError('Invalid RGB list "{:}" - expecting an XML object'.format(xml))

    colors = []

    for child in xml:
        if child.tag != "color":
            raise TypeError('Invalid XML format for a list of colors - expecting an XML block with several <color>...</color> blocks under it'.format(value))
        colors.append(parse_rgb(child.text.strip()))

    return colors
