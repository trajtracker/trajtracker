.. TrajTracker : Config.py

Config class (discrete choice)
==============================

Configuration parameters for a discrete-choice experiment.

All parameters can be set directly and via the constructor.

.. include:: Config_common.txt

.. currentmodule:: trajtrackerp.dchoice


Response buttons
----------------


.. autoinstanceattribute:: Config.resp_btn_colours
    :annotation: = Grey (RGV color)

    Colour of the response button. If two colours are provided, they will be used
    for the left and right buttons, correspondingly.

.. autoinstanceattribute:: Config.resp_btn_font_name
    :annotation: = 'Arial' (str)

.. autoinstanceattribute:: Config.resp_btn_font_size
    :annotation: = 16 (int)

.. autoinstanceattribute:: Config.resp_btn_positions
    :annotation: = None

    Position of the response button. This can be either of:

    - (x,y) tuple denoting the position of the right button. The left button will be symmetric.
    - A list with (x,y) positions of both buttons - [(xleft,yleft), (xright,yright)]

.. autoinstanceattribute:: Config.resp_btn_size
    :annotation: = (0.05, 0.1) (tuple width, height)

    Size of the response buttons.
    Specify fractions between 0 and 1 to indicate % of screen width/height.

.. autoinstanceattribute:: Config.resp_btn_texts
    :annotation: = None (str)

    Text of the response buttons. If two texts are provided, they will be used
    for the left and right buttons, correspondingly.

.. autoinstanceattribute:: Config.resp_btn_text_colour
    :annotation: = White (RGV color)

    A single color, used for both buttons.



Visual feedback on responses
----------------------------

How to use it:

- Determine the type of feedback stimulus (rectangle/pictures) by setting
  :attr:`~trajtrackerp.dchoice.Config.feedback_stim_type` .
- Determine where the stimulus appears: set :attr:`~trajtrackerp.dchoice.Config.feedback_stim_position`
  or rely on default positions by setting :attr:`~trajtrackerp.dchoice.Config.feedback_place`
- For rectangle feedback, use the other properties to set its size, color, etc.
- Each trial can show either of two feedback stimuli. Set
  :attr:`~trajtrackerp.dchoice.Config.feedback_select_by` to decide how to select one
  of these two stimuli.


.. autoinstanceattribute:: Config.feedback_stim_type
    :annotation: = None

    The kind of feedback stimulus to show, following a participant response:

    - 'rectangle': a rectangle (you can configure its shape and position)
    - 'picture': Configure it via :attr:`~trajtrackerp.dchoice.Config.feedback_pictures`

.. autoinstanceattribute:: Config.feedback_place
    :annotation: = 'button'

    Where to place the feedback stimuli. This affects the default values of
    :attr:`~trajtrackerp.dchoice.Config.feedback_stim_position` and
    :attr:`~trajtrackerp.dchoice.Config.feedback_btn_colours`

    Valid values:

    - 'buttons': over the response buttons
    - 'middle': between the buttons (on top of screen)

.. autoinstanceattribute:: Config.feedback_select_by
    :annotation: = 'response'

    Determnes how to select which of the two feedback stimuli will be shown.
    Possible values:

    - 'response': The feedback is determined by the button touched
    - 'expected': The feedback is the button that should be pressed
    - 'accuracy': The feedback is determined by whether the touched button was correct.
                     (when configuring the two feedback stimuli, e.g., size and position,
                     the first one refers to correct response).
                     If you use this feature, you must include an "expected_response" column in the
                     trials CSV file.

.. autoinstanceattribute:: Config.feedback_btn_colours

    The colour of the feedback button/rectangle. If two colors are provided, the first colour will
    be used for correct responses and the second colour for incorrect responses

    Default: Green for feedback_place = 'button', [Green Red] for feedback_place = 'middle'

.. autoinstanceattribute:: Config.feedback_duration
    :annotation: = 0.2 (number)

    Duration (in seconds) for which feedback is presented

.. autoinstanceattribute:: Config.feedback_rect_size
    :annotation: (optional)

    The size of the feedback stimuli: either (width, height) if both have the same size,
    or an array of two sizes i.e. [(width1, height1), (width2, height2)].

    - For feedback_place = 'button', the default size is the size of the response buttons.
    - For feedback_place = 'middle', you should either specify feedback_rect_size and
      feedback_stim_position or neither of them.
      Default: the feedback rectangle will be at the top of the screen, between the two buttons.

      For feedback_place = 'middle', if a single number is defined here, it denotes
      the rectangle's height.

.. autoinstanceattribute:: Config.feedback_stim_position
    :annotation: (optional)

    The position of the feedback stimulus - either (x,y) coordinates (indicating that
    both feedback areas are in the same location) or [(x1,y1), (x2,y2)].

    - For feedback_place = 'middle', the default position is in the middle-top of the screen.
    - For feedback_place = 'button', the default position is at the two top corners of the screen.

.. autoinstanceattribute:: Config.feedback_pictures
    :annotation: (array with two expyriment.stimuli.Picture objects)

    Pictures to use as feedback (when feedback_mode = 'picture').
