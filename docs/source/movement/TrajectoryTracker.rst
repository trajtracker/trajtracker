.. TrajTracker : TrajectoryTracker.py

TrajectoryTracker class
=======================

Track mouse/finger trajectory and save results to a CSV file.

**To use this class:**

- Call :func:`~trajtracker.movement.TrajectoryTracker.init_output_file` when the experiment starts
- Call :func:`~trajtracker.movement.TrajectoryTracker.reset` when the trial starts
- Set :attr:`~trajtracker.movement.TrajectoryTracker.tracking_active` to True and False in order to
  enable/disable tracking during a trial
- Call :func:`~trajtracker.movement.TrajectoryTracker.update_xyt` whenever the finger/mouse moves
- Call :func:`~trajtracker.movement.TrajectoryTracker.save_to_file` when the trial ends


Methods and properties:
-----------------------

.. autoclass:: trajtracker.movement.TrajectoryTracker
   :members:
   :member-order: bysource

