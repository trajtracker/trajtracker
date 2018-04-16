"""
Show one or more texts in a text box (e.g. for RSVP)

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

import trajtracker
import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.stimuli import BaseMultiStim


#
# NOTE: Some of the functionality of the base class (BaseMultiStim) is tested only for the
#       MultiStimulus class, and not here
#

# noinspection PyProtectedMember
class MultiTextBox(BaseMultiStim):


    #----------------------------------------------------
    def __init__(self, texts=None, text_font="Arial", text_size=26, text_bold=False, text_italic=False, text_underline=False,
                 text_justification=1, text_colour=xpy.misc.constants.C_WHITE,
                 background_colour=xpy.misc.constants.C_BLACK, size=None, position=(0, 0),
                 onset_time=None, duration=None, last_stimulus_remains=False,
                 onset_event=None, terminate_event=ttrk.events.TRIAL_ENDED):

        super(MultiTextBox, self).__init__(onset_time=onset_time, duration=duration, last_stimulus_remains=last_stimulus_remains)

        self.texts = texts
        self.text_font = text_font
        self.text_size = text_size
        self.text_bold = text_bold
        self.text_italic = text_italic
        self.text_underline = text_underline
        self.text_justification = text_justification
        self.text_colour = text_colour
        self.background_colour = background_colour
        self.size = size
        self.position = position

        if onset_event is not None:
            self.onset_event = onset_event

        self.terminate_event = terminate_event

    #----------------------------------------
    # If not enough TextBoxes exist - create additional
    #
    def _create_stimuli(self):

        n_stim = len(self._texts)

        for i in range(len(self._stimuli), n_stim+1):
            is_multiple = self._is_multiple_values(self._size, "coord")
            stim = self._create_textbox(self._size[i] if is_multiple else self._size)
            self._stimuli.append(stim)
            self._container.add(stim, visible=False)

    def _create_textbox(self, size):
        return xpy.stimuli.TextBox("", size)

    #----------------------------------------------------
    # Update the stimuli (before actually showing them)
    #
    def _configure_and_preload(self):
        self._log_func_enters("_configure_stimuli")
        self._validate()

        n_stim = len(self._texts)

        for i in range(len(self._stimuli)):
            self._stimuli[i].unload()

        self._create_stimuli()

        self._set_stimulus_font(n_stim)
        self._set_stimuli_property("texts", str, n_stim, stim_prop_name="text")
        self._set_stimuli_property("text_bold", bool, n_stim)
        self._set_stimuli_property("text_size", int, n_stim)
        self._set_stimuli_property("text_italic", bool, n_stim)
        self._set_stimuli_property("text_underline", bool, n_stim)
        self._set_stimuli_property("text_justification", str, n_stim)
        self._set_stimuli_property("text_colour", trajtracker.TYPE_RGB, n_stim)
        self._set_stimuli_property("background_colour", trajtracker.TYPE_RGB, n_stim)
        self._set_stimuli_property("size", "coord", n_stim)
        self._set_stimuli_property("position", "coord", n_stim)

        for i in range(len(self._texts)):
            self._stimuli[i].preload()


    #----------------------------------------------------
    # Validate that the MultiTextBox object is ready to go
    #
    def _validate(self):

        n_stim = len(self._texts)
        self._validate_property("texts")
        self._validate_property("text_font", n_stim)
        self._validate_property("text_size", n_stim)
        self._validate_property("text_bold", n_stim)
        self._validate_property("text_italic", n_stim)
        self._validate_property("text_underline", n_stim)
        self._validate_property("text_justification", n_stim)
        self._validate_property("text_colour", n_stim)
        self._validate_property("background_colour", n_stim)
        self._validate_property("size", n_stim)
        self._validate_property("position", n_stim)
        self._validate_property("onset_time", n_stim)
        self._validate_property("duration", n_stim)


    #------------------------------------------
    def _set_stimulus_font(self, n_stim):

        if self._is_multiple_values(self._text_font, str):
            fonts = [xpy.misc.find_font(f) for f in self._text_font]
        else:
            fonts = [xpy.misc.find_font(self._text_font)] * n_stim

        for i in range(n_stim):
            self._stimuli[i].text_font = fonts[i]


    #----------------------------------------------------
    def _value_type_desc(self):
        return "text"


    #----------------------------------------------------
    def get_stimulus_desc(self, stimulus_num):
        """
        Get one of the stimuli (= the text presented)

        :param stimulus_num: The index of the text to return
        :return: str 
        """
        return self._texts[stimulus_num]


    #----------------------------------------------------
    @property
    def n_stim(self):
        return len(self._texts)


    #----------------------------------------
    @property
    def stim_visibility(self):
        """
        Return an array of booleans, indicating whether each stimulus is presently visible or not.
        The array has as many elements as :attr:`~trajtracker.stimuli.MultiTextBox.text`
        """
        self._create_stimuli()
        return super(MultiTextBox, self).stim_visibility


    #==============================================================================
    #   Configure properties of Expyriment's TextBox
    #==============================================================================

    #-----------------------------------------------------------------
    @property
    def texts(self):
        """ 
        The texts to show (a list of strings)
        """
        return self._texts

    @texts.setter
    def texts(self, value):
        self._set_property("texts", value, str, allow_single_value=False)
        self._log_property_changed("texts")

    #-----------------------------------------------------------------
    @property
    def text_font(self):
        """ 
        The font name (str) 
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_font

    @text_font.setter
    def text_font(self, value):
        self._set_property("text_font", value, str)
        self._log_property_changed("text_font")

    #-----------------------------------------------------------------
    @property
    def text_size(self):
        """ 
        The font size (int) 
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_size

    @text_size.setter
    def text_size(self, value):
        self._set_property("text_size", value, int)
        self._log_property_changed("text_size")

    #-----------------------------------------------------------------
    @property
    def text_bold(self):
        """ 
        Whether the text is bold (bool) 
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_bold

    @text_bold.setter
    def text_bold(self, value):
        self._set_property("text_bold", value, bool, allow_none=False)
        self._log_property_changed("text_bold")

    #-----------------------------------------------------------------
    @property
    def text_italic(self):
        """ 
        Whether the text is in italic font (bool) 
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_italic

    @text_italic.setter
    def text_italic(self, value):
        self._set_property("text_italic", value, bool, allow_none=False)
        self._log_property_changed("text_italic")

    #-----------------------------------------------------------------
    @property
    def text_underline(self):
        """
        Whether the text is underlined (bool)
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_underline

    @text_underline.setter
    def text_underline(self, value):
        self._set_property("text_underline", value, bool, allow_none=False)
        self._log_property_changed("text_underline")

    #-----------------------------------------------------------------
    @property
    def text_justification(self):
        """
        The horizontal justification of the text. 0=left, 1=center, 2=right.
        This can be either a single value or a list of values, one per shown text
        """
        return self._text_justification

    @text_justification.setter
    def text_justification(self, value):
        self._set_property("text_justification", value, int)
        self._log_property_changed("text_justification")

    #-----------------------------------------------------------------
    @property
    def text_colour(self):
        """
        The color of the text to show. This can be either a single tuple (RGB) or a list of 
        tuples, one per shown text
        """
        return self._text_colour

    @text_colour.setter
    def text_colour(self, value):
        self._set_property("text_colour", value, trajtracker.TYPE_RGB)
        self._log_property_changed("text_colour")

    #-----------------------------------------------------------------
    @property
    def background_colour(self):
        """
        The background color TextBox. This can be either a single tuple (RGB) or a list of 
        tuples, one per shown text
        """
        return self._background_colour

    @background_colour.setter
    def background_colour(self, value):
        self._set_property("background_colour", value, trajtracker.TYPE_RGB)
        self._log_property_changed("background_colour")

    #-----------------------------------------------------------------
    @property
    def size(self):
        """
        The size of the TextBox (width,height). This can be either a single tuple or a list of 
        tuples, one per shown text
        """
        return self._size

    @size.setter
    def size(self, value):
        self._set_property("size", value, "coord")
        self._log_property_changed("size")
