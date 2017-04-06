.. TrajTracker : NumberLine.py

NumberLine class
================

A class that plots a number line and detects when the participant touches it in certain points.

**How to use this class:**

- Configure the object via constructor/properties
- :func:`trajtracker.stimuli.NumberLine.plot` or :func:`trajtracker.stimuli.NumberLine.present` it
- Call :func:`trajtracker.stimuli.NumberLine.reset` when mouse/finger starts moving
- Call :func:`trajtracker.stimuli.NumberLine.update_xy` when the mouse/finger continues moving


**Visual features:**

- Plot a number line, horizontal or vertical
- Optional tick marks at the end of the line and in locations along the line
- Optional text labels at the end of the line
- Allow modifying all common properties of the line and the text labels


**Behavioral features:**

- Detect when the finger/mouse clicks or crosses the number line
- Support both the physical coordinate space and the logical position on the line



Class-level definitions:
------------------------

**NumberLine.Orientation**: An enum that defines the number line orientation.
Possible values: *NumberLine.Orientation.Horizontal* or *NumberLine.Orientation.Vertical*


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.NumberLine
   :members:
   :member-order: bysource


