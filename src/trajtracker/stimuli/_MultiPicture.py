"""

Show one or more pictures (e.g. for RSVP)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import expyriment as xpy
from expyriment.stimuli import Picture

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.stimuli import BaseMultiStim


# noinspection PyProtectedMember
class MultiPicture(BaseMultiStim):


    #----------------------------------------------------
    def __init__(self, available_pictures=None, shown_pictures=None, position=None,
                 onset_time=None, duration=None, last_stimulus_remains=False,
                 onset_event=None, terminate_event=ttrk.events.TRIAL_ENDED):

        super(MultiPicture, self).__init__(onset_time=onset_time, duration=duration,
                                           last_stimulus_remains=last_stimulus_remains)

        self._stimuli = []

        self.available_pictures = available_pictures
        self.shown_pictures = shown_pictures
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

        n_stim = len(self._shown_pictures)

        self._stimuli = [self._available_pictures[pic_id] for pic_id in self._shown_pictures]

        self._set_stimuli_property("position", "coord", n_stim)


    #----------------------------------------------------
    # Validate that the MultiPicture object is ready to go
    #
    def _validate(self):

        self._validate_property("shown_pictures")

        missing_pics = [pic_id for pic_id in self._shown_pictures if pic_id not in self._available_pictures]
        if len(missing_pics) > 0:
            raise ttrk.ValueError("shown_pictures includes unknown picture IDs: {:}".format(
                ", ".join(missing_pics)))

        n_stim = len(self._shown_pictures)
        self._validate_property("position", n_stim)
        self._validate_property("onset_time", n_stim)
        self._validate_property("duration", n_stim)


    #----------------------------------------------------
    def _value_type_desc(self):
        return "picture"


    #----------------------------------------------------
    def _stimulus_to_string(self, stimulus_num):
        return self._stimuli[stimulus_num].filename


    #----------------------------------------------------
    def _set_visible(self, stimulus_num, visible):
        super(MultiPicture, self)._set_visible(stimulus_num, visible)

        #-- When setting the stimulus visible: update its position.
        #-- We do not update the position in advance, in case the same picture is shown
        #-- twice in the same trial, in different positions.
        if visible:
            self._stimuli[stimulus_num].position = \
                self._position[stimulus_num] if self._position_multiple else self._position


    #----------------------------------------------------
    @property
    def n_stim(self):
        return len(self._shown_pictures)


    #==============================================================================
    #   Handle the list of available pictures
    #==============================================================================


    #----------------------------------------------------
    @property
    def available_pictures(self):
        """
        The pool of pictures that can be presented. 
        
        :type: dict (key=string ID; value=expyriment.stimuli.Picture object).
        """
        return dict(self._available_pictures)

    @available_pictures.setter
    def available_pictures(self, value):
        _u.validate_attr_type(self, "available_pictures", value, dict, none_allowed=True)

        value = {} if value is None else dict(value)   # fix/copy

        for pic_id, picture in value.items():
            _u.validate_attr_type(self, "available_pictures(key)", pic_id, str)
            _u.validate_attr_type(self, "available_pictures(key)", picture, Picture)
            if not picture.is_preloaded:
                picture.preload()
            self._container.add(picture, pic_id, visible=False)

        self._available_pictures = value


    #------------------------------------------------------------------
    def add_picture(self, pic_id, picture):
        """
        Add a picture to the set of available pictures.
        
        :param pic_id: A logical name of the picture
        :type pic_id: str
        :type picture: expyriment.stimuli.Picture
        """

        _u.validate_func_arg_type(self, "add_picture", "pic_id", pic_id, str)
        _u.validate_func_arg_type(self, "add_picture", "picture", picture, Picture)

        if pic_id in self._available_pictures and self._should_log(ttrk.log_warn):
            self._log_write(
                'WARNING: Picture "{:}" already exists in the {:}, definition will be overriden'.format(
                    pic_id, _u.get_type_name(self)))

        if not picture.is_preloaded:
            picture.preload()

        self._available_pictures[pic_id] = picture
        self._container.add(picture, pic_id, visible=False)


    #==============================================================================
    #   Configure properties of Expyriment's Picture
    #==============================================================================

    #-----------------------------------------------------------------
    @property
    def shown_pictures(self):
        """ 
        The pictures to show in the trial (a list of strings, each is the ID of a picture)
        """
        return self._shown_pictures

    @shown_pictures.setter
    def shown_pictures(self, value):
        self._set_property("shown_pictures", value, str, allow_single_value=False)
        self._log_property_changed("shown_pictures")

        if self._shown_pictures is not None:
            missing_pics = [pic_id for pic_id in self._shown_pictures if pic_id not in self._available_pictures]
            if len(missing_pics) > 0:
                self._log_write_if(ttrk.log_warn, "WARNING: shown_pictures includes unknown picture IDs: {:}".format(
                    ", ".join(missing_pics)), True, True)
