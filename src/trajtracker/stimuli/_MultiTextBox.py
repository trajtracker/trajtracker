"""

Show one or more texts in a text box (e.g. for RSVP)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers
import numpy as np
from operator import itemgetter

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.data import fromXML
from trajtracker.stimuli import BaseMultiStim, StimulusContainer


#todo add documentation

# noinspection PyProtectedMember
class MultiTextBox(BaseMultiStim):


    #----------------------------------------------------
    def __init__(self, text=None, text_font="Arial", text_size=26, text_bold=False, text_italic=False, text_underline=False,
                 text_justification=1, text_colour=xpy.misc.constants.C_WHITE,
                 background_colour=xpy.misc.constants.C_BLACK, size=None, position=(0, 0),
                 onset_time=None, duration=None, last_stimulus_remains=False,
                 onset_event=None, terminate_event=ttrk.events.TRIAL_ENDED):

        super(MultiTextBox, self).__init__(onset_time=onset_time, duration=duration, last_stimulus_remains=last_stimulus_remains)

        self._stimuli = []
        self._container = StimulusContainer("MultiTextBox")
        self._event_manager = None

        self.texts = text
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
    @property
    def stimulus(self):
        """
        A single stimulus that represents all the stimuli in this MultiTextBox
        :type: StimulusContainer
        """
        return self._container

    #----------------------------------------
    @property
    def stim_visibility(self):
        """
        Return an array of booleans, indicating whether each stimulus is presently visible or not.
        The array has as many elements as :attr:`~trajtracker.stimuli.MultiTextBox.text`
        """
        n_stim = len(self._texts)
        self._create_stimuli()
        return [self._stimuli[i].visible for i in range(n_stim)]


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
        self._set_stimuli_property("text_colour", "RGB", n_stim)
        self._set_stimuli_property("background_colour", "RGB", n_stim)
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


    #----------------------------------------------------
    # Validate that one property is defined OK
    #
    def _validate_property(self, prop_name, n_stim=0):

        value = getattr(self, prop_name)
        if value is None:
            raise ttrk.ValueError('{:}.{:} was not set'.format(type(self).__name__, prop_name))

        is_multiple_values = getattr(self, "_" + prop_name + "_multiple")
        if is_multiple_values and len(value) < n_stim:
            raise ttrk.ValueError('{:}.{:} has {:} values, but there are {:} texts to present'.format(
                type(self).__name__, prop_name, len(value), n_stim))

    #----------------------------------------------------
    # Set a single property of all self._stimuli
    #
    def _set_stimuli_property(self, prop_name, prop_type, n_stim, stim_prop_name=None):

        if stim_prop_name is None:
            stim_prop_name = prop_name

        values = getattr(self, prop_name)
        if not self._is_multiple_values(values, prop_type):
            values = [values] * n_stim

        for i in range(n_stim):
            setattr(self._stimuli[i], stim_prop_name, values[i])

    #------------------------------------------
    def _set_stimulus_font(self, n_stim):

        if self._is_multiple_values(self._text_font, str):
            fonts = [xpy.misc.find_font(f) for f in self._text_font]
        else:
            fonts = [xpy.misc.find_font(self._text_font)] * n_stim

        for i in range(n_stim):
            self._stimuli[i].text_font = fonts[i]


    #==============================================================================
    #  For working with events: no public API
    #==============================================================================

    #----------------------------------------------------
    # Initialize everything for a specific trial
    #
    def _init_trial_events(self):
        self._log_func_enters("_init_trial_events")

        if self._onset_event is None:
            raise ttrk.ValueError('{:}.onset_event was not set'.format(type(self).__name__))

        self._configure_and_preload()

        n_stim = len(self._texts)

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)

        op_ids = set()

        for i in range(n_stim):
            onset_event = self._onset_event + self._onset_time[i]
            id1 = self._event_manager.register_operation(event=onset_event,
                                                         recurring=False,
                                                         description="Show text[{:}]({:})".format(i, self._texts[i]),
                                                         operation=TextboxEnableDisableOp(self, self._stimuli[i], True, i),
                                                         cancel_pending_operation_on=self.terminate_event)
            op_ids.add(id1)

            if i == n_stim - 1 and self._last_stimulus_remains:
                break

            offset_event = self._onset_event + self._onset_time[i] + duration[i]
            id2 = self._event_manager.register_operation(event=offset_event,
                                                         recurring=False,
                                                         description="Hide text[{:}]({:})".format(i, self._texts[i]),
                                                         operation=TextboxEnableDisableOp(self, self._stimuli[i], False, i),
                                                         cancel_pending_operation_on=self.terminate_event)
            op_ids.add(id2)

        self._registered_ops = op_ids

        if self.terminate_event is not None:
            self._event_manager.register_operation(event=self.terminate_event,
                                                   recurring=False,
                                                   description="Terminate MultiText",
                                                   operation=lambda t1, t2: self._terminate_display())


    #----------------------------------------------------
    # (when the event ends) if not all texts were displayed, terminate whatever remained
    #
    def _terminate_display(self):
        self._log_func_enters("_terminate_display")
        self._event_manager.unregister_operation(self._registered_ops, warn_if_op_missing=False)
        for stim in self._stimuli:
            stim.visible = False


    #==============================================================================
    #   API for working without events
    #==============================================================================

    #----------------------------------------------------
    def init_for_trial(self):
        """
        Initialize when a trial starts.
        
        Do not use this function if you are working with the events mechanism. 
        """

        self._log_func_enters("init_for_trial")
        if self._event_manager is not None:
            self._log_write_if(ttrk.log_warn, "init_for_trial() was called although the {:} was registered to an event manager".format(
                type(self).__name__))

        self._configure_and_preload()

        n_stim = len(self._texts)

        show_ops = zip(self._onset_time[:n_stim], [True] * n_stim, range(n_stim))

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)
        offset_times = [self._onset_time[i] + duration[i] for i in range(n_stim)]
        hide_ops = zip(offset_times, [False] * n_stim, range(n_stim))
        if self._last_stimulus_remains:
            hide_ops = hide_ops[:-1]  # don't hide the last one

        self._show_hide_operations = sorted(show_ops + hide_ops, key=itemgetter(0))
        self._start_showing_time = None


    #----------------------------------------------------
    def start_showing(self, time):
        """
        *When working without events:* this sets time=0 for the texts to show (i.e., the
        :attr:`~trajtracker.stimuli.MultiTextBox.onset_time` are relatively to this time point).

        This function will also invoke :func:`~trajtracker.stimuli.MultiTextBox.update_display`.

        Do not use this function if you are working with the events mechanism.
         
        :param time: The time in the current session/trial. This must be synchronized with the "time"
                     argument of :func:`~trajtracker.stimuli.MultiTextBox.update_display`
        """

        self._log_func_enters("start_showing", (time))
        if self._event_manager is not None:
            self._log_write_if(ttrk.log_warn,
                               "start_showing() was called although the {:} was registered to an event manager".format(
                                   type(self).__name__))

        self._start_showing_time = time
        self.update_display(time)


    #----------------------------------------------------
    def update_display(self, time):
        """
        Set relevant stimuli as visible/invisible.

        Do not use this function if you are working with the events mechanism.
         
        :param time: The time in the current session/trial. This must be synchronized with the "time"
                     argument of :func:`~trajtracker.stimuli.MultiTextBox.start_showing`
        """

        while (len(self._show_hide_operations) > 0 and
               time >= self._start_showing_time + self._show_hide_operations[0][0]):

            operation = self._show_hide_operations.pop(0)
            stim_num = operation[2]
            visible = operation[1]

            if self._should_log(ttrk.log_trace):
                self._log_write("{:} stimulus #{:} ({:})".format(
                    "showing" if visible else "hiding", stim_num, self._texts[stim_num]))
            self._stimuli[stim_num].visible = visible


    #==============================================================================
    #   Configure properties of Expyriment's TextBox
    #==============================================================================

    #-----------------------------------------------------------------
    @property
    def texts(self):
        return self._texts

    @texts.setter
    @fromXML(_u.parse_scalar_or_list(str))
    def texts(self, value):
        self._set_property("texts", value, str, allow_single_value=False)
        self._log_property_changed("texts")

    #-----------------------------------------------------------------
    @property
    def text_font(self):
        return self._text_font

    @text_font.setter
    @fromXML(_u.parse_scalar_or_list(str))
    def text_font(self, value):
        self._set_property("text_font", value, str)
        self._log_property_changed("text_font")

    #-----------------------------------------------------------------
    @property
    def text_size(self):
        """ The font size (int) """
        return self._text_size

    @text_size.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def text_size(self, value):
        self._set_property("text_size", value, int)
        self._log_property_changed("text_size")

    #-----------------------------------------------------------------
    @property
    def text_bold(self):
        """ Whether the text is bold (bool) """
        return self._text_bold

    @text_bold.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_bold(self, value):
        self._set_property("text_bold", value, bool, allow_none=False)
        self._log_property_changed("text_bold")

    #-----------------------------------------------------------------
    @property
    def text_italic(self):
        """ Whether the text is in italic font (bool) """
        return self._text_italic

    @text_italic.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_italic(self, value):
        self._set_property("text_italic", value, bool, allow_none=False)
        self._log_property_changed("text_italic")

    #-----------------------------------------------------------------
    @property
    def text_underline(self):
        """ Whether the text is underlined (bool) """
        return self._text_underline

    @text_underline.setter
    @fromXML(_u.parse_scalar_or_list(bool))
    def text_underline(self, value):
        self._set_property("text_underline", value, bool, allow_none=False)
        self._log_property_changed("text_underline")

    #-----------------------------------------------------------------
    @property
    def text_justification(self):
        """ The horizontal justification of the text. 0=left, 1=center, 2=right. """
        return self._text_justification

    @text_justification.setter
    def text_justification(self, value):
        self._set_property("text_justification", value, int)
        self._log_property_changed("text_justification")

    #-----------------------------------------------------------------
    @property
    def text_colour(self):
        return self._text_colour

    @text_colour.setter
    @fromXML(_u.parse_scalar_or_list(_u.parse_rgb))
    def text_colour(self, value):
        self._set_property("text_colour", value, "RGB")
        self._log_property_changed("text_colour")

    #-----------------------------------------------------------------
    @property
    def background_colour(self):
        return self._background_colour

    @background_colour.setter
    @fromXML(_u.parse_scalar_or_list(_u.parse_rgb))
    def background_colour(self, value):
        self._set_property("background_colour", value, "RGB")
        self._log_property_changed("background_colour")

    #-----------------------------------------------------------------
    @property
    def size(self):
        return self._size

    @size.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def size(self, value):
        self._set_property("size", value, "coord")
        self._log_property_changed("size")

    #-----------------------------------------------------------------
    @property
    def position(self):
        return self._position

    @position.setter
    @fromXML(_u.parse_scalar_or_list(int))
    def position(self, value):
        self._set_property("position", value, "coord")
        self._log_property_changed("position")


    #-----------------------------------------------------------------
    def _update_stimuli(self, prop_name, value):

        if multiple_values:
            value_per_stim = value
        else:
            value_per_stim = [value] * len(self._stimuli)

        for i in range(len(self._stimuli)):
            setattr(self._stimuli[i], prop_name, value_per_stim[i])



#=====================================================================
# The operation that is registered to the event manager
#
class TextboxEnableDisableOp(object):

    #---------------------------------
    def __init__(self, multi_text_box, stimulus, visible, stimulus_num):
        self._multi_text_box = multi_text_box
        self._stimulus = stimulus
        self._visible = visible
        self._stimulus_num = stimulus_num

    #---------------------------------
    def __call__(self, *args, **kwargs):
        self._multi_text_box._log_write_if(ttrk.log_info, "Set text#{:} ({:}) {:}".format(
            self._stimulus_num, self._stimulus.text, "visible" if self._visible else "invisible"))

        self._stimulus.visible = self._visible

    #---------------------------------
    def __str__(self):
        return "Text #{:} ({:})".format(self._stimulus_num, self._stimulus.text)
