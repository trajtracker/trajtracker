.. TrajTracker : Slider.py

Slider class
============

A slider is used to set a value on a given scale: you use the mouse to drag a gauge along a given
line (or any other stimulus on your choice). The gauge's physical coordinate
is translated to a value on a customizable linear scale.


Main features:

- Vertical / horizontal slider.
- Get the slider value using a numeric scale of your choice.
- Track the number of times the gauge was moved since the trial started.
- Limit the gauge movement (how far it can move, how many times it can move).
- Configurable background stimulus (e.g. a line) and gauge stimulus


Using this class:
-----------------

**To configure the slider:**

- Create the slider and set the background stimulus (:attr:`~trajtracker.stimuli.Slider.bgnd_stimulus`)
  and the gauge stimulus (:attr:`~trajtracker.stimuli.Slider.gauge_stimulus`)

- Choose the slider's :attr:`~trajtracker.stimuli.Slider.orientation` : vertical or horizontal

- Customize the slider scale by setting :attr:`~trajtracker.stimuli.Slider.min_value`
  and :attr:`~trajtracker.stimuli.Slider.max_value`

- (Optional) Choose the slider's :attr:`~trajtracker.stimuli.Slider.default_value` (the gauge will reset to this value
  whenever :func:`~trajtracker.stimuli.Slider.reset` is called)

- (Optional) Limit the area where finger touches will move the gauge (:func:`~trajtracker.stimuli.Slider.set_clickable_area`,
  :func:`~trajtracker.stimuli.Slider.set_drag_area`)

- (Optional) set :attr:`~trajtracker.stimuli.Slider.slidable_range` to define how far the gauge can move

- (Optional) set :attr:`~trajtracker.stimuli.Slider.max_moves` to limit the number of times the gauge can move.
  If this number is exceeded, the slider will become :attr:`~trajtracker.stimuli.Slider.locked`.

- Add :attr:`Slider.stimulus <trajtracker.stimuli.Slider.stimulus>` to a :class:`~trajtracker.stimuli.StimulusContainer`
  (or present() it directly)


**To use it (e.g., during a trial):**

- Set the slider :attr:`~trajtracker.stimuli.Slider.visible`

- Call :func:`~trajtracker.stimuli.Slider.reset` when the trial starts

- Call :func:`~trajtracker.stimuli.Slider.update` to inform the slider whether the mouse is clicked or not
  and about its position.

- Obtain the slider value via :attr:`~trajtracker.stimuli.Slider.current_value`

- Check how many times it was moved via :attr:`~trajtracker.stimuli.Slider.n_moves`


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.Slider
   :members:
   :inherited-members:
   :member-order: alphabetical
