.. TrajTracker : MultiStimulis.py

MultiStimulus class
===================

This class can present one or more stimuli during a trial. The class can handle Expyriment stimuli of
any type - pictures, shapes, etc.
You can easily configure the onset and offset time of each of the stimuli to present, so you
can use this to present stimuli in RSVP.

The MultiStimulus object holds a set of preloaded stimuli that it can show, each with a string ID.
On each trial, you define which of these stimuli to show. Thus, switching between stimuli is
not time-consuming, and can be safely done in mid-trial. The only time-consuming operation is
the initialization of stimuli, which would typically be done before the experiment starts.


Using this class:
-----------------


Configuring the stimuli
^^^^^^^^^^^^^^^^^^^^^^^

When working with the MultiStimulis class, you define stimuli twice:

- :attr:`~trajtracker.stimuli.MultiStimulis.available_stimuli` is the set of all stimuli
  that can be presented. Typically, you'll define this before the experiment starts, and preload all stimuli.
  Each picture is assigned a string ID.

- :attr:`~trajtracker.stimuli.MultiStimulis.shown_stimuli` is the list of stimuli shown in a specific trial.
  Here, you don't reload the stimuli - you just specify their string IDs.


Controlling the onset and offset times of each picture can be done via the :doc:`events mechanism <../events/events_overview>`
or by directly calling some methods of this class. This works just like the :class:`~trajtracker.stimuli.MultiTextBox`
class - please see there for details.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.MultiStimulis
   :members:
   :inherited-members:
   :member-order: bysource


