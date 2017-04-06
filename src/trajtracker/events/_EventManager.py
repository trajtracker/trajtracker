"""

Manages the events during an experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


import numbers
import numpy as np
from operator import itemgetter

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u


# noinspection PyProtectedMember
class EventManager(trajtracker._TTrkObject):


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

        if "on_registered" not in dir(es_obj):
            raise TypeError("trajtracker error: EventManager.register() was called with an incorrect object " +
                            "({:}) - the registered object must have a on_registered() method".format(es_obj))

        es_obj.on_registered(self)


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

        _u.validate_func_arg_type(self, "dispatch_event", "event", event, trajtracker.events.Event)
        _u.validate_func_arg_type(self, "dispatch_event", "time_in_trial", time_in_trial, numbers.Number)
        _u.validate_func_arg_type(self, "dispatch_event", "time_in_session", time_in_session, numbers.Number)

        if event.offset > 0 and self._should_log(self.log_warn):
            self._log_write("dispatch_event warning: you dispatched event {:}, which has offset > 0; the offset parameter is ignored".format(event), True)

        if event._extended and self._should_log(self.log_warn):
            self._log_write("dispatch_event warning: you dispatched event {:}, which has some sub-events".format(event))

        self._dispatch_event(event, time_in_trial, time_in_session)


    #--------------------------------------------------------------
    def _dispatch_event(self, event, time_in_trial, time_in_session):

        #-- Dispatch base events
        if event.extends is not None:
            self.dispatch_event(event.extends, time_in_trial, time_in_session)

        if event.event_id not in self._operations_by_event:
            return

        added_pending_op = False

        for op_info in self._operations_by_event[event.event_id].values():

            if not op_info['active']:
                #-- It was already invoked
                continue

            if not op_info['recurring']:
                op_info['active'] = False

            if op_info['event'].offset == 0:
                #-- Invoke operation immediately
                self._invoke_operation(op_info['id'], time_in_trial, time_in_session)

            else:
                #-- Remember for later
                self._pending_operations.append((op_info['id'], time_in_session + op_info['event'].offset))
                added_pending_op = True

        if added_pending_op:
            self._pending_operations.sort(key=itemgetter(1))


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

        _u.validate_func_arg_type(self, "on_frame", "time_in_trial", time_in_trial, numbers.Number)
        _u.validate_func_arg_type(self, "on_frame", "time_in_session", time_in_session, numbers.Number)

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
        :param operation: A function with a single argument, which is the time in the trial.
                          The function will be called at the time of the requested event.
                          (you can provide any python object that behaves like a function, i.e., supports
                          the () operator).
        :param recurring: If True, the operation will be re-invoked every time the event occurs again.
                          If False, the operation will be invoked once and then forgotten.
        :param cancel_pending_operation_on: This is relevant for operations that were registered to run
                          some time after an event X occurred. If, between the time of event X and the operation's
                          due time, a second event Y occurs (and cancel_pending_operation_on=Y), the operation will
                          be discarded and not invoked.
        :returns: a unique identifier of this operation. You can use it later to unregister the operation via
                        :func:`~trajtracker.events.EventManager.unregister_operation()`.
        """

        _u.validate_func_arg_type(self, "register_operation", "event", event, trajtracker.events.Event)
        _u.validate_func_arg_type(self, "register_operation", "recurring", recurring, bool)
        _u.validate_func_arg_type(self, "register_operation", "cancel_pending_operation_on", cancel_pending_operation_on,
                                  (trajtracker.events.Event, list, tuple, set, np.ndarray))
        if "__call__" not in dir(operation):
            raise TypeError("trajtracker error: EventManager.register_operation() was called with an invalid operation " +
                            "({:}) - expecting a function or another callable object".format(operation))

        self._id_generator += 1
        operation_id = self._id_generator

        op_info = dict(operation=operation,
                       event=event,
                       cancel_pending_operation_on=cancel_pending_operation_on,
                       recurring=recurring,
                       description=description,
                       id=operation_id,
                       active=True)


        #-- Register the operation

        self._operations_by_id[operation_id] = op_info

        if event.event_id not in self._operations_by_event:
            self._operations_by_event[event.event_id] = dict()
            self._operations_by_event[event.event_id][operation_id] = op_info

        #-- Log
        if self._should_log(self.log_debug):
            self._log_write('register {:} operation "{:}" on event {:}{:}; operation ID={:}'.format(
                "recurring" if recurring else "non-recurring",
                operation if description is None else description,
                event,
                "" if len(cancel_pending_operation_on) == 0 else ("; cancel pending on " + ",".join(cancel_pending_operation_on)),
                operation_id), True)

        return operation_id


    #--------------------------------------------------------------
    def unregister_operation(self, operation_id):
        """
        Unregister a previously-registered operation.

        This method is intended for internal use of the trajtracker package. Generally, you should not use
        this method but :func:`~trajtracker.events.EventManager.register`.

        :param operation_id: The ID returned from :func:`~trajtracker.events.EventManager.register_operation`.
        :return: The operation and the event on which it was registered (as tuple); or None if operation was not found.
        """

        _u.validate_func_arg_type(self, "unregister_operation", "operation_id", operation_id, int)

        if operation_id not in self._operations_by_id:
            return None

        if self._should_log(self.log_debug):
            self._log_write('unregistering {:} operation "{:}" (ID={:}) from event {:}'.format(
                "recurring" if recurring else "non-recurring",
                operation if description is None else description,
                operation_id,
                event), True)

        op_info = self._operations_by_id[operation_id]
        self._remove_operation(operation_id, True)

        return op_info['operation'], op_info['event']


    #======================================================================================
    # Internal stuff
    #======================================================================================

    #--------------------------------------------------------------
    def _remove_operation(self, operation_id, remove_pending):

        op_info = self._operations_by_id[operation_id]
        op_event_id = op_info['event'].event_id

        #-- Remove the operation
        del self._operations_by_id[operation_id]
        del self._operations_by_event[op_event_id][operation_id]

        #-- Remove from the pending list
        if remove_pending:
            self._pending_operations = [op for op in self._pending_operations if op[0] != operation_id]


    #--------------------------------------------------------------
    def _invoke_operation(self, operation_id, time_in_trial, time_in_session, remove_pending=True):

        op_info = self._operations_by_id[operation_id]
        op_desc = str(op_info['operation']) if op_info['description'] is None else op_info['description']

        # -- Invoke it
        if self._should_log(self.log_trace):
            self._log_write("Invoking operation (id={:}, operation={:}, event={:})".format(
                operation_id, op_desc, op_info['event']), True)
        op = op_info['operation']
        op(time_in_trial, time_in_session)  # todo really?

        #-- After a one-time operation was invoked, remove it
        if not op_info['recurring']:
            self._remove_operation(operation_id, remove_pending)
