"""

TrajTracker - stimuli package

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

from enum import Enum
Orientation = Enum('Orientation', 'Horizontal Vertical')

#  Import the package classes
from ._BaseMultiStim import BaseMultiStim
from ._FixationZoom import FixationZoom
from ._NumberLine import NumberLine
from ._Slider import Slider
from ._StimulusContainer import StimulusContainer
from ._StimulusSelector import StimulusSelector
from ._MultiStimulus import MultiStimulus
from ._MultiTextBox import MultiTextBox
