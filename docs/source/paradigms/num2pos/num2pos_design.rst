
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
- :doc:`ExperimentInfo <ExperimentInfo>` : an object that keeps all the experiment-level information:
  visual objects (number-line, stimulus), movement validators, the info from the CSV data file,
  experiment-level results (e.g., number of failed trial), etc.
- TrialInfo : an object that keeps the information about the present trial.




The persistent objects
++++++++++++++++++++++

The following objects exist throughout the experiment session (all are stored as part of the
:doc:`ExperimentInfo <ExperimentInfo>` object):

- A :class:`~trajtracker.stimuli.NumberLine`

- Placeholders for the stimuli: a :class:`~trajtracker.stimuli.MultiTextBox` for text stimuli, and
  a :class:`~trajtracker.stimuli.MultiStimulus` for other stimuli (pictures, shapes, etc.)

- A :class:`~trajtracker.movement.RectStartPoint` for initiating a trial

- A :class:`~trajtracker.stimuli.StimulusContainer` that keeps all the experiment's presentable objects

- A :class:`~trajtracker.movement.TrajectoryTracker` for saving the finger trajectories

- Movement validators: :class:`~trajtracker.validators.GlobalSpeedValidator` and
  :class:`~trajtracker.validators.InstantaneousSpeedValidator` to enforce speed,
  :class:`~trajtracker.validators.MovementAngleValidator` to prevent downward movement,
  and :class:`~trajtracker.validators.` to prevent zigzag movement.

- An :class:`~trajtracker.events.EventManager` - because the program works with
  :doc:`events <../../events/events_overview>`

- Objects that can visually denote specific locations on the number line: a feedback arrow, and a vertical
  line indicating the correct target location.

- Sounds (`expyriment.stimuli.Audio <http://docs.expyriment.org/expyriment.stimuli.Audio.html>`_ objects)
  to play when the trial ends (successfully or with an error).

- An `expyriment.stimuli.TextBox <http://docs.expyriment.org/expyriment.stimuli.TextBox.html>`_ for presenting
  error messages.

- A list of :doc:`TrialInfo <TrialInfo>` objects, typically created by loading from the CSV file.

- The :doc:`Config <Config>` object and some other configuration parameters (e.g., result file names,
  subject ID and name, etc.).

- A *dict* with experiment-level results (which is saved to the results file at the end of the exepriment).
  Trial-level results (which are saved in trials.csv) are stored on the :doc:`TrialInfo <TrialInfo>` object.


Events
++++++

A trial can include the following events:

- *trajtracker.events.TRIAL_INITIALIZED* - when the trial was initialized (right after the previous trial ended)
- *trajtracker.events.TRIAL_STARTED* - when the finger touches the "start" rectangle
- *FINGER_STARTED_MOVING* - when the finger starts moving
- *trajtracker.events.TRIAL_SUCCEEDED* - when the trial ended successfully (this has nothing to do with
  the location marked by the subject; it only indicates that the subject marked *some* location on the number line)
- *trajtracker.events.TRIAL_FAILED* - when the trial failed, for any reason
- *trajtracker.events.TRIAL_ENDED* - this event is dispatched whenever a TRIAL_SUCCEEDED or TRIAL_FAILED
  events are dispatched.

The operations triggered by events are:

- Showing/hiding stimuli: this happens in certain delay after TRIAL_STARTED (when config.stimulusThenMove=True)
  or after FINGER_STARTED_MOVING (when config.stimulusThenMove=False)
- Hiding the feedback arrow (runs on TRIAL_STARTED)
- Enabling the :class:`~trajtracker.movement.TrajectoryTracker` and all validators on FINGER_STARTED_MOVING,
  and disabling them on TRIAL_ENDED.


Initialization functions (in _n2p_init.py)
++++++++++++++++++++++++++++++++++++++++++

Here, the main program calls *create_experiment_objects()*; this function takes care of the complete
initialization process: it calls all the other functions in this file.

.. autofunction:: trajtracker.paradigms.num2pos.create_experiment_objects
.. autofunction:: trajtracker.paradigms.num2pos.create_numberline
.. autofunction:: trajtracker.paradigms.num2pos.create_start_point
.. autofunction:: trajtracker.paradigms.num2pos.create_traj_tracker
.. autofunction:: trajtracker.paradigms.num2pos.create_validators
.. autofunction:: trajtracker.paradigms.num2pos.create_textbox_target
.. autofunction:: trajtracker.paradigms.num2pos.create_generic_target
.. autofunction:: trajtracker.paradigms.num2pos.create_errmsg_textbox
.. autofunction:: trajtracker.paradigms.num2pos.register_to_event_manager
.. autofunction:: trajtracker.paradigms.num2pos.create_sounds
.. autofunction:: trajtracker.paradigms.num2pos.load_sound
.. autofunction:: trajtracker.paradigms.num2pos.load_data_source



Runtime functions (in _n2p_run.py)
++++++++++++++++++++++++++++++++++

.. autofunction:: trajtracker.paradigms.num2pos.run_full_experiment
.. autofunction:: trajtracker.paradigms.num2pos.run_trials
.. autofunction:: trajtracker.paradigms.num2pos.run_trial
.. autofunction:: trajtracker.paradigms.num2pos.initialize_trial
.. autofunction:: trajtracker.paradigms.num2pos.on_finger_touched_screen
.. autofunction:: trajtracker.paradigms.num2pos.wait_until_finger_moves
.. autofunction:: trajtracker.paradigms.num2pos.on_finger_started_moving
.. autofunction:: trajtracker.paradigms.num2pos.update_text_target_for_trial
.. autofunction:: trajtracker.paradigms.num2pos.update_generic_target_for_trial
.. autofunction:: trajtracker.paradigms.num2pos.update_movement
.. autofunction:: trajtracker.paradigms.num2pos.trial_failed
.. autofunction:: trajtracker.paradigms.num2pos.trial_succeeded
.. autofunction:: trajtracker.paradigms.num2pos.trial_ended
.. autofunction:: trajtracker.paradigms.num2pos.play_success_sound
.. autofunction:: trajtracker.paradigms.num2pos.save_session_file
