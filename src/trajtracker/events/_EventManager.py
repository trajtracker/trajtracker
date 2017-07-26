"""

Manages the events during an experiment

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


import numbers
import numpy as np
from operator import itemgetter

import trajtracker
import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.events import Event


# noinspection PyProtectedMember
class EventManager(ttrk.TTrkObject):


    #======================================================================================
    # Public interface
    #======================================================================================

    def __init__(self):
        super(EventManager, self).__init__()

        self._operations_by_id = dict()
        self._operations_by_event = dict()

        self._pending_operations = []

        self._id_generator = 0


    #--------------------------------------------------------------
    def register(self, es_obj):
        """
        Register an event-sensitive object: an object that needs to run things based on the occurrence of events.

        **Under the hood**: Technically, the only thing this method does is to call es_obj.on_registered(),
        and that method should take care of all the rest.

        :param es_obj: Must have an "on_registered" method, which will be called at the time
                       of registration with the event manager as a single argument.
        """

        if es_obj is None:
            return

        self._log_func_enters("register", [es_obj])

        if "on_registered" not in dir(es_obj):
            raise ttrk.TypeError("EventManager.register() was called with an incorrect object " +
                                 "({:}) - the registered object must have a on_registered() method".format(es_obj))

        es_obj.on_registered(self)

        self._log_func_returns("register")


    #--------------------------------------------------------------
    def dispatch_event(self, event, time_in_trial, time_in_session):
        """
        Inform the event manager that an event has occurred. This method will:

        - If an operation was registered to run on this event (with offset=0), invoke it
        - If an operation was registered to run some time after the event (offset > 0), remember it
          for later. It will be invoked by :func:`~trajtracker.events.EventManager.on_frame`

        :param event: an :class:`~trajtracker.events.Event` object
        :param time_in_trial: The time (in seconds) from the beginning of the present trial
        :param time_in_session: The time (in seconds) from the beginning of the session.
                       This parameter is very important, as the timing of operations is based on it.
                       It must be syncronized with the time_in_session parameter sent to
                       :func:`~trajtracker.events.EventManager.on_frame`
        """

        _u.validate_func_arg_type(self, "dispatch_event", "event", event, ttrk.events.Event)
        _u.validate_func_arg_type(self, "dispatch_event", "time_in_trial", time_in_trial, numbers.Number)
        _u.validate_func_arg_type(self, "dispatch_event", "time_in_session", time_in_session, numbers.Number)

        if event.offset > 0:
            self._log_write_if(ttrk.log_warn, "dispatch_event warning: you dispatched event {:}, which has offset > 0; the offset parameter is ignored".format(event), True)

        if event._extended:
            self._log_write_if(ttrk.log_warn, "dispatch_event warning: you dispatched event {:}, which has some sub-events".format(event))

        self._dispatch_event(event, time_in_trial, time_in_session)


    #--------------------------------------------------------------
    def _dispatch_event(self, event, time_in_trial, time_in_session):

        self._log_func_enters("_dispatch_event", [event, time_in_trial, time_in_session])

        #-- Dispatch base events
        if event.extends is not None:
            self._dispatch_event(event.extends, time_in_trial, time_in_session)

        self._log_write_if(ttrk.log_info, "Dispatching event {:}, time_in_trial={:}, time_in_session={:}".format(event.event_id, time_in_trial, time_in_session))

        if event.event_id not in self._operations_by_event:
            self._log_write_if(ttrk.log_trace, "No operations to invoke for event {:}".format(event.event_id))
            return

        added_pending_op = False

        op_infos = list(self._operations_by_event[event.event_id].values())
        for op_info in op_infos:

            if not op_info.active:
                #-- It was already invoked
                continue

            if not op_info.recurring:
                op_info.active = False

            if op_info.event.offset == 0:
                #-- Invoke operation immediately
                self._invoke_operation(op_info.operation_id, time_in_trial, time_in_session)

            else:
                #-- Remember for later
                op_time = time_in_session + op_info.event.offset
                if self._should_log(ttrk.log_trace):
                    self._log_write("Operation {:} ({:}) is now pending to run later, at {:.3f} ({:})".
                                    format(op_info.operation_id, op_info.description, op_time, op_info.event))
                self._pending_operations.append((op_info.operation_id, op_time))
                added_pending_op = True

        if added_pending_op:
            self._pending_operations.sort(key=itemgetter(1))

        self._log_func_returns("_dispatch_event")


    #--------------------------------------------------------------
    def on_frame(self, time_in_trial, time_in_session):
        """
        This method must be called repeatedly - preferably on each frame. It takes care of invoking
        delayed operations - i.e., operations that should run somewhen after an already-dispatched event.

        :param time_in_trial: The time (in seconds) from the beginning of the current trial
        :param time_in_session: The time (in seconds) from the beginning of the session.
                       This parameter is very important, as the timing of operations is based on it.
                       It must be syncronized with the time_in_session parameter sent to
                       :func:`~trajtracker.events.EventManager.dispatch_event`
        :return: The number of operations invoked.
        """

        _u.validate_func_arg_type(self, "on_frame", "time_in_trial", time_in_trial, numbers.Number, none_allowed=True)
        _u.validate_func_arg_type(self, "on_frame", "time_in_session", time_in_session, numbers.Number)

        if self._should_log(ttrk.log_trace):
            self._log_write("{:}.on_frame(time_in_trial={:.3f}, time_in_session={:.3f}) called".
                            format(_u.get_type_name(self), time_in_trial, time_in_session))

        n = 0
        while len(self._pending_operations) > 0 and self._pending_operations[0][1] <= time_in_session:
            op = self._pending_operations.pop(0)
            self._invoke_operation(op[0], time_in_trial, time_in_session, remove_pending=False)
            n += 1

        return n


    #--------------------------------------------------------------
    def cancel_pending_operations(self):
        """
        Cancel all pending operation - i.e., operations that were registered to run in a delay from an
        event that has already occurred.

        In standard mode, there will be no need to call this function. You can call it, however, in case
        you want to reset everything and make sure you don't have any leftovers.
        """
        self._log_func_enters("cancel_pending_operations")
        self._pending_operations = []


    #======================================================================================
    #
    #  Methods to be used by event-sensitive objects
    #
    #  In typical experiments, these are only classes from the trajtracker package
    #
    #======================================================================================

    #--------------------------------------------------------------
    def register_operation(self, event, operation, recurring=False, cancel_pending_operation_on=(), description=None):
        """
        Register a specific operation to run at some time.

        This method is intended for internal use of the trajtracker package. Generally, you should not use
        this method but :func:`~trajtracker.events.EventManager.register`.

        :param event: Determines when the operation should be invoked
        :param operation: A function that gets two arguments - time_in_trial and time_in_session.
                          The function will be called at the time of the requested event.
                          (you can provide any python object that behaves like a function, i.e., supports
                          the () operator).
        :param recurring: If True, the operation will be re-invoked every time the event occurs again.
                          If False, the operation will be invoked once and then forgotten.
        :param cancel_pending_operation_on: This is relevant for operations that were registered to run
                          some time after an event X occurred. If, between the time of event X and the operation's
                          due time, a second event Y occurs (and cancel_pending_operation_on=Y), the operation will
                          be discarded and not invoked.
        :type cancel_pending_operation_on: either :class:`~trajtracker.events.Event` or a list of events
        :returns: a unique identifier of this operation. You can use it later to unregister the operation via
                        :func:`~trajtracker.events.EventManager.unregister_operation()`.
        """

        _u.validate_func_arg_type(self, "register_operation", "event", event, ttrk.events.Event)
        _u.validate_func_arg_type(self, "register_operation", "recurring", recurring, bool)
        _u.validate_func_arg_type(self, "register_operation", "cancel_pending_operation_on", cancel_pending_operation_on,
                                  (ttrk.events.Event, list, tuple, set, np.ndarray))
        _u.validate_func_arg_type(self, "register_operation", "operation", operation, trajtracker.TYPE_CALLABLE)

        self._log_func_enters("register_operation", [event, operation, recurring, cancel_pending_operation_on, description])

        if isinstance(cancel_pending_operation_on, Event):
            cancel_pending_operation_on = cancel_pending_operation_on,

        self._id_generator += 1
        operation_id = self._id_generator

        op_info = _RegisteredOperation(callback_function=operation,
                                       event=event,
                                       cancel_pending_operation_on=cancel_pending_operation_on,
                                       recurring=recurring,
                                       description=description,
                                       operation_id=operation_id)

        #-- Register the operation

        self._operations_by_id[operation_id] = op_info

        if event.event_id not in self._operations_by_event:
            self._operations_by_event[event.event_id] = dict()

        self._operations_by_event[event.event_id][operation_id] = op_info

        #-- Log
        if self._should_log(ttrk.log_debug):
            cancel_events_desc = ""
            if len(cancel_pending_operation_on) > 0:
                cancel_events = [e.event_id for e in cancel_pending_operation_on]
                cancel_events_desc = "; cancel pending on " + ",".join(cancel_events)

            self._log_write('register {:} operation "{:}" on event {:}{:}; operation ID={:}'.format(
                "recurring" if recurring else "non-recurring",
                operation if description is None else description,
                event,
                cancel_events_desc,
                operation_id), True)

        self._log_func_returns("register_operation", operation_id)
        return operation_id


    #--------------------------------------------------------------
    def unregister_operation(self, operation_ids, warn_if_op_missing=True):
        """
        Unregister a previously-registered operation.

        This method is intended for internal use of the trajtracker package. Generally, you should not use
        this method but :func:`~trajtracker.events.EventManager.register`.

        :param operation_ids: The ID returned from :func:`~trajtracker.events.EventManager.register_operation`.
        :param warn_if_op_missing: Print a warning to log if an operation ID is not registered in the event manager
        """

        _u.validate_func_arg_type(self, "unregister_operation", "warn_if_op_missing", warn_if_op_missing, bool)

        if isinstance(operation_ids, int):
            operation_ids = operation_ids,
        else:
            _u.validate_func_arg_is_collection(self, "unregister_operation", "operation_id", operation_ids, allow_set=True)

        self._log_func_enters("unregister_operation", [operation_ids, warn_if_op_missing])

        for op_id in operation_ids:
            if op_id in self._operations_by_id:
                if self._should_log(ttrk.log_debug):
                    op_info = self._operations_by_id[op_id]
                    self._log_write('unregistering {:} operation "{:}" (ID={:}) from event {:}'.format(
                        "recurring" if op_info.recurring else "non-recurring",
                        op_info.description, op_id, op_info.event), True)
                self._remove_operation(op_id, True)
            elif warn_if_op_missing:
                self._log_write_if(ttrk.log_warn, "operation {:} is not in the event manager - not removed".format(op_id), True)

        self._log_func_returns("unregister_operation")

    #======================================================================================
    # Internal stuff
    #======================================================================================

    #--------------------------------------------------------------
    def _remove_operation(self, operation_id, remove_pending):

        op_info = self._operations_by_id[operation_id]
        op_event_id = op_info.event.event_id

        if self._should_log(ttrk.log_trace):
            self._log_write("Remove operation {:} (registered to {:}){:}".
                            format(op_info, op_info.event, ", including pending operations" if remove_pending else ""))

        #-- Remove the operation
        del self._operations_by_id[operation_id]
        del self._operations_by_event[op_event_id][operation_id]

        #-- Remove from the pending list
        if remove_pending:
            self._pending_operations = [op for op in self._pending_operations if op[0] != operation_id]


    #--------------------------------------------------------------
    def _invoke_operation(self, operation_id, time_in_trial, time_in_session, remove_pending=True):

        op_info = self._operations_by_id[operation_id]

        if self._should_log(ttrk.log_trace):
            self._log_write("Invoking operation (id={:}, operation={:}, event={:})".format(
                operation_id, op_info.description, op_info.event), True)

        #-- Invoke it
        op_info.function(time_in_trial, time_in_session)

        #-- After a one-time operation was invoked, remove it
        if not op_info.recurring:
            self._remove_operation(operation_id, remove_pending)


#=================================================================
class _RegisteredOperation(object):
    """
    An operation registered in the event manager
    """

    def __init__(self, callback_function, event, cancel_pending_operation_on,
                 recurring, description, operation_id):
        self.function = callback_function
        self.event = event
        self.cancel_pending_operation_on = cancel_pending_operation_on
        self.recurring = recurring
        self._description = description
        self.operation_id = operation_id
        self.active = True

    @property
    def description(self):
        return str(self.function) if self._description is None else self._description

    def __str__(self):
        return "{:} ({:})".format(self.operation_id, self.description)
