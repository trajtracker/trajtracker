"""

TrajTracker - movement package - private utilities

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
import re
import xml.etree.ElementTree as ET

import numpy as np
from enum import Enum

import expyriment as xpy
from expyriment.misc import geometry

import trajtracker


#--------------------------------------------------------------------------
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

            raise trajtracker.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, type_name, value))

    elif attr_type == "RGB":
        validate_attr_rgb(obj, attr_name, value)

    elif attr_type == "coord":
        validate_attr_is_coord(obj, attr_name, value)

    else:
        raise Exception("trajtracker internal error: unsupported type '{:}'".format(attr_type))


#--------------------------------------
LIST_TYPES = (list, tuple, np.ndarray)

def validate_attr_is_collection(obj, attr_name, value, min_length=None, max_length=None,
                                none_allowed=False, allow_set=False):

    if value is None and none_allowed:
        value = ()

    val_methods = dir(value)
    ok = "__len__" in val_methods and "__iter__" in val_methods and (allow_set or "__getitem__" in val_methods)
    if not ok:
        raise trajtracker.TypeError("{:}.{:} was set to a non-{:} value ({:})".format(
            get_type_name(obj), attr_name, "collection" if allow_set else "list", value))

    if min_length is not None and len(value) < min_length:
        raise trajtracker.TypeError(
            "{:}.{:} cannot be assigned to a collection with {:} elements - a minimal of {:} elements are expected".
            format(get_type_name(obj), attr_name, len(value), min_length))

    if max_length is not None and len(value) > max_length:
        raise trajtracker.TypeError(
            "{:}.{:} cannot be assigned to a collection with {:} elements - a maximum of {:} elements is allowed".
            format(get_type_name(obj), attr_name, len(value), max_length))

    return value


#--------------------------------------
def validate_attr_rgb(obj, attr_name, value, accept_single_num=False, none_allowed=False):

    if none_allowed and value is None:
        return None

    if accept_single_num and isinstance(value, int) and 0 <= value < 2**24:
        return (int(np.floor(value / 2 ** 16)), int(np.floor(value / 256)) % 256, value % 256)

    validate_attr_type(obj, attr_name, value, tuple, type_name="(red,green,blue)")
    if len(value) != 3 or \
            not isinstance(value[0], int) or not (0 <= value[0] < 256) or \
            not isinstance(value[1], int) or not (0 <= value[1] < 256) or \
            not isinstance(value[2], int) or not (0 <= value[2] < 256):
        raise trajtracker.TypeError("{:}.{:} was set to an invalid value ({:}) - expecting (red,green,blue)".format(get_type_name(obj), attr_name, value))

    return value

#--------------------------------------
def validate_attr_is_coord(obj, attr_name, value, change_none_to_0=False, allow_float=False):

    if value is None and change_none_to_0:
        return (0, 0)

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    validate_attr_is_collection(obj, attr_name, value, 2, 2)
    elem_type = numbers.Number if allow_float else int
    validate_attr_type(obj, "{:}[0]".format(attr_name), value[0], elem_type)
    validate_attr_type(obj, "{:}[1]".format(attr_name), value[1], elem_type)

    return value


#--------------------------------------
def validate_attr_numeric(obj, attr_name, value, none_value=NoneValues.Invalid):
    if value is None:
        if none_value == NoneValues.Invalid:
            raise trajtracker.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, "numeric", "None"))
        elif none_value == NoneValues.Valid:
            pass
        elif none_value == NoneValues.ChangeTo0:
            value = 0

    if value is not None and not isinstance(value, numbers.Number):
        raise trajtracker.TypeError(ErrMsg.attr_invalid_type(get_type_name(obj), attr_name, "numeric", value))

    return value

#--------------------------------------
def validate_attr_not_negative(obj, attr_name, value):
    if value is not None and value < 0:
        msg = "{:}.{:} was set to a negative value ({:})".format(get_type_name(obj), attr_name, value)
        raise trajtracker.ValueError(msg)

#--------------------------------------
def validate_attr_positive(obj, attr_name, value):
    if value is not None and value <= 0:
        msg = "{:}.{:} was set to a negative/0 value ({:})".format(get_type_name(obj), attr_name, value)
        raise trajtracker.ValueError(msg)


#============================================================================
#   Validate function arguments
#============================================================================

#-------------------------------------------------------------------------
def validate_func_arg_type(obj, func_name, arg_name, value, arg_type, none_allowed=False, type_name=None):

    if arg_type == "coord":
        validate_func_arg_is_coord(obj, func_name, arg_name, value)

    elif (value is None and not none_allowed) or (value is not None and not isinstance(value, arg_type)):
        if type_name is None:
            type_name = get_type_name(arg_type)

        raise trajtracker.TypeError("{:}() was called with a non-{:} {:} ({:})".format(
            _get_func_name(obj, func_name), type_name, arg_name, value))


#--------------------------------------
def validate_func_arg_not_negative(obj, func_name, arg_name, value):

    if value is not None and value < 0:
        raise ttrk.ValueError("Argument '{:}' of {:}() has a negative value ({:})".format(arg_name, _get_func_name(obj, func_name), value))

#--------------------------------------
_LIST_TYPES = (list, tuple, np.ndarray)

def validate_func_arg_is_collection(obj, func_name, arg_name, value, min_length=None, max_length=None,
                                    none_allowed=False, allow_set=False):

    if value is None and none_allowed:
        value = ()

    val_methods = dir(value)
    ok = "__len__" in val_methods and "__iter__" in val_methods and (allow_set or "__getitem__" in val_methods)
    if not ok:
        raise trajtracker.TypeError("{:}() was called with a non-{:} {:} ({:})".format(
            _get_func_name(obj, func_name), "collection" if allow_set else "list", arg_name, value))

    if min_length is not None and len(value) < min_length:
        raise trajtracker.TypeError("Argument {:} of {:}() cannot be set to a collection with {:} elements - a minimal of {:} elements are expected".
                         format(arg_name, _get_func_name(obj, func_name), len(value), min_length))
    if max_length is not None and len(value) > max_length:
        raise trajtracker.TypeError("Argument {:} of {:}() cannot be set to a collection with {:} elements - a maximum of {:} elements is allowed".
                         format(arg_name, _get_func_name(obj, func_name), len(value), max_length))

    return value

#--------------------------------------
def validate_func_arg_positive(obj, func_name, arg_name, value):
    if value is not None and value <= 0:
        raise trajtracker.ValueError("Argument {:} of {:}() has a negative/0 value ({:})".format(arg_name, _get_func_name(obj, func_name), value))


#--------------------------------------
def validate_func_arg_is_coord(obj, func_name, arg_name, value, change_none_to_0=False):

    if value is None and change_none_to_0:
        return (0, 0)

    if isinstance(value, geometry.XYPoint):
        value = (value.x, value.y)

    validate_func_arg_is_collection(obj, func_name, arg_name, value, 2, 2)
    validate_func_arg_type(obj, func_name, "{:}[0]".format(arg_name), value[0], int)
    validate_func_arg_type(obj, func_name, "{:}[1]".format(arg_name), value[1], int)

    return value


#--------------------------------------------------------------------
def update_xyt_validate_and_log(self, x_coord, y_coord, time_in_trial, time_used=True):

    validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number, type_name="numeric")
    validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number, type_name="numeric")

    if time_used:
        validate_func_arg_type(self, "update_xyt", "time_in_trial", time_in_trial, numbers.Number, type_name="numeric")

    self._log_func_enters("update_xyt", [x_coord, y_coord, time_in_trial])


#============================================================================
#   Misc
#============================================================================

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
    xpy._internals.active_exp.screen.clear()

def display_update():
    xpy._internals.active_exp.screen.update()


#============================================================================
#  Parse strings into values (this is used mainly for configuring objects via XML)
#============================================================================


#--------------------------------------------------------------------
def parse_coord(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise trajtracker.TypeError('Invalid coordinates "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise trajtracker.ValueError('Invalid coordinates "{:}"'.format(value))

    return (int(m.group(1)), int(m.group(2)))

#--------------------------------------------------------------------
def parse_rgb(value):

    if isinstance(value, tuple):
        return value

    if not isinstance(value, str):
        raise trajtracker.TypeError('Invalid RGB "{:}" - expecting a string'.format(value))

    m = re.match('^\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)\s*$', value)

    if m is None:
        raise trajtracker.ValueError('Invalid RGB "{:}"'.format(value))

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
        raise trajtracker.TypeError('Invalid RGB list "{:}" - expecting an XML object'.format(xml))

    colors = []

    for child in xml:
        if child.tag != "color":
            raise trajtracker.TypeError('Invalid XML format for a list of colors - expecting an XML block with several <color>...</color> blocks under it'.format(value))
        colors.append(parse_rgb(child.text.strip()))

    return colors

#--------------------------------------------------------------------
def _parse_list_of(value, converter):

    if re.match("^\[.*\]$", value):
        elems = value[1:-1].split(";")
        return [converter(e) for e in elems]
    else:
        return converter(value)


def parse_scalar_or_list(converter):
    return lambda value: _parse_list_of(value, converter)
