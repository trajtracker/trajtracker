"""

TrajTracker - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum
import numbers

import trajtracker._utils as _u
from trajtracker import _TTrkObject, BadFormatError

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')

from _ExperimentError import ExperimentError
from trajtracker.data import fromXML


#-------------------------------------------------------------------
# Base class for all validators
#
class _BaseValidator(_TTrkObject):

    def __init__(self, enabled=False):
        super(_BaseValidator, self).__init__()
        self.enabled = enabled


    @property
    def enabled(self):
        """
        Whether the validator is currently enabled

        :type: bool
        """
        return self._enabled

    @enabled.setter
    @fromXML(bool)
    def enabled(self, value):
        _u.validate_attr_type(self, "enabled", value, bool)
        self._enabled = value


#--------------------------------------------------------------------
# Parse a string into ValidationAxis (for loading from XML)
#
def _parse_validation_axis(value):

    if isinstance(value, ValidationAxis):
        return value

    if not isinstance(value, str):
        raise TypeError('Invalid ValidationAxis "{:}" - expecting a string'.format(value))

    value = value.lower()

    if value == 'x':
        return ValidationAxis.x
    elif value == 'y':
        return ValidationAxis.y
    elif value == 'xy':
        return ValidationAxis.xy

    raise BadFormatError('Invalid ValidationAxis "{:}"'.format(value))


ValidationAxis.parse = staticmethod(_parse_validation_axis)


#--------------------------------------------------------------------
def create_experiment_error(self, err_code, message, err_args=None):
    if self._should_log(self.log_warn):
        self._log_write("ExperimentError,{0},{1},{2},{3}".format(type(self).__name__, err_code, message, err_args))

    return ExperimentError(err_code, message, self, err_args)


#--------------------------------------------------------------------

from _GlobalSpeedValidator import GlobalSpeedValidator, GlobalSpeedGuide
from _InstantaneousSpeedValidator import InstantaneousSpeedValidator
from _LocationsValidator import LocationsValidator
from _MovementAngleValidator import MovementAngleValidator
from _MoveByGradientValidator import MoveByGradientValidator
from _NCurvesValidator import NCurvesValidator


