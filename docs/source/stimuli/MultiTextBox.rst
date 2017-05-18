.. TrajTracker : MultiTextBox.py

MultiTextBox class
==================

A text box that can present one or more values during a trial, e.g., to shown an RSVP. You can easily configure the onset
and offset time of each of the values to present.

Each value to present is implemented as a separate Expyriment TextBox, which means that:

- You can set the graphical properties (font, size, position, etc.) to have a common value for
  all presented texts, or a separate value per text.

- Changing from one text to another is not time-consuming, and can be safely done in mid-trial. The
  only time-consuming operation is when you initialize the stimuli (which should be done at the beginning of the trial)


Using this class:
-----------------

This class is used in slightly different ways depending on whether or not you use an
:class:`~trajtracker.events.EventManager` in your application.


Using MultiTextBox with an EventManager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Add :attr:`~trajtracker.stimuli.MultiTextBox.stimulus` into your :class:`~trajtracker.stimuli.StimulusContainer`

- Call :func:`EventManager.register <trajtracker.events.EventManager.register>` to register the MultiTextBox
  on the event manager.

  Note: if you modify :attr:`~trajtracker.stimuli.MultiTextBox.trial_configured_event`, this must be done before
  before calling :func:`EventManager.register <trajtracker.events.EventManager.register>`.

- On the beginning of each trial, update the visual properties of the textbox (text, font, size, position, etc.).

  Note that these initializations must be completed before the
  :attr:`~trajtracker.stimuli.MultiTextBox.trial_configured_event` event is dispatched.
  Changing properties after :attr:`~trajtracker.stimuli.MultiTextBox.trial_configured_event` was dispatched
  will have no effect.


Using MultiTextBox without an EventManager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- On the beginning of each trial, update the visual properties of the textbox (text, font, size, position, etc.).
  You do not need to configure the events.

- After these properties were set, call :func:`~trajtracker.stimuli.MultiTextBox.init_for_trial`.

- To start showing the stimuli, call :func:`~trajtracker.stimuli.MultiTextBox.start_showing`.

- Call :func:`~trajtracker.stimuli.MultiTextBox.update_display` periodically - preferably once per frame.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.MultiTextBox
   :members:
   :inherited-members:
   :member-order: bysource


