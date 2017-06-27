"""
Show one or more stimuli of any type (e.g. for RSVP)

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

from __future__ import division

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.stimuli import BaseMultiStim


# noinspection PyProtectedMember
class MultiStimulus(BaseMultiStim):


    #----------------------------------------------------
    def __init__(self, available_stimuli=None, shown_stimuli=None, position=None,
                 onset_time=None, duration=None, last_stimulus_remains=False,
                 onset_event=None, terminate_event=ttrk.events.TRIAL_ENDED):
        """
        Called when creating a MultiStimulus object 
        
        :param available_stimuli: See :attr:`~trajtracker.stimuli.MultiStimulus.available_stimuli` 
        :param shown_stimuli:  See :attr:`~trajtracker.stimuli.MultiStimulus.shown_stimuli`
        :param position:  See :attr:`~trajtracker.stimuli.MultiStimulus.position`
        :param onset_time:  See :attr:`~trajtracker.stimuli.MultiStimulus.onset_time`
        :param duration:  See :attr:`~trajtracker.stimuli.MultiStimulus.duration`
        :param last_stimulus_remains:  See :attr:`~trajtracker.stimuli.MultiStimulus.last_stimulus_remains`
        :param onset_event:  See :attr:`~trajtracker.stimuli.MultiStimulus.onset_event`
        :param terminate_event:  See :attr:`~trajtracker.stimuli.MultiStimulus.terminate_event`
        """

        super(MultiStimulus, self).__init__(onset_time=onset_time, duration=duration,
                                            last_stimulus_remains=last_stimulus_remains)

        self._stimuli = []

        self.available_stimuli = available_stimuli
        self.shown_stimuli = shown_stimuli
        self.position = position

        if onset_event is not None:
            self.onset_event = onset_event

        self.terminate_event = terminate_event


    #----------------------------------------------------
    # Update the stimuli (before actually showing them)
    #
    def _configure_and_preload(self):
        self._log_func_enters("_configure_stimuli")
        self._validate()

        n_stim = len(self._shown_stimuli)

        self._stimuli = [self._available_stimuli[s_id] for s_id in self._shown_stimuli]

        self._set_stimuli_property("position", "coord", n_stim)


    #----------------------------------------------------
    # Validate that the MultiStimulus object is ready to go
    #
    def _validate(self):

        self._validate_property("shown_stimuli")

        missing_pics = [s_id for s_id in self._shown_stimuli if s_id not in self._available_stimuli]
        if len(missing_pics) > 0:
            raise ttrk.ValueError("shown_stimuli includes unknown stimulus IDs: {:}".format(
                ", ".join(missing_pics)))

        n_stim = len(self._shown_stimuli)
        self._validate_property("position", n_stim)
        self._validate_property("onset_time", n_stim)
        self._validate_property("duration", n_stim)


    #----------------------------------------------------
    def _value_type_desc(self):
        return "stim"


    #----------------------------------------------------
    def get_stimulus_desc(self, stimulus_num):
        """
        Get a description of one of the stimuli (e.g., the filename in case of a picture) 
        
        :param stimulus_num: The stimulus index
        :return: str 
        """
        if isinstance(self._stimuli[stimulus_num], xpy.stimuli.Picture):
            return self._stimuli[stimulus_num].filename
        else:
            return str(self._stimuli[stimulus_num])


    #----------------------------------------------------
    def _set_visible(self, stimulus_num, visible):
        super(MultiStimulus, self)._set_visible(stimulus_num, visible)

        #-- When setting the stimulus visible: update its position.
        #-- We do not update the position in advance, in case the same stimulus is shown
        #-- twice in the same trial, in different positions.
        if visible:
            self._stimuli[stimulus_num].position = \
                self._position[stimulus_num] if self._position_multiple else self._position


    #----------------------------------------------------
    @property
    def n_stim(self):
        return len(self._shown_stimuli)


    #==============================================================================
    #   Handle the list of available stimuli
    #==============================================================================


    #----------------------------------------------------
    @property
    def available_stimuli(self):
        """
        The pool of stimuli that can be presented. 
        
        :type: dict (key=string ID; value=an expyriment stimulus).
        """
        return dict(self._available_stimuli)

    @available_stimuli.setter
    def available_stimuli(self, value):
        _u.validate_attr_type(self, "available_stim", value, dict, none_allowed=True)

        value = {} if value is None else dict(value)   # fix/copy

        for stim_id, stim in value.items():
            _u.validate_attr_type(self, "available_stim(key)", stim_id, str)
            if "is_preloaded" not in dir(stim) or "present" not in dir(stim):
                raise ttrk.TypeError(
                    "Invalid stimulus in {:}.add_stimulus() - {:}".format(_u.get_type_name(self), stim))
            if not stim.is_preloaded:
                stim.preload()
            self._container.add(stim, stim_id, visible=False)

        self._available_stimuli = value


    #------------------------------------------------------------------
    def add_stimulus(self, stim_id, stimulus):
        """
        Add a stimulus to the set of available stimuli.
        
        :param stim_id: A logical name of the stimulus
        :type stim_id: str
        :param stimulus: an expyriment stimulus
        """

        _u.validate_func_arg_type(self, "add_stimulus", "stim_id", stim_id, str)
        if "is_preloaded" not in dir(stimulus) or "present" not in dir(stimulus):
            raise ttrk.TypeError("Invalid stimulus in {:}.add_stimulus() - {:}".format(_u.get_type_name(self), stimulus))

        if stim_id in self._available_stimuli and self._should_log(ttrk.log_warn):
            self._log_write(
                'WARNING: Stimulus "{:}" already exists in the {:}, definition will be overriden'.format(
                    stim_id, _u.get_type_name(self)))

        if not stimulus.is_preloaded:
            stimulus.preload()

        self._available_stimuli[stim_id] = stimulus
        self._container.add(stimulus, stim_id, visible=False)


    #==============================================================================
    #   Configure properties of Expyriment's stimuli
    #==============================================================================

    #-----------------------------------------------------------------
    @property
    def shown_stimuli(self):
        """ 
        The stimuli to show in the trial (a list of strings, each is the stimulus ID)
        """
        return self._shown_stimuli

    @shown_stimuli.setter
    def shown_stimuli(self, value):
        value = [] if value is None else value
        self._set_property("shown_stimuli", value, str, allow_single_value=False)
        self._log_property_changed("shown_stimuli")

        missing_stims = [id for id in self._shown_stimuli if id not in self._available_stimuli]
        if len(missing_stims) > 0:
            self._log_write_if(ttrk.log_warn, "WARNING: shown_stimuli includes unknown stimulus IDs: {:}".format(
                ", ".join(missing_stims)), True, True)
