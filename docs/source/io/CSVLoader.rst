.. TrajTracker : CSVLoader.py

CSVLoader class
===============

Load a CSV file. This class can:

- Define some fields (columns) as mandatory;
- Define, per field, how to transform its value from string to something else
- Handle case sensitive/insensitive field names


You can define CSV fields using :func:`~trajtracker.io.CSVLoader.add_field` , in which case you can also
specify their type and whether they're optional or not.

Excessive fields are allowed too, they will be loaded as strings.



Methods and properties:
-----------------------

.. autoclass:: trajtracker.io.CSVLoader
   :members:
   :inherited-members:
   :member-order: bysource


