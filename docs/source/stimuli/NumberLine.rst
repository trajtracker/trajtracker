.. TrajTracker : NumberLine.py

NumberLine class
================

A class that plots a number line and detects when the participant touches it in certain points.

**Visual features:**

- Plot a number line, horizontal or vertical
- Optional tick marks at the end of the line and in locations along the line
- Optional text labels at the end of the line
- Allow modifying all common properties of the line and the text labels

**Behavioral features:**

- Detect when the finger/mouse clicks or crosses the number line
- Support both the physical coordinate space and the logical position on the line

Using this class
----------------

- Configure the number line (via the constructor or by setting properties)
- Optionally set :attr:`~trajtracker.stimuli.NumberLine.feedback_stim` to a stimulus that shows
  the finger langing position. If you use an event manager, you can set
  :attr:`~trajtracker.stimuli.NumberLine.feedback_stim_hide_event` to automatically hide the feedback stimulus
  (e.g. after some time, or when the next trial starts)
- Draw the number line on screen with :func:`~trajtracker.stimuli.NumberLine.plot` or
  :func:`~trajtracker.stimuli.NumberLine.present`
- Call :func:`~trajtracker.stimuli.NumberLine.reset` when mouse/finger starts moving
- Call :func:`~trajtracker.stimuli.NumberLine.update_xyt` when the mouse/finger continues moving
- Check :attr:`~trajtracker.stimuli.NumberLine.touched` to see if the number-line was touched

Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.NumberLine
   :members:
   :inherited-members:
   :member-order: bysource


