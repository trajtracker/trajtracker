

Design of the discrete-choice experiment software
=================================================

The organization of python files
++++++++++++++++++++++++++++++++

The discrete-choice experiment program is organized in two main files and has 3 main data structures.

**Files:**

- _dc_init.py: contains the initiailzation functions (which run before the experiment starts).
- _dc_run.py: contains runtime functions (actually run the experiment)

**Data structures**:

- :doc:`Config <Config>` : an object containing the configuration of supported features.
- :class:`~trajtrackerp.dchoice.ExperimentInfo` : an object that keeps all the experiment-level information:
  visual objects (e.g. stimuli, response feedback), movement validators, the info from the CSV data file,
  experiment-level results (e.g., number of failed trial), etc.
- :class:`~trajtrackerp.dchoice.TrialInfo` : an object that keeps the information about the present trial.


The persistent objects
++++++++++++++++++++++

The following objects exist throughout the experiment session (all are stored as part of the
:class:`~trajtrackerp.dchoice.ExperimentInfo` object):

- The response buttons

- The stimuli used as visual feedback once a response is selected

- A list of :class:`~trajtrackerp.dchoice.TrialInfo` objects, typically created by loading from the CSV file.

- The :doc:`Config <Config>` object and some other configuration parameters (e.g., result file names,
  subject ID and name, etc.).

.. include:: ../exp_design_persistent_objects.txt


.. include:: ../exp_design_events.txt


List of functions
+++++++++++++++++

The main program calls *create_experiment_objects()*; this function takes care of the complete
initialization process: it calls all the other functions in this file.

Below is the list of functions specific to the number-to-position task.
See :doc:`here <../functions_common>` a list of common functions.


Functions in _dc_init.py
------------------------

.. autofunction:: trajtrackerp.dchoice.create_experiment_objects
.. autofunction:: trajtrackerp.dchoice.create_feedback_stimuli
.. autofunction:: trajtrackerp.dchoice.create_response_buttons
.. autofunction:: trajtrackerp.dchoice.create_sounds
.. autofunction:: trajtrackerp.dchoice.hide_feedback_stimuli
.. autofunction:: trajtrackerp.dchoice.initialize_experiment
.. autofunction:: trajtrackerp.dchoice.load_data_source

Functions in _dc_run.py
-----------------------

.. autofunction:: trajtrackerp.dchoice.initialize_trial
.. autofunction:: trajtrackerp.dchoice.get_touched_button
.. autofunction:: trajtrackerp.dchoice.run_trials
.. autofunction:: trajtrackerp.dchoice.run_trial
.. autofunction:: trajtrackerp.dchoice.trial_ended
.. autofunction:: trajtrackerp.dchoice.trial_failed
.. autofunction:: trajtrackerp.dchoice.trial_succeeded
.. autofunction:: trajtrackerp.dchoice.update_trials_file
