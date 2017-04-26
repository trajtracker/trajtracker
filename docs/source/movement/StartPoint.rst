.. TrajTracker : StartPoint.py

StartPoint class
================

A starting point for a trial.

The starting point defines two areas: a **start area**, which you must touch/click to initiate a trial. After
touching the start area, the subject must move the finger/mouse (without lifting it) from the start area
directly into an **exit area**. The movement into the exit area can be used as a trigger for starting the trial
voluntarily by the subject, or can be the mandatory behavior when a trial start is imposed by the software.

If the finger leaves the start area into a position other than the exit area, the trial may fail.

Technically, the :func:`~trajtracker.movement.StartPoint.check_xy` ,method tracks the mouse/finger movement,
and returns one of four states: The screen not touched yet; the start area was touched; the finger moved
from the start area into the exit area; or the finger moved to an invalid location.


Using this class:
-----------------

- Define a start area and an :attr:`~trajtracker.movement.StartPoint.exit_area`.
- When the trial is initialized, call :func:`~trajtracker.movement.StartPoint.reset`

Then, you can go in two ways. The convenient way consists of two steps:

- When the trial is initialized, call :func:`~trajtracker.movement.StartPoint.wait_until_startpoint_touched`
  to detect when the subject touches the starting point.

- Then, call :func:`~trajtracker.movement.StartPoint.wait_until_exit` to detect when the subject
  starts moving the mouse/finger.

Alternatively, if you want to create a slighly different flow, you can skip the two functions above
and repeatedly call :func:`~trajtracker.movement.StartPoint.check_xy` .
This may monitor the subject behavior in more detail.


Related classes:
----------------

:class:`~trajtracker.movement.RectStartPoint` is a more specific implementation of *StartPoint*:
it lets you easily define a rectangular "start" area and tilt it.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.movement.StartPoint
   :members:
   :inherited-members:
   :member-order: bysource

