"""
TrajTracker - validators package

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

import enum

import trajtracker as ttrk
from trajtracker import BadFormatError, TypeError

ValidationAxis = enum.Enum('ValidationAxis', 'x y xy')

from ._ExperimentError import ExperimentError, create_experiment_error
from ._FingerLiftedValidator import FingerLiftedValidator
from ._GlobalSpeedValidator import GlobalSpeedValidator, GlobalSpeedGuide
from ._InstantaneousSpeedValidator import InstantaneousSpeedValidator
from ._LocationsValidator import LocationsValidator
from ._MovementAngleValidator import MovementAngleValidator
from ._MoveByGradientValidator import MoveByGradientValidator
from ._NCurvesValidator import NCurvesValidator
