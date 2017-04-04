"""

TrajTracker - events package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""


from _Event import Event
from _OnsetOffsetObj import OnsetOffsetObj

#-- Predefined events
TRIAL_STARTS = Event("TRIAL_STARTS")
TRIAL_SUCCEEDED = Event("TRIAL_SUCCEEDED")
TRIAL_ERROR = Event("TRIAL_ERROR")
