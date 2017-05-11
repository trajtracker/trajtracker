"""

TrajTracker - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum

import trajtracker as ttrk
from trajtracker import BadFormatError, TypeError

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')

from ._ExperimentError import ExperimentError


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
    if self._should_log(ttrk.log_info):
        self._log_write("ExperimentError,{0},{1},{2},{3}".format(type(self).__name__, err_code, message, err_args))

    return ExperimentError(err_code, message, self, err_args)


#========================================================================================

from ._GlobalSpeedValidator import GlobalSpeedValidator, GlobalSpeedGuide
from ._InstantaneousSpeedValidator import InstantaneousSpeedValidator
from ._LocationsValidator import LocationsValidator
from ._MovementAngleValidator import MovementAngleValidator
from ._MoveByGradientValidator import MoveByGradientValidator
from ._NCurvesValidator import NCurvesValidator


