
CSV configuration file
======================

The CSV file contains one line per trial. In this file, you define the target location on the number line,
as well as the stimulus to present.

You can also optionally define the times when it appears or disappears, and its position. This will be useful
if you want to change some of these parameters on each trial.

**Target:**

There are two columns where you can indicate the target to present - one for text targets
(a :class:`~trajtracker.stimuli.MultiTextBox`) and one for non-text targets (a
:class:`~trajtracker.stimuli.MultiStimulus` ). Each of these columns can include several stimuli, separated by
semicolon. In other columns, you can define the time when each of these stimuli will appear on screen
and disappear.

- **text.target**: The text(s) to present as the target stimulus.

- **genstim.target** - The :class:`~trajtracker.stimuli.MultiStimulus` generic stimulus keeps all stimuli in a
  :class:`~trajtracker.stimuli.StimulusSelector` , where each stimulus has a string ID. *genstim.target* is the
  ID(s) of the stimulus (or stimuli) to present as targets.

  If you include here several semicolon-separated stimulus IDs (e.g. to create an RSVP),
  you can repeat the same target more than once (e.g. "shape1;shape2;shape1;shape3").

  This column is mandatory if you are using generic stimuli (*config.use_generic_targets = True*)

- **target** (mandatory column): The target location on the number line. If you use text stimuli
  (*config.use_text_targets = True*) and the *text.target* column was not defined, the *target* column
  indicates not only the target location, but also the single text stimulus.


**Optional columns:**

Columns that refer to the text stimuli (the :class:`~trajtracker.stimuli.MultiTextBox`) are called *text.<something>*.
Columns that refer to non-text stimuli (the :class:`~trajtracker.stimuli.MultiStimulus`) are called *genstim.<something>*.
Columns that refer to fixation stimulus are called *fixation.<something>*.

All columns can contain either a single value or a semicolon-separated list of values (at least one per target;
excessive values are ignored).

- **text.position**, **genstim.position**, **fixation.position**: The stimulus position - x and y coordinates, separated by
  a colon, e.g.: "10:20" for x=10, y=20. If you specified several target stimuli, you can define here a
  semicolon-separated list of positions.

- **text.position.x**, **text.position.y**, **genstim.position.x**, **genstim.position.y**,
  **fixation.position.x**, **fixation.position.y**: The stimulus position - either x or y coordinates
  (the other coordinate can be defined either in another column or just in the initialization script).

- **text.onset_time**, **genstim.onset_time**: The time to present the stimulus, specified in seconds relatively
  to the baseline event (which is TRIAL_STARTED in case config.stimulusThenMove is True, and FINGER_STARTED_MOVING
  in case config.stimulusThenMove is False).

  If several targets were specified (in the **text.target** or
  **genstim.target** columns), you cannot specify a single onset_time - you must provide an onset_time per target.

- **text.duration**, **genstim.duration**: The duration of presenting the target (in seconds),
  or a semicolon-separated list of durations - one per target.

- **text.font**: The font name; or a semicolon-separated list of names.

- **text.text_size**: The font size (integer); or a semicolon-separated list of integers.

- **text.bold**: Use bold font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

- **text.italic**: Use italic font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

- **text.underline**: Use underline font (boolean - "True" or "False"); or a semicolon-separated list of booleans.

- **text.justification**: Horizontal justification - the word "left", "right", or "center";
  or a semicolon-separated list of justifications.

- **text.text_colour**: The font RGB color - 3 colon-separated integers between 0 and 255
  (R:G:B, e.g., "0:0:255" is blue); or a semicolon-separated list of RGB's.

- **text.background_colour**: Background color (R:G:B); or a semicolon-separated list of RGB's.

- **text.size**: The textbox size, in pixels (width:height); or a semicolon-separated list of sizes

- **fixation.text**: The text to show as fixation stimulus. This is applied only if
  config.fixation_type = 'text'
