.. TrajTracker : MultiPicture.py

MultiPicture class
==================

This class can present one or more pictures during a trial, e.g., to shown an RSVP. You can easily configure the onset
and offset time of each of the pictures to present.

Each picture to present is implemented as a separate Expyriment Picture object. Thus, switching
between pictures is not time-consuming, and can be safely done in mid-trial. The
only time-consuming operation is when you initialize the stimuli
(which should be done at the beginning of the trial)


Using this class:
-----------------


Configuring the pictures
^^^^^^^^^^^^^^^^^^^^^^^^

When working with the MultiPicture class, you define pictures twice:

- :attr:`~trajtracker.stimuli.MultiPicture.available_pictures` is the set of all pictures
  that can be presented. Typically, you'll define this before the experiment starts, and preload all pictures.
  Each picture is assigned a string ID.

- :attr:`~trajtracker.stimuli.MultiPicture.shown_pictures` is the list of pictures shown in a specific trial.
  Here, you don't reload the pictures - you just specify their string IDs.


Controlling the onset and offset times of each picture can be done via the :doc:`events mechanism <../events/events_overview>`
or by directly calling some methods of this class. This works just like the :class:`~trajtracker.stimuli.MultiTextBox`
class - please see there for details.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.MultiPicture
   :members:
   :inherited-members:
   :member-order: bysource


