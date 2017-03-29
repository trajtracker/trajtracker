"""

Exception class, thrown by validators when they fail

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""



class ValidationFailed(BaseException):

    """ An application validation has failed """


    def __init__(self, err_code, message, validator, err_args=None):
        self._err_code = err_code
        self._message = message
        self._validator = validator
        self._args = {} if err_args is None else err_args


    @property
    def err_code(self):
        return self._err_code

    @property
    def message(self):
        return self._message

    @property
    def validator(self):
        return self._validator


    def arg(self, arg_name):
        if arg_name not in self._args:
            raise AttributeError("Argument '{0}' does not exist in this exception".format(arg_name))
        return self._args[arg_name]


