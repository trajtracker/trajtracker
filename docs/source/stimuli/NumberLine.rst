.. TrajTracker : NumberLine.py

NumberLine class
================

A class that plots a number line and detects when the participant touches it in certain points.

**Visual features:**

- The number line can be horizontal or vertical
- Optional tick marks at the end of the line and in locations along the line
- Optional text labels at the end of the line
- Standard properties of the line and the text labels (colour, font, etc.)

**Behavioral features:**

- Detect when the finger/mouse clicks or crosses the number line
- Get the touch location as coordiantes or on the number line's scale
- Show the response location on screen
- Convert between the physical coordinate space and the number line values
  (:func:`~trajtracker.stimuli.NumberLine.coord_to_value` ,
  :func:`~trajtracker.stimuli.NumberLine.value_to_coord`, and :func:`~trajtracker.stimuli.NumberLine.value_to_coords`)


Using this class
----------------

- Configure the number line (via the constructor or by setting properties)

- To show the response location (finger landing position): provide one or more
  :attr:`~trajtracker.stimuli.NumberLine.feedback_stimuli` and define a
  :attr:`~trajtracker.stimuli.NumberLine.feedback_stim_chooser` that decides, once the numberline was touched,
  which of them to show.

  The stimulus selector may rely on the :attr:`~trajtracker.stimuli.NumberLine.response_bias`,
  in which case you should set :attr:`~trajtracker.stimuli.NumberLine.target` in advance.

  When defining a feedback stimulus, the numberline will automatically show it when the
  line is touched (in fact, touching the line only sets an indication that the feedback should be presented;
  the feedback will be actually displayed on the next call to
  :func:`~trajtracker.stimuli.NumberLine.present` ).

  Hide the feedback stimulus by calling :func:`~trajtracker.stimuli.NumberLine.hide_feedback_stim` or,
  if you use the :doc:`events mechanism <../events/events_overview>` , by setting
  :attr:`~trajtracker.stimuli.NumberLine.feedback_stim_hide_event` .

- Draw the number line on screen with :func:`~trajtracker.stimuli.NumberLine.plot` or
  :func:`~trajtracker.stimuli.NumberLine.present`

- Call :func:`~trajtracker.stimuli.NumberLine.reset` when mouse/finger starts moving

- Call :func:`~trajtracker.stimuli.NumberLine.update_xyt` when the mouse/finger continues moving

- Check :attr:`~trajtracker.stimuli.NumberLine.touched` to see if the number-line was touched

  When the line was touched, get the touch location - either as coordinates
  (:attr:`~trajtracker.stimuli.NumberLine.last_touched_coord`) or
  by the numberline's numeric scale (:attr:`~trajtracker.stimuli.NumberLine.last_touched_value`).

  In case you updated :attr:`~trajtracker.stimuli.NumberLine.target` , you can also obtain
  :attr:`~trajtracker.stimuli.NumberLine.response_bias` .


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.NumberLine
   :members:
   :inherited-members:
   :member-order: alphabetical


