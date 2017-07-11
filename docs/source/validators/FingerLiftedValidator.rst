.. TrajTracker : FingerLiftedValidator.py

FingerLiftedValidator class
===========================

Validate that finger is not lifted in mid-trial.


Using this validator
--------------------

Note that unlike other validators, this one does not have a *update_xyt()* function (i.e., you do not notify it
continuously about the finger position). Instead, it has an
:func:`~trajtracker.validators.FingerLiftedValidator.update_touching` function, which you use to
continuously notify the validator whether the finger is touching the screen.

The validator can suffer short finger-off-screen durations without issuing an error (see
:attr:`~trajtracker.validators.FingerLiftedValidator.max_offscreen_duration`).
This is useful, for example, when using touchpads with inaccurate touch detection: such devices
may occasionally lose the touch information and report that the finger is not touching the screen.



Methods and properties:
-----------------------

.. autoclass:: trajtracker.validators.FingerLiftedValidator
   :members:
   :inherited-members:
   :member-order: alphabetical

