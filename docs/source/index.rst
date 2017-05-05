.. TrajTracker documentation master file, created by
   sphinx-quickstart on Mon Feb 20 15:35:23 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TrajTracker documentation
=========================

Expyriment-based tools for psychology experiments, focusing on finger/mouse tracking


trajtracker.stimuli
-------------------

Visual objects.

.. toctree::
   :maxdepth: 1
   :glob:

   stimuli/*


trajtracker.validators
----------------------

Perform various validations on mouse/finger movement during the trial.

.. toctree::
   :maxdepth: 1
   :glob:

   validators/*


trajtracker.movement
--------------------

Classes that handle various aspects of finger/mouse movement.


**Animate a visual object along a given path:**

.. toctree::
   :maxdepth: 1
   :glob:

   movement/StimulusAnimator
   movement/CircularTrajectoryGenerator
   movement/CustomTrajectoryGenerator
   movement/LineTrajectoryGenerator
   movement/SegmentedTrajectoryGenerator


**Monitor the finger/mouse movement:**

.. toctree::
   :maxdepth: 1
   :glob:

   movement/DirectionMonitor
   movement/Hotspot
   movement/SpeedMonitor
   movement/StartPoint
   movement/RectStartPoint
   movement/TrajectoryTracker


trajtracker.events
------------------

This set of classes allows defining the flow of a trial by using events.

Before looking at specific classes, check out :doc:`this overview <events/events_overview>`.

.. toctree::
   :maxdepth: 1
   :glob:

   events/Event
   events/EventManager


trajtracker.misc
----------------

.. toctree::
   :maxdepth: 1
   :glob:

   misc/*


other modules
-------------

.. toctree::
   :maxdepth: 1
   :glob:

   utils




Off-the-shelf paradigms
=======================

TrajTracker also offers ready-to-use experimental paradigms: sets of functions that allow
creating your own experiment with almost no programming.:

* :doc:`Number-to-position mapping <paradigms/num2pos/num2pos>` experiments
* Dual-choice experiments: coming up soon


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

