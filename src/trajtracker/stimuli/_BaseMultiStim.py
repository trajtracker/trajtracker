"""

Base class for showing multiple stimuli (e.g., RSVP)

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers
import numpy as np
from operator import itemgetter

from expyriment.misc.geometry import XYPoint

import trajtracker
import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.events import Event
from trajtracker.events import TRIAL_INITIALIZED, TRIAL_ENDED


# noinspection PyProtectedMember
class BaseMultiStim(ttrk.TTrkObject):


    def __init__(self, onset_time=None, duration=None, last_stimulus_remains=False):

        super(BaseMultiStim, self).__init__()

        self._event_manager = None
        self._registered_ops = []
        self.trial_configured_event = TRIAL_INITIALIZED
        self.onset_event = None
        self.terminate_event = TRIAL_ENDED

        self.onset_time = onset_time
        self.duration = duration
        self.last_stimulus_remains = last_stimulus_remains

        self._stimuli = []
        self._container = ttrk.stimuli.StimulusContainer(_u.get_type_name(self))

        self._onset_offset_callbacks = []


    #----------------------------------------------------
    # Validate that one property is defined OK
    #
    def _validate_property(self, prop_name, n_stim=0):

        value = getattr(self, prop_name)
        if value is None:
            raise ttrk.ValueError('{:}.{:} was not set'.format(_u.get_type_name(self), prop_name))

        is_multiple_values = getattr(self, "_" + prop_name + "_multiple")
        if is_multiple_values and len(value) < n_stim:
            raise ttrk.ValueError('{:}.{:} has {:} values, but there are {:} values to present'.format(
                _u.get_type_name(self), prop_name, len(value), n_stim))


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

    #-----------------------------------------------------------------
    # Propagate a "MultiStim" property to properties of the underlying stimuli (in self._stimuli)
    #
    def _update_stimuli(self, prop_name, value):

        if multiple_values:
            value_per_stim = value
        else:
            value_per_stim = [value] * len(self._stimuli)

        for i in range(len(self._stimuli)):
            setattr(self._stimuli[i], prop_name, value_per_stim[i])

    #----------------------------------------------------
    def _value_type_desc(self):
        return "value"


    #---------------------------------------------------
    def _set_visible(self, stimulus_num, visible):

        self._log_write_if(ttrk.log_debug, "Set stimulus #{:} to {:}".format(stimulus_num, "visible" if visible else "invisible"), prepend_self=True)

        self._stimuli[stimulus_num].visible = visible

        callback_funcs = list(self._onset_offset_callbacks)  # take a snapshot copy of the list's present state

        def on_stim_container_presented(sc, ids, present_time):
            for func in callback_funcs:
                func(self, stimulus_num, visible, present_time)

        self._container.register_callback(on_stim_container_presented)


    #---------------------------------------------------
    def register_onset_offset_callback_func(self, func):
        """
        Register a function that should be called when a stimulus is shown/hidden
         
        :param func: The function, which gets 4 parameters:
            
            1. The MultiStimulus/MultiTextBox object
            2. The stimulus/text number (0=first)
            3. Whether the stimulus is presented (True) or hidden (False)
            4. The time when the corresponding present() function returned 
        """
        _u.validate_func_arg_type(self, "add_onset_offset_callback_func", "func", func, ttrk.TYPE_CALLABLE)
        self._onset_offset_callbacks.append(func)

    #---------------------------------------------------
    def unregister_onset_offset_callback_func(self, func):
        """
        Unegister a callback function previously registered with unregister_onset_offset_callback_func() 
         
        :param func: The function
        """
        exists = func in self._onset_offset_callbacks.append
        if exists:
            self._onset_offset_callbacks.append.remove(func)
        return exists


    #==============================================================================
    #   Show / hide
    #==============================================================================

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
        The array has as many elements as the number of stimuli (text/picture) presented.
        """
        return [self._stimuli[i].visible for i in range(self.n_stim)]


    #==============================================================================
    #  For working with events: no public API
    #==============================================================================

    #----------------------------------------------------
    def on_registered(self, event_manager):
        self._event_manager = event_manager

        #-- Whenever the trial starts: register specifc events
        event_manager.register_operation(event=self._trial_configured_event,
                                         operation=lambda t1, t2: self._init_trial_events(),
                                         recurring=True,
                                         description="Setup {:}".format(_u.get_type_name(self)))


    #----------------------------------------------------
    # Initialize everything for a specific trial
    #
    def _init_trial_events(self):
        self._log_func_enters("_init_trial_events")

        if self._onset_event is None:
            raise ttrk.ValueError('{:}.onset_event was not set'.format(_u.get_type_name(self)))

        n_stim = self.n_stim
        self._configure_and_preload()

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)

        op_ids = set()

        for i in range(n_stim):
            onset_event = self._onset_event + self._onset_time[i]
            op = StimulusEnableDisableOp(self, i, True)
            id1 = self._event_manager.register_operation(event=onset_event, recurring=False,
                                                         description=str(op), operation=op,
                                                         cancel_pending_operation_on=self.terminate_event)
            op_ids.add(id1)

            if i == n_stim - 1 and self._last_stimulus_remains:
                break

            offset_event = self._onset_event + self._onset_time[i] + duration[i]
            op = StimulusEnableDisableOp(self, i, False)
            id2 = self._event_manager.register_operation(event=offset_event, recurring=False,
                                                         description=str(op), operation=op,
                                                         cancel_pending_operation_on=self.terminate_event)
            op_ids.add(id2)

        self._registered_ops = op_ids

        if self._terminate_event is not None:
            self._event_manager.register_operation(event=self._terminate_event,
                                                   recurring=False,
                                                   description="Terminate " + _u.get_type_name(self),
                                                   operation=lambda t1, t2: self.terminate_display())


    #----------------------------------------------------
    # (when the event ends) if not all texts were displayed, terminate whatever remained
    #
    def terminate_display(self):
        self._log_func_enters("_terminate_display")
        self._event_manager.unregister_operation(self._registered_ops, warn_if_op_missing=False)
        for i in range(len(self._stimuli)):
            self._set_visible(i, False)

    #==============================================================================
    #   API for working without events
    #==============================================================================

    # ----------------------------------------------------
    def init_for_trial(self):
        """
        Initialize when a trial starts.

        Do not use this function if you are working with the events mechanism. 
        """

        self._log_func_enters("init_for_trial")
        if self._event_manager is not None:
            self._log_write_if(ttrk.log_warn,
                               "init_for_trial() was called although the {:} was registered to an event manager".format(
                                   _u.get_type_name(self)))

        self._configure_and_preload()

        n_stim = self.n_stim

        show_ops = list(zip(self._onset_time[:n_stim], [True] * n_stim, range(n_stim)))

        duration = self._duration if self._duration_multiple else ([self._duration] * n_stim)
        offset_times = [self._onset_time[i] + duration[i] for i in range(n_stim)]
        hide_ops = list(zip(offset_times, [False] * n_stim, range(n_stim)))
        if self._last_stimulus_remains:
            hide_ops = hide_ops[:-1]  # don't hide the last one

        self._show_hide_operations = sorted(show_ops + hide_ops, key=itemgetter(0))
        self._start_showing_time = None

    # ----------------------------------------------------
    def start_showing(self, time):
        """
        *When working without events:* this sets time=0 for the texts to show (i.e., the
        :attr:`~trajtracker.stimuli.MultiTextBox.onset_time` are relatively to this time point).

        This function will also invoke :func:`~trajtracker.stimuli.MultiTextBox.update_display`.

        Do not use this function if you are working with the events mechanism.

        :param time: The time in the current session/trial. This must be synchronized with the "time"
                     argument of :func:`~trajtracker.stimuli.MultiTextBox.update_display`
        """

        self._log_func_enters("start_showing", [time])
        if self._event_manager is not None:
            self._log_write_if(ttrk.log_warn,
                               "start_showing() was called although the {:} was registered to an event manager".format(
                                   _u.get_type_name(self)))

        self._start_showing_time = time
        self.update_display(time)

    # ----------------------------------------------------
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
            self._set_visible(stim_num, visible)


    #==============================================================================
    #   Configuration
    #==============================================================================

    #----------------------------------------------------
    @property
    def trial_configured_event(self):
        """
        An event indicating the time when the per-trial information was configured.
        By default, this is the TRIAL_INIITALIZED event.

        **Note:**

        - This property is relevant only when working with events (and with an :class:`~trajtracker.events.EventManager`)
        - The property cannot be changed after the object was registered to an :class:`~trajtracker.events.EventManager`
        """
        return self._trial_configured_event

    @trial_configured_event.setter
    def trial_configured_event(self, event):
        _u.validate_attr_type(self, "registration_event", event, Event)
        if self._event_manager is not None:
            raise ttrk.InvalidStateError(("{:}.trial_configured_event cannot be changed after " +
                                          "registering to the event manager".format(_u.get_type_name(self))))
        self._trial_configured_event = event
        self._log_property_changed("trial_configured_event")


    #----------------------------------------------------
    @property
    def onset_event(self):
        """
        The event which serves as a reference point for displaying stimul. All onset_time's are indicated
        relatively to this event.

        **Note:** This property is relevant only when working with events (with an
        :class:`~trajtracker.events.EventManager`)
        """
        return self._onset_event

    @onset_event.setter
    def onset_event(self, event):
        _u.validate_attr_type(self, "onset_event", event, Event, none_allowed=True)
        self._onset_event = event
        self._log_property_changed("onset_event")


    #----------------------------------------------------
    @property
    def terminate_event(self):
        """
        An event that terminates the display of stimuli, including the display of stimuli that are
        still scheduled to appear. Default: TRIAL_ENDED.

        You can set to None to disable termination; however, note that in this case you might get strange
        behavior if the next trial starts while the stimuli are still being shown. To prevent this, you'll have to
        take care yourself of cleaning up pending operations from the event manager.

        **Note:** This property is relevant only when working with events (and with an
        :class:`~trajtracker.events.EventManager`)
        """
        return self._terminate_event

    @terminate_event.setter
    def terminate_event(self, event):
        _u.validate_attr_type(self, "terminate_event", event, Event, none_allowed=True)
        self._terminate_event = event
        self._log_property_changed("terminate_event")


    #----------------------------------------------------
    @property
    def onset_time(self):
        """
        The onset time of each stimulus, relatively to the **onset_event**.
        
        :type: list/tuple of numbers 
        """
        return self._onset_time

    @onset_time.setter
    def onset_time(self, value):

        if value is not None:
            _u.validate_attr_is_collection(self, "onset_time", value, min_length=1)
            for i in range(len(value)):
                _u.validate_attr_numeric(self, "onset_time[%d]" % i, value[i])
                _u.validate_attr_not_negative(self, "onset_time[%d]" % i, value[i])

        self._onset_time = value
        self._onset_time_multiple = True
        self._log_property_changed("onset_time")


    #----------------------------------------------------
    @property
    def duration(self):
        """
        The duration of showing each stimulus.
        
        A stimulus disappears when the duration expired or when a **terminate_event** was dispatched.

        :type: list/tuple of numbers 
        """
        return self._duration

    @duration.setter
    def duration(self, value):

        is_multiple = False

        if isinstance(value, numbers.Number):
            _u.validate_attr_positive(self, "duration", value)

        elif value is not None:
            is_multiple = True
            _u.validate_attr_is_collection(self, "duration", value, min_length=1)
            for i in range(len(value)):
                _u.validate_attr_numeric(self, "duration[%d]" % i, value[i])
                _u.validate_attr_positive(self, "duration[%d]" % i, value[i])

        self._duration = value
        self._duration_multiple = is_multiple
        self._log_property_changed("duration")


    #----------------------------------------------------
    @property
    def last_stimulus_remains(self):
        """
        Whether the last stimulus presented in the sequence should remain on screen (True), or has
        a limited duration similarly to the previous stimuli (False)
        """
        return self._last_stimulus_remains

    @last_stimulus_remains.setter
    def last_stimulus_remains(self, value):
        _u.validate_attr_type(self, "last_stimulus_remains", value, bool)
        self._last_stimulus_remains = value
        self._log_property_changed("last_stimulus_remains")


    #-----------------------------------------------------------------
    @property
    def position(self):
        """
        The position of the stimuli to show (x,y). This can be either a single tuple or a list of 
        tuples, one per shown value
        """
        return self._position

    @position.setter
    def position(self, value):
        self._set_property("position", value, trajtracker.TYPE_COORD)
        self._log_property_changed("position")

    #==============================================================================
    #   Misc.
    #==============================================================================

    #-----------------------------------------------------------------
    def _is_multiple_values(self, value, prop_type):

        if type(prop_type) == type:
            return isinstance(value, (tuple, list, np.ndarray))
        elif prop_type == trajtracker.TYPE_RGB:
            return isinstance(value, (tuple, list, np.ndarray)) and \
                    (len(value) == 0 or u.is_rgb(value[0]))
        elif prop_type == trajtracker.TYPE_COORD:
            return isinstance(value, (tuple, list, np.ndarray)) and \
                    (len(value) == 0 or isinstance(value[0], (tuple, list, XYPoint, np.ndarray)))
        else:
            raise Exception("Trajtracker internal error: {:}._validate_attr_type() does not support type={:}".format(
                _u.get_type_name(self), prop_type))


    #-----------------------------------------------------------------
    def _set_property(self, prop_name, value, prop_type, allow_single_value=True, allow_none=True):

        multiple_values = False

        if value is None and not allow_none:
                raise ttrk.TypeError("{:}.{:} cannot be set to None".format(_u.get_type_name(self), prop_name))

        if value is not None:

            multiple_values = self._is_multiple_values(value, prop_type)
            if multiple_values:
                for v in value:
                    _u.validate_attr_type(self, prop_name, v, prop_type)
                value = list(value)
            elif allow_single_value:
                _u.validate_attr_type(self, prop_name, value, prop_type, none_allowed=True)
            else:
                raise ttrk.TypeError("{:}.{:} must be set to a list of values; a single {:} is invalid".format(
                    _u.get_type_name(self), prop_name, prop_type.__name__ if isinstance(prop_type, type) else prop_type))

        setattr(self, "_" + prop_name, value)
        setattr(self, "_" + prop_name + "_multiple", multiple_values)


#=====================================================================
# The operation that is registered to the event manager for hiding/showing
#=====================================================================


# --------------------------------------------------------------
# noinspection PyProtectedMember
class StimulusEnableDisableOp(object):


    #--------------------------------------------------
    def __init__(self, multistim, stimulus_num, visible):
        self._multistim = multistim
        self._stimulus_num = stimulus_num
        self._visible = visible


    #--------------------------------------------------
    def __call__(self, *args, **kwargs):
        self._multistim._log_write_if(ttrk.log_info, str(self))
        self._multistim._set_visible(self._stimulus_num, self._visible)


    #--------------------------------------------------
    def __str__(self):
        return "{:} {:} #{:} ({:})".format("Show" if self._visible else "Hide",
                                           self._multistim._value_type_desc(),
                                           self._stimulus_num,
                                           self._multistim.get_stimulus_desc(self._stimulus_num))
