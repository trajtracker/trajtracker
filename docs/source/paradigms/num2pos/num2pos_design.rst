
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
- TrialInfo : an object that keeps the information about the present trial.




The persistent objects
++++++++++++++++++++++

The following objects exist throughout the experiment session (all are stored as part of the
:class:`~trajtracker.paradigms.num2pos.ExperimentInfo` object):

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

- A list of :class:`~trajtracker.paradigms.num2pos.TrialInfo` objects, typically created by loading from the CSV file.

- The :doc:`Config <Config>` object and some other configuration parameters (e.g., result file names,
  subject ID and name, etc.).

- A *dict* with experiment-level results (which is saved to the results file at the end of the exepriment).
  Trial-level results (which are saved in trials.csv) are stored on the :class:`~trajtracker.paradigms.num2pos.TrialInfo`
  object.


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

- Showing/hiding stimuli: this happens in certain delay after TRIAL_STARTED (when
  :attr:`config.stimulus_then_move <trajtracker.paradigms.num2pos.Config.stimulus_then_move>` = True)
  or after FINGER_STARTED_MOVING (when
  :attr:`config.stimulus_then_move <trajtracker.paradigms.num2pos.Config.stimulus_then_move>` = False)
- Hiding the feedback arrow (runs on TRIAL_STARTED)
- Enabling the :class:`~trajtracker.movement.TrajectoryTracker` and all validators on FINGER_STARTED_MOVING,
  and disabling them on TRIAL_ENDED.


Initialization functions
++++++++++++++++++++++++

Here, the main program calls *create_experiment_objects()*; this function takes care of the complete
initialization process: it calls all the other functions in this file.

Functions in _n2p_init.py (specific to number-to-position paradigm)
-------------------------------------------------------------------

.. autofunction:: trajtracker.paradigms.num2pos.create_experiment_objects
.. autofunction:: trajtracker.paradigms.num2pos.create_numberline
.. autofunction:: trajtracker.paradigms.num2pos.create_sounds
.. autofunction:: trajtracker.paradigms.num2pos.load_data_source


Functions in _common_funcs_init.py (common to several paradigms)
----------------------------------------------------------------

.. autofunction:: trajtracker.paradigms.common.create_errmsg_textbox
.. autofunction:: trajtracker.paradigms.common.create_fixation
.. autofunction:: trajtracker.paradigms.common.create_fixation_cross
.. autofunction:: trajtracker.paradigms.common.create_generic_target
.. autofunction:: trajtracker.paradigms.common.create_start_point
.. autofunction:: trajtracker.paradigms.common.create_textbox_fixation
.. autofunction:: trajtracker.paradigms.common.create_textbox_target
.. autofunction:: trajtracker.paradigms.common.create_traj_tracker
.. autofunction:: trajtracker.paradigms.common.create_validators
.. autofunction:: trajtracker.paradigms.common.get_subject_name_id
.. autofunction:: trajtracker.paradigms.common.load_sound
.. autofunction:: trajtracker.paradigms.common.register_to_event_manager



Functions that run the experiment
+++++++++++++++++++++++++++++++++


Functions in _n2p_run.py (specific to number-to-position paradigm)
------------------------------------------------------------------

.. autofunction:: trajtracker.paradigms.num2pos.run_full_experiment

.. autofunction:: trajtracker.paradigms.num2pos.initialize_trial
.. autofunction:: trajtracker.paradigms.num2pos.on_finger_touched_screen
.. autofunction:: trajtracker.paradigms.num2pos.play_success_sound
.. autofunction:: trajtracker.paradigms.num2pos.run_trials
.. autofunction:: trajtracker.paradigms.num2pos.run_trial
.. autofunction:: trajtracker.paradigms.num2pos.trial_ended
.. autofunction:: trajtracker.paradigms.num2pos.trial_failed
.. autofunction:: trajtracker.paradigms.num2pos.trial_succeeded

Functions in _common_funcs_run.py (common to several paradigms)
---------------------------------------------------------------

.. autofunction:: trajtracker.paradigms.common.init_experiment
.. autofunction:: trajtracker.paradigms.common.on_finger_started_moving
.. autofunction:: trajtracker.paradigms.common.open_trials_file
.. autofunction:: trajtracker.paradigms.common.save_session_file
.. autofunction:: trajtracker.paradigms.common.show_fixation
.. autofunction:: trajtracker.paradigms.common.update_attr_by_csv_config
.. autofunction:: trajtracker.paradigms.common.update_fixation_for_trial
.. autofunction:: trajtracker.paradigms.common.update_generic_target_for_trial
.. autofunction:: trajtracker.paradigms.common.update_movement_in_traj_sensitive_objects
.. autofunction:: trajtracker.paradigms.common.update_text_target_for_trial
.. autofunction:: trajtracker.paradigms.common.update_obj_position
.. autofunction:: trajtracker.paradigms.common.wait_until_finger_moves
