
Design of the number-to-position experiment software
====================================================


The organization of python files
++++++++++++++++++++++++++++++++

The number-to-position experiment program is organized in two main files and has 3 main data structures.

**Files:**

- _n2p_init.py: contains the initiailzation functions (which run before the experiment starts).
- _n2p_run.py: contains runtime functions (actually run the experiment)

**Data structures**:

- :doc:`Config <Config>` : an object containing the configuration of supported features.
- :class:`~trajtracker.paradigms.num2pos.ExperimentInfo` : an object that keeps all the experiment-level information:
  visual objects (number-line, stimulus), movement validators, the info from the CSV data file,
  experiment-level results (e.g., number of failed trial), etc.
- :class:`~trajtracker.paradigms.num2pos.TrialInfo` : an object that keeps the information about the present trial.



The persistent objects
++++++++++++++++++++++

The following objects exist throughout the experiment session (all are stored as part of the
:class:`~trajtracker.paradigms.num2pos.ExperimentInfo` object):

- A :class:`~trajtracker.stimuli.NumberLine`

- Objects that can visually denote specific locations on the number line: a feedback arrow, and a vertical
  line indicating the correct target location.

- A list of :class:`~trajtracker.paradigms.num2pos.TrialInfo` objects, typically created by loading from the CSV file.

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

Functions in _n2p_init.py
-------------------------

.. autofunction:: trajtracker.paradigms.num2pos.create_experiment_objects
.. autofunction:: trajtracker.paradigms.num2pos.create_numberline
.. autofunction:: trajtracker.paradigms.num2pos.create_sounds
.. autofunction:: trajtracker.paradigms.num2pos.load_data_source


Functions in _n2p_run.py
------------------------

.. autofunction:: trajtracker.paradigms.num2pos.run_full_experiment
.. autofunction:: trajtracker.paradigms.num2pos.initialize_trial
.. autofunction:: trajtracker.paradigms.num2pos.on_finger_touched_screen
.. autofunction:: trajtracker.paradigms.num2pos.play_success_sound
.. autofunction:: trajtracker.paradigms.num2pos.run_trials
.. autofunction:: trajtracker.paradigms.num2pos.run_trial
.. autofunction:: trajtracker.paradigms.num2pos.trial_ended
.. autofunction:: trajtracker.paradigms.num2pos.trial_failed
.. autofunction:: trajtracker.paradigms.num2pos.trial_succeeded

