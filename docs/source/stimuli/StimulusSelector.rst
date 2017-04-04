.. TrajTracker : StimulusSelector.py

StimulusSelector class
======================

This object keeps several expyriment stimuli, and can define one of them as active.

You can then handle the active stimulus: present it, modify its position.

This class is useful when you have a stimulus that can change during a trial, and you want to change the
stimulus independently of presenting and moving it. For example, support you want to move a rectangle around the
screen, and make its color flicker between red and green. You can:

- Define two rectangles with the same size, one red and one green (this is better than repeatedly
changing the color of a single rectangle, because you don't want to redraw the stimulus on every frame)
- Wrap the two rectangles as a StimulusSelector object
- Use a :class:`~trajtracker.movement.StimulusAnimator` to move the stimulus around screen. The animator
will not control the rectangles directly, but the StimulusSelector
- Repeatedly call :func:`~trajtracker.movement.StimulusAnimator.update` to move the rectangle, and
:func:`~trajtracker.stimuli.StimulusSelector.activate` to change its color.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.StimulusSelector
   :members:
   :member-order: bysource


