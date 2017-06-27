"""
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
import re

import trajtracker as ttrk


#----------------------------------------------------------
def parse_text_justification(s):
    s = s.lower()

    if s == "left":
        return 0
    elif s == "center":
        return 1
    elif s == "right":
        return 2
    else:
        raise ttrk.ValueError("Invalid text justification ({:})".format(s))


#----------------------------------------------------------
def parse_rgb(s):
    orig_s = s

    if re.match("^\((.*)\)$", s) is not None:
        s = s[1:-1]

    m = re.match("\s*(\d+)\s*:\s*(\d+)\s*:\s*(\d+)\s*", s)
    if m is None:
        raise ttrk.ValueError("Invalid RGB format: {:}".format(orig_s))

    return m.group(1), m.group(2), m.group(3)


#----------------------------------------------------------
def parse_coord(s):
    orig_s = s

    if re.match("^\((.*)\)$", s) is not None:
        s = s[1:-1]

    m = re.match("\s*(-?\d+)\s*:\s*(-?\d+)\s*", s)
    if m is None:
        raise ttrk.ValueError("Invalid format for coordinates: {:}".format(orig_s))

    return m.group(1), m.group(2)

#----------------------------------------------------------
def parse_size(s):
    orig_s = s

    if re.match("^\((.*)\)$", s) is not None:
        s = s[1:-1]

    m = re.match("\s*(\d+)\s*:\s*(\d+)\s*", s)
    if m is None:
        raise ttrk.ValueError("Invalid format for size: {:}".format(orig_s))

    return m.group(1), m.group(2)
