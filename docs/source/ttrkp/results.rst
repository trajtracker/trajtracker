:orphan:


Experiment results
==================

Each experiment session yields 3 results files, stored in the *data* sub-directory:

- General information about the experiment session (e.g., when it was run, the subject ID, the
  experiment ID, etc.).

  File name: *session_<subjid>_<time>.xml*

- Trials file: a CSV file with one line per trial, containing various trial-level information.

  File name: *trials_<subjid>_<time>.csv*

- Trajectory file: a CSV file with the trajectory data.

  File name: *trajectory_<subjid>_<time>.csv*

In all files, <subjid> is the subject ID provided in the application's welcome page (not Expyriment's opening page).


session.xml file
----------------

The file contains various parameters about the experiment session, as detailed below.

.. code-block:: xml
   :caption: session.xml

    <data>
      <source>
        <software name="TrajTracker" version="0.0.1"/>
        <paradigm name="NL" version="1.0"/> <!-- NL: Indicates that this is the numberline paradigm -->
                                            <!-- version: of the number to position package-->
        <experiment name="Num2Pos(0-100*2)"/>  <!-- The value provided in config.experiment_id -->
      </source>

      <subject expyriment_id="5" id="dd">  <!-- expyriment_id: subject ID provided in Expyriment's opening page -->
                                           <!-- id: subject ID provided in the page following the subject name -->
        <name>Dror Dotan</name>            <!-- As provided in the opening page -->
      </subject>

      <session start_time="2017-05-08 21:08:03">

        <exp_level_results>
          <data name="WindowWidth" type="number" value="800" />          <!-- In pixels -->
          <data name="WindowHeight" type="number" value="600" />

          <data name="nTrialsFailed" type="number" value="1" />
          <data name="nTrialsSucceeded" type="number" value="202" />
          <data name="nTrialsCompleted" type="number" value="5" />   <!-- Succeeded and failed -->

          <data name="nExpectedTrials" type="number" value="4" />    <!-- No. of trials in the data source -->

          <!-- The position that counts as the start of movement (above the "start" rectangle) -->
          <data name="TrajZeroCoordX" type="number" value="0" />
          <data name="TrajZeroCoordY" type="number" value="-270" />

        </exp_level_results>

        <!-- Names of the other results files -->
        <files>
          <file name="trials_dd_20170508_2108.csv" type="trials" />
          <file name="trajectory_dd_20170508_2108.csv" type="trajectory" />
        </files>

      </session>

    </data>



Trials file
-----------

The trials file contains one line per completed trial (both succeeded and failed). It has the following columns:

- **trialNum**: The trial's serial number
- **LineNum**: The line number in the input CSV trials file
- **presentedTarget**: The stimulus presented
- **status**: Either "OK" or "ERR_<error-code>"
- **movementTime**: Time (in seconds) between the finger starting to move and reaching the number line
- **timeInSession**: The time when the trial started, relatively to the session start time.
- **timeUntilFingerMoved**: Time from touching the screen until the finger left the "start" area.
- **timeUntilTarget**: Time from touching the screen until the target's t=0 (note that if you defined
  onset_time > 0 for all targets, this time will be earlier than the targets' actual onset time).
  In stimulusThenMove mode, this value is always 0.
- The columns from the :doc:`trials input file <input_data_format>`.
- **text.position, genstim.position**: These fields will appear if the input file changed the stimulus position
  in any way (even if only x or y coordinates were defined). They will contain the stimuli position(s), formatted
  as x1:y1;x2:y2;x3:y3 etc.

In the number-to-position paradigm, the file also contains these columns:

- **target**: The target location
- **endPoint**: The location mrked by the subject on the number line, using the number line's scale
- **nl.position.x, nl.position.y**: The number line's position, in pixels. These columns will appear even if the
  input file contained the columns *nl.position.x%* or *nl.position.y%*

In the discrete-choice paradigm, the file also contains these columns:

- **expectedResponse**: The button expected to be selected (0 = left, 1 = right, -1 = unknown)
- **UserResponse**: The button actually selected (0 = left, 1 = right)

Trajectory file
---------------

The trials file contains one line per trajetory point. Only succeeded trials are saved here.
The file has the following columns:

- **trial**: The trial number (matches *trialNum* in the trials.csv file)
- **time**: The time when this point was sampled, relatively to the trial's start time (when
  the finger touched the screen).
- **x**, **y**: Coordinates
