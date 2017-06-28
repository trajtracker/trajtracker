.. TrajTracker : ExperimentInfo.py


ExperimentInfo class (number-to-position)
=========================================

This object keeps all the experiment data:

- The configuration (:doc:`Config <Config>`) ;
- TrajTracker objects such as number line, the "start" point, the movement validators, etc. ;
- The data from the CSV file ;
- Expyriment's active_experiment object ; and
- The experiment results.


.. autoclass:: trajtrackerp.num2pos.ExperimentInfo
    :members:
    :member-order: alphabetical


The ExperimentInfo class is an extension of BaseExperimentInfo so it contains all its properties
too, as detailed below:

.. autoclass:: trajtrackerp.common.BaseExperimentInfo
    :members:
    :exclude-members: __init__
    :member-order: alphabetical

