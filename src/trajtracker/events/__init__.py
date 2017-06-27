"""

TrajTracker - events package

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
