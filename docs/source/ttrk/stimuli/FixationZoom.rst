.. TrajTracker : FixationZoom.py


FixationZoom class
====================

A fixation stimulus that starts as 4 dots, organized on the corners of a rectangle, and then moves
them in to the rectangle's center.


Using this class
----------------


Without the :doc:`events mechanism <../events/events_overview>`
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Create the FixationZoom
- Add :attr:`~trajtracker.stimuli.FixationZoom.stimulus` to your :class:`~trajtracker.stimuli.StimulusContainer`
- When the trial is initialized, call :func:`~trajtracker.stimuli.FixationZoom.reset`
- To show the fixation, call :func:`~trajtracker.stimuli.FixationZoom.show`
- To start zooming in the dots, call :func:`~trajtracker.stimuli.FixationZoom.start_zoom`
- To refresh the position of the dots as they zoom in, call :func:`~trajtracker.stimuli.FixationZoom.update`
  or :func:`~trajtracker.stimuli.FixationZoom.update_xyt` on each frame.
- When timed out, the dots will auto-hide. Alternatively, you can explicitly call
  :func:`~trajtracker.stimuli.FixationZoom.hide` to hide them and terminate the zoom-in process.


With the :doc:`events mechanism <../events/events_overview>`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

- Create the FixationZoom
- Add :attr:`~trajtracker.stimuli.FixationZoom.stimulus` to your :class:`~trajtracker.stimuli.StimulusContainer`
- Define :attr:`~trajtracker.stimuli.FixationZoom.start_zoom_event`, and (optionally)
  :attr:`~trajtracker.stimuli.FixationZoom.show_event`
- Register the FixationZoom to an :class:`~trajtracker.events.EventManager`
- When the trial is initialized, call :func:`~trajtracker.stimuli.FixationZoom.reset`
- To refresh the position of the dots as they zoom in, call :func:`~trajtracker.stimuli.FixationZoom.update`
  or :func:`~trajtracker.stimuli.FixationZoom.update_xyt` on each frame.
- When timed out, the dots will auto-hide. Alternatively, you can explicitly call
  :func:`~trajtracker.stimuli.FixationZoom.hide` to hide them and terminate the zoom-in process.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.FixationZoom
   :members:
   :inherited-members:
   :member-order: alphabetical


