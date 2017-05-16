.. TrajTracker : Config.py

Config class
============

Configuration parameters for a number-to-position experiment.

All parameters can be set directly and via the constructor.

Some advanced config parameters are not documented here - see the source file for details.


General:
--------

    **experiment_id**  (str, mandatory parameter)
       A unique ID of the present experiment configuration. Will be saved as-is in the results file,
       to help you identify the specific configuration you were executing.

Targets to show
---------------

    **data_source** (str, mandatory parameter)
       The name of a CSV file with the per trial data. See (TBD) for detailed description of this file format.
       Alternatively, you can provide a list of numbers, each of which will be presented as a text target.

    **shuffle_trials** (bool, default: True)
       Whether to randomize the order of trials, or to present them in the order in which they
       were provided in data_source.

    **use_text_targets** (bool, default: True)
       Whether to present text targets. If True, you should have a *text.target* column in the CSV file.

    **text_target_height** (number, default: 1.0)
        The height of the text target, specified as percentage of the available distance
        between the number line and the top of the screen (value between 0 and 1).
        The actual target size (in pixels) will be printed in the output file.

    **use_generic_targets** (bool, default: False)
       Whether to present generic targets. A generic target is any Expyriment (or equivalent) stimulus - e.g.,
       image, shape, etc.

    **fixation_type**
       The type of fixation stimulus: 'cross', 'text', or None.
       When using 'text' fixation, you can set the text via *fixation_text* or via the CSV config file.

    **fixation_text**
       The default fixation text to use when *fixation_type='text'*.
       This value can be overriden by column *fixation.text* in the CSV config file.


Number line
-----------

    **max_numberline_value** (number, mandatory parameter)
        The value at the right end of the number line.

    **show_feedback** (bool, default: True)
        Whether to show a feedback arrow (where the finger landed on the number line)

    **feedback_accuracy_levels** (list of numbers, default: None)
        Use this to show the feedback arrow in different colors, depending on the response accuracy.
        Define a list of numbers between 0 and 1 (percentages of the number line length). Configure
        the corresponding colors in *feedback_arrow_colors*.

    **feedback_arrow_colors** (list of RGB colors, default: [Green])
        Color of the feedback arrow (or a list of colors, in case you defined feedback_accuracy_levels;
        in this case, the first color corresponds with best accuracy)

    **post_response_target** (bool, default: False)
        Whether to show the correct target location, as a downward-pointing arrow along the number line,
        after the response was made


"Start" rectangle
-----------------

    **stimulus_then_move** (bool, default: False)
        *True*: The software decides when the target appears, and then the finger must start moving

        *False*: The finger moves at will and this is what triggers the appearance of the target

    **finger_moves_min_time, finger_moves_max_time** (number, default: None)
        The minimal/maximal time (in seconds) in which the finger should start moving.
        The time is specified relatively to the time point of touching the screen

    **start_point_size** (tuple (width, height); default: (40, 30))
        The size of the "start" rectangle, in pixels.

    **start_point_tilt** (number, default: 0)
        Rotation of the "start" rectangle (clockwise degrees)

    **start_point_colour** (RGB color, default: Grey)
        Colour of the "start" rectangle


Sounds
------

    **sound_by_accuracy** (default: None)
        Use this in order to play a different sound depending on the subject's accuracy.
        The parameter should be a list/tuple with several elements, each of which is a (endpoint_error, sound)
        tuple. "endpoint_error" indicates a top error (as ratio of the number line length),
        and "sound" is a sound file name.

        The worst accuracy is ignored (e.g., if you specify [(0.05, 'good.wav'), (0.5, 'bad.wav')]
        the program will play good.wav for endpoint errors up to 5% of the line length, and bad.wav for
        any larger error

    **sounds_dir** (str, default: "./sounds")
        The name of the directory where the sound files are located


Movement restrictions (validators)
----------------------------------

    **min_trial_duration** (number, default: 0.2)
        Minimal valid time from leaving the "start" rectangle until reaching the number line (in seconds)

    **max_trial_duration** (number, mandatory parameter)
        Maximal valid time from leaving the "start" rectangle until reaching the number line (in seconds)
        This parameter also affects the speed limit per time point (via
        :class:`~trajtracker.validators.GlobalSpeedValidator` )

    **speed_guide_enabled** (bool, default: False)
        If True, the speed limit will be visualized as a moving line.
        This parameter applies to :class:`~trajtracker.validators.GlobalSpeedValidator`

    **min_inst_speed** (number, default: 10)
        The minimal instantaneous speed (pixels per second).
        This parameter applies to :class:`~trajtracker.validators.InstantaneousSpeedValidator`

    **grace_period** (number, default: 0.3)
        Duration (in seconds) in the beginning of the trial during which speed is not validated.
        This parameter applies both to :class:`~trajtracker.validators.InstantaneousSpeedValidator` and to
        :class:`~trajtracker.validators.GlobalSpeedValidator`

    **max_zigzags** (int, default: 8)
        Maximal number of left-right deviations allowed per trial.
        This parameter applies to :class:`~trajtracker.validators.NCurvesValidator`

    **save_results** (bool, default: True)
        Whether to save the results (trials and trajectory).
