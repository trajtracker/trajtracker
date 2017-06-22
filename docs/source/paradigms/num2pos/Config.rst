.. TrajTracker : Config.py

Config class
============

Configuration parameters for a number-to-position experiment.

All parameters can be set directly and via the constructor.

.. currentmodule:: trajtracker.paradigms.num2pos

.. include:: Config_common.txt


Number line
-----------

.. autoinstanceattribute:: Config.max_numberline_value
    :annotation: - number, mandatory parameter

    The value at the right end of the number line.

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
        any larger error

.. autoinstanceattribute:: Config.sounds_dir
    :annotation: = "./sounds" (str)

    The name of the directory where the sound files are located
