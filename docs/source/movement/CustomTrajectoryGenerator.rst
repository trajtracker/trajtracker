.. TrajTracker : CustomTrajectoryGenerator.py

CustomTrajectoryGenerator class
===============================

Create a movement trajectory for a stimulus, according to explicit definition.

The definition can be loaded from a CSV file or specified programmatically.

This class can hold several different trajectories. Each has its own ID. Before the trial
starts, set the ID of the trajectory to play.

Use this class in conjunction with :class:`~trajtracker.movement.StimulusAnimator`

After loading trajectories, call :func:`~trajtracker.movement.CustomTrajectoryGenerator.validate`


Methods and properties:
-----------------------

.. autoclass:: trajtracker.movement.CustomTrajectoryGenerator
   :members:
   :inherited-members:
   :member-order: bysource

