"""

TrajTracker - events package

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

"""


from ._Event import Event
from ._EventManager import EventManager
from ._OnsetOffsetObj import OnsetOffsetObj

#-- Predefined events
TRIAL_INITIALIZED = Event("TRIAL_INITIALIZED")
TRIAL_STARTED = Event("TRIAL_STARTED")

# End-of-trial events: you should only dispatch TRIAL_SUCCEEDED and TRIAL_ERROR; the
# TRIAL_ENDED event will be automatically dispatched just before them.
TRIAL_ENDED = Event("TRIAL_ENDED")
TRIAL_SUCCEEDED = Event("TRIAL_SUCCEEDED", TRIAL_ENDED)
TRIAL_FAILED = Event("TRIAL_ERROR", TRIAL_ENDED)
