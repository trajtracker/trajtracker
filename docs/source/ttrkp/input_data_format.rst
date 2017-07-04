:orphan:

CSV configuration file
======================

The file format for number-to-position experiments and discrete-choice experiments is very similar.
This page describes both.

Overview
++++++++

The CSV file contains one line per trial. The possible columns in this file are defined below.

Via the CSV config file, you can define per trial:

- The stimuli to show
- The time when stimuli appear / disappear
- The fixation text (in case you used *config.use_text_targets = True*)
- Visual properties of the stimuli, the fixation, and the number line (e.g., position, font, etc.)
- The target location (in case of number-to-position experiments)

All columns that refer to stimuli can contain either a single value or a semicolon-separated list of values
(at least one per target; excessive values are ignored).


Conventions for column names
++++++++++++++++++++++++++++

- Columns that refer to the text stimuli (the *MultiTextBox* object) are called *text.<something>*.
- Columns that refer to non-text stimuli (the *MultiStimulus* object) are called *genstim.<something>*.
- Columns that refer to the fixation stimulus are called *fixation.<something>*.
- In the number-to-position paradigm: Columns that refer to the number line are called *nl.<something>*.



Columns to define the target stimulus & response location
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

There are two columns where you can indicate the target to present - one for text targets
(a `MultiTextBox <http://trajtracker.com/apiref/ttrk/stimuli/MultiTextBox.html>`_)
and one for non-text targets (a `MultiTextBox <http://trajtracker.com/apiref/ttrk/stimuli/MultiStimulus.html>`_).
Each of these columns can include several stimuli, separated by
semicolon. In other columns, you can define the time when each of these stimuli will appear on screen
and disappear.

**text.target**
    The text(s) to present as the target stimulus.

**genstim.target**
    The *MultiStimulus* generic stimulus keeps all stimuli in a
    `StimulusSelector <http://trajtracker.com/apiref/ttrk/stimuli/StimulusSelector.html>`_
    where each stimulus has a string ID. *genstim.target* is the
    ID(s) of the stimulus (or stimuli) to present as targets.

    If you include here several semicolon-separated stimulus IDs (e.g. to create an RSVP),
    you can repeat the same target more than once (e.g. "shape1;shape2;shape1;shape3").

    This column is mandatory if you are using generic stimuli (*config.use_generic_targets = True*)

**target** (mandatory column, exists only in the number-to-position paradigm)
    The target location on the number line. If you use text stimuli
    (*config.use_text_targets = True*) and the *text.target* column was not defined, the *target* column
    indicates not only the target location, but also the single text stimulus.


**expected_response**
    In the discrete-choice paradigm, this column indicates which is the correct response button:
    0 (left) or 1 (right).

**left_resp_btn.text, right_resp_btn.text**
    In the discrete-choice paradigm: text to write on each of the response buttons


Columns to define visual properties
+++++++++++++++++++++++++++++++++++

All these columns are optional.

| **text.position**
| **genstim.position**
| **fixation.position**
| **nl.position**
|   The position of the stimulus / fixation / number line - x and y coordinates, separated by
    a colon, e.g.: "10:20" for x=10, y=20.

| **text.position.x**
| **text.position.y**
| **genstim.position.x**
| **genstim.position.y**
| **fixation.position.x**
| **fixation.position.y**
| **nl.position.x**
| **nl.position.y**
|   The position of the stimulus / fixation / number line - either x or y coordinates
    (the other coordinate can be defined either in another column or just in the initialization script).

| **nl.position.x%**
| **fixation.position.x%**
|     Specify the horizontal position of the fixation / number line as percentage of the screen width

| **text.onset_time**
| **genstim.onset_time**
|   The time to present the stimulus, specified in seconds relatively
    to the baseline event (which is TRIAL_STARTED in case config.stimulusThenMove is True, and FINGER_STARTED_MOVING
    in case config.stimulusThenMove is False).

    If several targets were specified (in the **text.target** or
    **genstim.target** columns), you cannot specify a single onset_time - you must provide an onset_time per target.

| **text.duration**
| **genstim.duration**
|   The duration of presenting the target (in seconds),
    or a semicolon-separated list of durations - one per target.

**text.font**
    The font name; or a semicolon-separated list of names.

**text.text_size**
    The font size (integer); or a semicolon-separated list of integers.

**text.bold**
    Use bold font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

**text.italic**
    Use italic font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

**text.underline**
    Use underline font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

**text.justification**
    Horizontal justification - the word "left", "right", or "center";
    or a semicolon-separated list of justifications.

**text.text_colour**
    The font RGB color - 3 colon-separated integers between 0 and 255
    (R:G:B, e.g., "0:0:255" is blue); or a semicolon-separated list of RGB's.

**text.background_colour**
    Background color (R:G:B); or a semicolon-separated list of RGB's.

**text.size**
    The textbox size, in pixels (width:height); or a semicolon-separated list of sizes

**fixation.text**
    The text to show as fixation stimulus. This is applied only if *config.fixation_type = 'text'*


Columns to modify behavior
++++++++++++++++++++++++++

**min_movement_time**
    The finger's minimal movement time (= duration from starting to move until making a response)
