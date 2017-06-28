.. TrajTracker : RectStartPoint.py

RectStartPoint class
====================

This is a specific implementation of :class:`~trajtracker.movement.StartPoint` that shows a rectangular
"start" area, and expects the movement to start in an upward direction.

The differences between the basic :class:`~trajtracker.movement.StartPoint` and this class are:

- The present class also creates the visual rectangle to display on screen.
  The rectangle is created with default visual properties and you can modify it later
  (access it via :attr:`~trajtracker.movement.RectStartPoint.start_area` )
- Consequently, unlike :class:`~trajtracker.movement.StartPoint` the present class does not allow
  defining the start & exit area flexibly.
- The present class lets you also tilt the rectangle (:attr:`~trajtracker.movement.RectStartPoint.rotation`)


Methods and properties:
-----------------------

.. autoclass:: trajtracker.movement.RectStartPoint
   :members:
   :inherited-members:
   :member-order: alphabetical

