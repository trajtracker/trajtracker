.. TrajTracker : EventManager.py

EventManager class
==================

An object that takes care of events in the experiment. See (TBD) for overview of the events mechanism.

When working with event manager, you should:

- :func:`~trajtracker.events.EventManager.register` event-sensitive objects
- Call :func:`~trajtracker.events.EventManager.dispatch_event` whenever an event occurs.
  See :class:`~trajtracker.events.Event` about defining events.
- Call :func:`~trajtracker.events.EventManager.on_frame` frequently - preferably, once per frame

Some operations are triggered to run with temporal delay after the event. The event manager takes care of this
timing. However, note that the event manager never takes the system time: it fully relies on the time you
provide it (both :func:`~trajtracker.events.EventManager.dispatch_event` and
:func:`~trajtracker.events.EventManager.on_frame` receive a time_in_session argument).
For best precision, time_in_session should be synchronized with the display - i.e., set its value
right aftet calling stimulus.present()


Methods and properties:
-----------------------

.. autoclass:: trajtracker.events.EventManager
   :members:
   :inherited-members:
   :member-order: alphabetical

