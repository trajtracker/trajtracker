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
   :inherited-members:
   :member-order: alphabetical


Circle
------

.. autoclass:: trajtracker.misc.nvshapes.Circle
   :members:
   :inherited-members:
   :member-order: alphabetical


Sector
------

.. autoclass:: trajtracker.misc.nvshapes.Sector
   :members:
   :inherited-members:
   :member-order: alphabetical

