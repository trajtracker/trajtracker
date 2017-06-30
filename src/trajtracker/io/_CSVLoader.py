"""

CSV reader: read a CSV file and translate columns to specific data types

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

import csv

import trajtracker as ttrk
import trajtracker._utils as _u

func_type = type(lambda: None)


class CSVLoader(ttrk.TTrkObject):

    #: Each loaded row will have an auto-generated field with this name. The field contains the corresponding
    #: line number in the csv text file (int)
    FLD_LINE_NUM = 'line_num'


    #------------------------------------------------
    def __init__(self, case_sensitive_col_names=False):
        """
        Create a CSVLoader object

        :param case_sensitive_col_names: If True, all field names are case insensitive
                             (when converting each row to dict, the dict key will be lowercase)
        """

        super(CSVLoader, self).__init__()

        self._case_sensitive_col_names = case_sensitive_col_names
        self._fields = {}


    #------------------------------------------------
    def add_field(self, field_name, field_type=str, optional=False):
        """
        Define a configurable field. You do not have to define all fields in the file - only
        those for which you need special configuration.
        
        Do this before calling :func:`~trajtracker.io.CSVLoader.load_file`

        :param field_type: either a type, or a function that converts the string (from the CSV file) to another value
        :param optional: If False, :func:`~trajtracker.io.CSVLoader.load_file` will fail if the field is missing.
        """

        _u.validate_func_arg_type(self, "add_field", "field_name", field_name, str)
        _u.validate_func_arg_type(self, "add_field", "field_type", field_type, (type, func_type))
        _u.validate_func_arg_type(self, "add_field", "optional", optional, bool)

        if not self._case_sensitive_col_names:
            field_name = field_name.lower()

        self._fields[field_name] = {'type': field_type, 'optional': optional}


    #------------------------------------------------
    def load_file(self, filename):
        """
        Load data from the CSV file

        :return: a tuple with two elements: (1) list with one dict per row, transformed to the required types; 
                (2) List of field names that were found in the file.
        """

        _u.validate_func_arg_type(self, "load_file", "filename", filename, str)

        rows, fieldnames = self._read_data_from_file(filename)

        self._validate_field_names(fieldnames, filename)

        #-- Transform data
        result = []
        for row in rows:
            if not self._case_sensitive_col_names:
                row = self._transform_lowercase(row)
            row = self._transform_types(row, filename)
            result.append(row)

        return result, fieldnames


    #------------------------------------------------
    def _read_data_from_file(self, filename):

        #-- Load data from file
        fp = open(filename)
        try:
            reader = csv.DictReader(fp)

            rows = []
            for row in reader:
                row[self.FLD_LINE_NUM] = reader.line_num
                rows.append(row)
            fieldnames = reader.fieldnames
        finally:
            fp.close()

        return rows, fieldnames


    #------------------------------------------------
    def _validate_field_names(self, fieldnames, filename):

        if not self._case_sensitive_col_names:
            fieldnames = [field.lower() for field in fieldnames]

        if self.FLD_LINE_NUM in fieldnames:
            raise ttrk.BadFormatError("An invalid field name ({:}) was found im {:} - this is a reserved field name".format(
                self.FLD_LINE_NUM, filename))

        for field in self._fields:
            if field not in fieldnames and not self._fields[field]['optional']:
                raise ttrk.BadFormatError("Mandatory field '{:} is missing in file {:}".format(field, filename))


    #------------------------------------------------
    @staticmethod
    def _transform_lowercase(row):
        return dict([(k.lower(), row[k]) for k in row.keys()])


    #------------------------------------------------
    def _transform_types(self, row, filename):

        for field in row:

            if field not in self._fields:
                continue

            field_type = self._fields[field]['type']

            if field_type != str:
                try:
                    row[field] = field_type(row[field])
                except BaseException as e:
                    raise ttrk.BadFormatError("Invalid CSV file format (line {:} in {:}): {:}".
                                              format(row[self.FLD_LINE_NUM], filename, e))

        return row
