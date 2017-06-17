"""
This module has functions to support the discrete-choice paradigm

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from ._Config import Config
from ._ExperimentInfo import ExperimentInfo
from ._TrialInfo import TrialInfo


from ._dc_init import \
    create_experiment_objects, \
    create_response_buttons, \
    load_data_source

