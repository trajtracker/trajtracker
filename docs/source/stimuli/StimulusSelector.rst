.. TrajTracker : StimulusSelector.py

StimulusSelector class
======================

This object keeps several expyriment stimuli, and can define one of them as active.

You can then handle the active stimulus: present it, modify its position.

This class is useful when you have a stimulus that can change during a trial, and you want to change the
stimulus independently of presenting and moving it. For example, suppose a moving rectangle should repeatedly
changes its color between red and green according to some logic. You can:

- Define two rectangles with the same size, one red and one green (this is better than repeatedly
  changing the color of a single rectangle: replotting the stimulus on every frame would be time-consuming)

- Wrap the two rectangles as a single StimulusSelector object

- To move the rectangle, change :meth:`StimulusSelector.position <trajtracker.stimuli.StimulusSelector.position>`.

- To change the rectangle color, use :meth:`StimulusSelector.activate <trajtracker.stimuli.StimulusSelector.activate>`.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.StimulusSelector
   :members:
   :inherited-members:
   :member-order: bysource
