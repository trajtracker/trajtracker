.. TrajTracker : Event.py

Event class
===========

This class defines an event that occurred during the experiment.
Several TrajTracker objects can define things that should happen when an event occurs, or some time later.
For example, stimuli can appear or disappear at certain times.

**Defining an event:**

.. code-block:: python

    number_line = trajtracker.stimuli.NumberLine()
    number_line.onset = Event("SessionStarts")
    number_line.offset = Event("SessionStarts")

Defining stimulus behavior via events requires that you use :class:`~trajtracker.events.EventManager`
in your program.

TrajTracker also has some :ref:`pre-defined-events`.


.. _event-hierarchy:

Advanced: Event Hierarchy
-------------------------

You can group several events into a hierarchy of "is a" relation. Event A is saied to *extend* event B if A
is a subtype of B. For example, trajtracker defines TRIAL_SUCCEEDED and TRIAL_ERROR events, both of which
extend the TRIAL_ENDED event, because these are two subtypes of the "end of trial" situation.

The advantage of creating such hierarchies is that when the program dispatches a TRIAL_SUCCEEDED or a
TRIAL_ERROR event, any operation registered to run on TRIAL_ENDED would be invoked too.

To define hierarchies in your custom events, use the "extends" argument when creating the Event object:

.. code-block:: python

   TRIAL_ENDED = Event("TRIAL_ENDED")
   TRIAL_SUCCEEDED = Event("TRIAL_SUCCEEDED", TRIAL_ENDED)
   TRIAL_ERROR = Event("TRIAL_ERROR", TRIAL_ENDED)



Methods and properties:
-----------------------

.. autoclass:: trajtracker.events.Event
   :members:
   :inherited-members:
   :member-order: alphabetical


