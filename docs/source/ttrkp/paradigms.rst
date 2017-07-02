.. Documentation of off-the-shelf paradigms


Off-the-shelf paradigms
=======================

TrajTracker also offers ready-to-use experimental paradigms: sets of functions that allow
creating your own experiment with almost no programming:

Example scripts with these paradigms are provided as part of the TrajTracker distribution,
under `samples/paradigms <http://github.com/trajtracker/trajtracker/tree/master/samples/paradigms>`_.

You can create your own number-to-position experiment in two ways:

* For most common features, you will only have to change the program configuration.

* If your experiment requires features that are not directly supported by the configuration offered,
  you can change the python code. To help you in that, see below the documentation of the functions
  that implement each of the two paradigms.

The list of trial is defined in a CSV file. The format of this files, including the
possible things you can configure via this file, are explained :doc:`here <input_data_format>`.

The results of each experiment session are saved in 3 files: a file with general data, a file with
trials information, and a trajectory file. See details :doc:`here <results>`.

Supported paradigms
-------------------

Number-to-position mapping
++++++++++++++++++++++++++

This paradigm shows a number line and various possible stimuli. The response is indicated by
dragging the finger to a location on the number line.

For an overview of this paradigm under TrajTracker, see
`the number-to-position page <https://drordotan.wixsite.com/trajtracker/ttrk-exp-num2pos>`_.

.. toctree::
   :maxdepth: 1
   :glob:

   Configuration: the Config class <num2pos/Config>
   Technical: the software design <num2pos/num2pos_design>
   Technical: the ExperimentInfo class <num2pos/ExperimentInfo>
   Technical: the TrialInfo class <num2pos/TrialInfo>


Discrete choice
+++++++++++++++

This paradigm shows two response buttons (in the top corners of the screen) and various possible stimuli.
The response is indicated by dragging the finger to one of the buttons.

For an overview of this paradigm under TrajTracker, see
`the discrete-choice page <https://drordotan.wixsite.com/trajtracker/ttrk-exp-dchoice>`_.

.. toctree::
   :maxdepth: 1
   :glob:

   Configuration: the Config class <dchoice/Config>
   Technical: the software design <dchoice/dchoice_design>
   Technical: the ExperimentInfo class <dchoice/ExperimentInfo>
   Technical: the TrialInfo class <dchoice/TrialInfo>


How to use these paradigms
--------------------------

Creating a simple experiment (that uses only the supported features)
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Several features are already supported by the paradigm we wrote. These features can be used
with almost no programming. To use them, you should:

- Create your main program by copy one of the existing sample scripts. The simplest ones are
  `number_to_position_1 <https://github.com/trajtracker/trajtracker/tree/master/samples/number_to_position_1>`_
  for number-to-position experiments and
  `dchoice_1 <https://github.com/trajtracker/trajtracker/tree/master/samples/dchoice_1>`_
  for discrete-choice experiments.
- In your script, set the experiment's general configuration parameters.
  This is done by updating the **Config** object (see here its documentation for
  :doc:`number-to-position <num2pos/Config>` and
  :doc:`discrete-choice <num2pos/Config>` experiments.
- Create a CSV file with the per-trial data. See :doc:`here <input_data_format>`
  a detailed description of this file format.

Even in this experiment, you may need to write minimal code - e.g., if you use non-text stimuli,
you would have to create them yourself (e.g., see the
`quantity_to_position <https://github.com/trajtracker/trajtracker/tree/master/samples/quantity_to_position>`_
sample experiment we created, where the stimuli are sets of dots).


Making advanced changes by modifying the code
+++++++++++++++++++++++++++++++++++++++++++++

If your experiment requires features that are not supported via the above configuration, you can modify
the relevant python functions. To help you on this, the following pages describe how the experiment
software is designed: for :doc:`number-to-position <num2pos/num2pos_design>` experiments
and for :doc:`discrete-choice <dchoice/dchoice_design>` experiments.

The simplest way to do such modifications is to copy the relevant functions into your own script.
You can see an example for the way it is done in the
`number_to_position_2 <https://github.com/trajtracker/trajtracker/tree/master/samples/number_to_position_2>`_
sample script.

Resource files
++++++++++++++

TrajTracker includes the source code for the two paradigms above, and also some resource files:

- Sounds (to indicate successful / incorrect trial)
- Images for simple stimuli

These files are in the `src/res <https://github.com/trajtracker/trajtracker/tree/master/src/res>`_ sub-directory.
