
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
