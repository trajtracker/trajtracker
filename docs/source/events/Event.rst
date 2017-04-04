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




Methods and properties:
-----------------------

.. autoclass:: trajtracker.events.Event
   :members:
   :member-order: bysource


