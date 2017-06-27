"""
Arrow that points at the number line

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

import expyriment as xpy


class DownArrow(xpy.stimuli.Shape):

    def __init__(self, colour=xpy.misc.constants.C_GREEN):
        super(DownArrow, self).__init__()
        # noinspection PyTypeChecker
        self.add_vertices([(10, 20), (-6, 0), (0, 20), (-9, 0), (0, -20), (-6, 0)])
        self.colour = colour
        self.preload()


    @property
    def size(self):
        return (20, 40)
