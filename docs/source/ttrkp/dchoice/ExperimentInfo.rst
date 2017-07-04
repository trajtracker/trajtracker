.. TrajTracker : ExperimentInfo.py


ExperimentInfo class (discrete choice)
======================================

This object keeps all the experiment data:

- The configuration (:class:`~trajtrackerp.dchoice.Config`) ;
- TrajTracker objects such as the target, the "start" point, the movement validators, etc. ;
- The data from the CSV file ;
- Expyriment's active_experiment object ; and
- The experiment results.


.. autoclass:: trajtrackerp.dchoice.ExperimentInfo
    :members:
    :member-order: alphabetical


The ExperimentInfo class is an extension of BaseExperimentInfo so it contains all its properties
too, as detailed below:

.. autoclass:: trajtrackerp.common.BaseExperimentInfo
    :members:
    :exclude-members: __init__
    :member-order: alphabetical
    :noindex:

