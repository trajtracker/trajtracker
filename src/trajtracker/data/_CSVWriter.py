"""

CSV writer: write a CSV file, optionally in parts (while closing the file between consecutive parts)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import csv

import trajtracker
import trajtracker._utils as _u

func_type = type(lambda: None)


class CSVWriter(trajtracker._TTrkObject):

    # todo   NOT SURE THIS CLASS IS NEEDED! WE CAN KEEP A FILE OPEN AND FLUSH

    # define fields in constructor
    # each field is defined either as name or as name+formatter, e.g.
    #  writer = CSVWriter(filename)

    # add_field(name, getter, format="{:}")  -- the getter gets {exp, trial} etc.

    # write_header(close_file=True)

    # write_row(close_file=True)  [opens and closes the output file on each row]

    # write_rows() -- gets list of rows

    pass
