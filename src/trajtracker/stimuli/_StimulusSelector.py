"""
Stimulus selector: show one of several stimuli

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

import expyriment

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u


# noinspection PyProtectedMember
class StimulusSelector(ttrk.TTrkObject, ttrk.events.OnsetOffsetObj):

    def __init__(self, stimuli=()):
        """
        Constructor - invoked when you create a new object by writing ChangingStimulus()

        :param stimuli: A list of stimuli to add. Each entry in the list is a (key, stimulus) pair -
                        see :func:`~trajtracker.stimuli.ChangingStimulus.add_stimulus`
        """

        super(StimulusSelector, self).__init__()

        self._active_key = None
        self._stimuli = {}

        for key, stim in stimuli:
            self.add_stimulus(key, stim)


    #--------------------------------------------------
    def add_stimulus(self, key, stim):
        """
        Add a stimulus

        :param key: Identifier (logical name) for this stimulus
        :param stim: The actual expyriment stimulus
        """
        self._stimuli[key] = stim


    #--------------------------------------------------
    def _get_stimulus(self, key):
        return self._stimuli[key]


    #--------------------------------------------------
    def activate(self, key):
        """
        Set one of the stimuli as the active one.

        :param key: The key of the stimulus, as set in :func:`~trajtracker.stimuli.ChangingStimulus.add_stimulus`
        """
        if key is None or key in self._stimuli:
            if self._should_log(ttrk.log_trace):
                self._log_write("Activate,{:}".format(key), True)
            self._active_key = key
        else:
            raise ttrk.ValueError("{:}.select(key={:}) - this stimulus was not defined".format(_u.get_type_name(self), key))


    #--------------------------------------------------
    @property
    def active_stimulus(self):
        """ Get the expyriment stimulus currently active """
        if self._active_key is None:
            return None
        else:
            return self._stimuli[self._active_key]

    @property
    def selected_key(self):
        return self._active_key

    #--------------------------------------------------
    def present(self, clear=True, update=True):
        """ 
        present the active stimulus
        :return: The function's running time
        """

        start_time = ttrk.utils.get_time()

        self._log_func_enters("present", [clear, update])

        s = self.active_stimulus
        if s is None:
            # Take care of the clear and update
            if clear:
                _u.display_clear()
            if update:
                _u.display_update()
        else:
            s.present(clear=clear, update=update)

        return ttrk.utils.get_time() - start_time


    #--------------------------------------------------
    @property
    def position(self):
        """ 
        The position of the active stimulus. When you update this, positions of *all* stimuli will be updated.  
        """
        s = self.active_stimulus
        return None if s is None else s.position

    @position.setter
    def position(self, value):
        value = _u.validate_attr_is_coord(self, "position", value, change_none_to_0=True)

        for s in self._stimuli.values():
            s.position = value

        self._log_property_changed("position", value)
