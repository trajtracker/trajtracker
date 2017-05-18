.. TrajTracker : StimulusContainer.py

StimulusContainer class
=======================

Maintain several stimuli, and can present them all with a single command.
You can also define some of the stimuli as temporarily invisible by setting their "visible" property.


Using this class
----------------

- Create the container
- Add visual objects to the container using :func:`~trajtracker.stimuli.StimulusContainer.add`
- Once an object is added to the container, it will have a "visible" property, which you can set at any time.
- Present the container using :func:`~trajtracker.stimuli.StimulusContainer.present` . All objects with
  *visible=True* will be presented.
- Objects added to the container later will appear on top of earlier-added objects.
- You can access objects from the container by writing *container[obj_id]*, where *obj_id* is the ID
  you provided to :func:`~trajtracker.stimuli.StimulusContainer.add`.
- You can also tell the StimulusContainer to call a function when
  :func:`~trajtracker.stimuli.StimulusContainer.present` is called - to do this, use
  :func:`~trajtracker.stimuli.StimulusContainer.register_callback`


Methods and properties:
-----------------------

.. autoclass:: trajtracker.stimuli.StimulusContainer
   :members:
   :inherited-members:
   :member-order: bysource


