.. TrajTracker : Config.py

Config class (number-to-position)
=================================

Configuration parameters for a number-to-position experiment.

All parameters can be set directly and via the constructor.

.. include:: Config_common.txt

.. currentmodule:: trajtrackerp.num2pos


Number line
-----------

.. autoinstanceattribute:: Config.max_numberline_value
    :annotation: - number, mandatory parameter

    The value at the right end of the number line.

.. autoinstanceattribute:: Config.max_response_excess
    :annotation: = None (number)

    Determines how far it's valid to go beyond the end of the number line on each side.
    Responses farther than this will result in an an error.
    The value is specified as percentage of the number line's length (e.g., 0.1 = allow exceeding the ends of
    the number line by 10% its length to either direction).

.. autoinstanceattribute:: Config.min_numberline_value
    :annotation: = 0 (number)

    The value at the left end of the number line.

.. autoinstanceattribute:: Config.nl_labels_visible
    :annotation: = True (bool)

    Whether to show labels at the end of the number line (with min/max values)

.. autoinstanceattribute:: Config.nl_length
    :annotation: = 0.9 (number)

    The length of the number line. The length is specified either in pixels (an int value larger than 1)
    or as percentage of the screen width (a number between 0 and 1).

.. autoinstanceattribute:: Config.nl_offset_event
    :annotation: = None (trajtracker.events.Event)

    Defines when the number line should be hidden.

.. autoinstanceattribute:: Config.nl_onset_event
    :annotation: = None (trajtracker.events.Event)

    Defines when the number line should be displayed. If False, the number line will be displayed from
    the start of the experiement.

.. autoinstanceattribute:: Config.show_feedback
    :annotation: = True (bool)

    Whether to show a feedback arrow (where the finger landed on the number line)

.. autoinstanceattribute:: Config.feedback_accuracy_levels
    :annotation: = None (list of numbers)

    Use this to show the feedback arrow in different colors, depending on the response accuracy.
    Define a list of numbers between 0 and 1 (percentages of the number line length). Configure
    the corresponding colors in *feedback_arrow_colors*.

.. autoinstanceattribute:: Config.feedback_arrow_colors
    :annotation: = [Green] (list of RGB colors)

    Color of the feedback arrow (or a list of colors, in case you defined feedback_accuracy_levels;
    in this case, the first color corresponds with best accuracy)

.. autoinstanceattribute:: Config.post_response_target
    :annotation: = False (bool)

    Whether to show the correct target location, as a downward-pointing arrow along the number line,
    after the response was made

.. autoinstanceattribute:: Config.nl_line_width
    :annotation: = 2 (int)

    Width (in pixels) of the number line

.. autoinstanceattribute:: Config.nl_end_tick_height
    :annotation: = 5 (int)

    height (in pixels) of the ticks at the end of the line

.. autoinstanceattribute:: Config.nl_line_colour
    :annotation: = White (RGB)

    The line colour

.. autoinstanceattribute:: Config.nl_labels_box_size
    :annotation: - (width, height)

    Size (in pixels) of the end-of-line labels' text box

.. autoinstanceattribute:: Config.nl_labels_font_name
    :annotation: = 'Arial' (str)

.. autoinstanceattribute:: Config.nl_labels_colour
    :annotation: = Grey (RGB color)

.. autoinstanceattribute:: Config.nl_labels_offset
    :annotation: = (0, 0) (tuple x, y)

    Offset to move labels (relatively to their default position)

.. autoinstanceattribute:: Config.nl_distance_from_top
    :annotation: = 80 (int)

    Distance of the numberline's main line from top-of-screen (in pixels)



Sounds
------

.. autoinstanceattribute:: Config.sound_by_accuracy
    :annotation: = None

        Use this in order to play a different sound depending on the subject's accuracy.
        The parameter should be a list/tuple with several elements, each of which is a (endpoint_error, sound)
        tuple. "endpoint_error" indicates a top error (as ratio of the number line length),
        and "sound" is a sound file name.

        The worst accuracy is ignored (e.g., if you specify [(0.05, 'good.wav'), (0.5, 'bad.wav')]
        the program will play good.wav for endpoint errors up to 5% of the line length, and bad.wav for
        any larger error.

        If you only use a single sound for good trials, don't use this parameter; use
        :attr:`~trajtrackerp.num2pos.Config.sound_ok` instead

.. autoinstanceattribute:: Config.sounds_dir
    :annotation: = "./sounds" (str)

    The name of the directory where the sound files are located

.. autoinstanceattribute:: Config.sound_err
    :annotation: = 'error.wav' (str)

    Name of a WAV file (in :attr:`~trajtrackerp.num2pos.Config.sounds_dir`) - sound to play
    in case of error (i.e. failed trial).

.. autoinstanceattribute:: Config.sound_ok
    :annotation: = 'click.wav' (str)

    Name of a WAV file (in :attr:`~trajtrackerp.num2pos.Config.sounds_dir`) - sound to play
    when the trial ended successfully.

    No need for this if :attr:`~trajtrackerp.num2pos.Config.sound_by_accuracy` was specified.
