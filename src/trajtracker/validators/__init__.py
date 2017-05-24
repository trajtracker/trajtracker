"""

TrajTracker - validators package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""

import enum

import trajtracker as ttrk
from trajtracker import BadFormatError, TypeError

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')

from ._ExperimentError import ExperimentError, create_experiment_error
from ._GlobalSpeedValidator import GlobalSpeedValidator, GlobalSpeedGuide
from ._InstantaneousSpeedValidator import InstantaneousSpeedValidator
from ._LocationsValidator import LocationsValidator
from ._MovementAngleValidator import MovementAngleValidator
from ._MoveByGradientValidator import MoveByGradientValidator
from ._NCurvesValidator import NCurvesValidator


