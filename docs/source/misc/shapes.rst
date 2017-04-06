.. TrajTracker : shapes.py

Non-visual shapes
=================

TrajTracker provides a set of classes that define geometric shapes. These shapes are not visual:
we can know their geometric properties and even assign them a location on screen, but they cannot be
displayed.

These shapes can be used by trajtracker classes that require defining regions on screen - e.g.,
:class:`~trajtracker.movement.StartPoint`.


Rectangle
---------

.. autoclass:: trajtracker.misc.nvshapes.Rectangle
   :members:
   :member-order: bysource


Circle
------

.. autoclass:: trajtracker.misc.nvshapes.Circle
   :members:
   :member-order: bysource


Sector
------

.. autoclass:: trajtracker.misc.nvshapes.Sector
   :members:
   :member-order: bysource

