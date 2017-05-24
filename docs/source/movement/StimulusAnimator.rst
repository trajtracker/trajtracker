.. TrajTracker : StimulusAnimator.py

StimulusAnimator class
======================

Move a stimulus in a predefined visual trajectory.

The trajectory is defined by a separate class, a "trajectory generator", which defines where the stimulus
should appear in each time point. The trajectory generator should have a get_traj_point() method, which
gets a time point (a number, specifying seconds) and returns a dict with the trajectory info
at that time point ('x', 'y', and 'visible' entries, all optional).

See :class:`~trajtracker.movement.CircularTrajectoryGenerator` for an example trajectory generator.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.movement.StimulusAnimator
   :members:
   :inherited-members:
   :member-order: alphabetical

