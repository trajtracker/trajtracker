"""

CSV reader: read a CSV file and translate columns to specific data types

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import csv

import trajtracker
import trajtracker._utils as _u

func_type = type(lambda: None)


class CSVLoader(trajtracker._TTrkObject):
    """
    Load data from a CSV file. This class can:

    - Define some fields (columns) as mandatory;
    - Define, per field, how to transform its value from string to something else
    - Handle changes in lower/uppercase of field names
    """

    FLD_LINE_NUM = 'line_num'


    #------------------------------------------------
    def __init__(self, case_sensitive_col_names=False):
        """
        Constructor

        :param case_sensitive_col_names: If True, all field names will be converted to lowercase when loading
        """

        super(CSVLoader, self).__init__()

        self._case_sensitive_col_names = case_sensitive_col_names
        self._fields = {}


    #------------------------------------------------
    def add_field(self, field_name, field_type=str, optional=False):
        """
        Define a configurable field. You do not have to define all fields in the file - only
        those for which you need special configuration.

        :param field_name:
        :param field_type: either a type, or a function that converts string to another value
        :param optional: If False, :func:`~trajtracker.data.CSVLoader.load_file` will fail if the field is missing.
s       """

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

        :return: list with one dict per row, transformed to the required types
        """

        _u.validate_func_arg_type(self, "load_file", "filename", filename, str)

        rows, fieldnames = self._read_data_from_file(filename)

        self._validate_field_names(fieldnames, filename)

        #-- Transform data
        result = []
        for row in rows:
            if not self._case_sensitive_col_names:
                row = self._transform_lowercase(row)
            row = self._transform_types(row)
            result.append(row)

        return result


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
            raise trajtracker.BadFormatError("An invalid field name ({:}) was found im {:} - this is a reserved field name".format(
                self.FLD_LINE_NUM, filename))

        for field in self._fields:
            if field not in fieldnames and not self._fields[field]['optional']:
                raise trajtracker.BadFormatError("Mandatory field '{:} is missing in file {:}".format(field, filename))


    #------------------------------------------------
    @staticmethod
    def _transform_lowercase(row):
        return dict([(k.lower(), row[k]) for k in row.keys()])


    #------------------------------------------------
    def _transform_types(self, row):

        for field in row:

            if field not in self._fields:
                continue

            field_type = self._fields[field]['type']

            if field_type != str:
                row[field] = field_type(row[field])

        return row
