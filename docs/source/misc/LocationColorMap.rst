.. TrajTracker : LocationColorMap.py

LocationColorMap class
======================

Translate the finger location into a code, according to a BMP image. The image is not displayed,
but the class can tell you the color of a certain image pixel had it been displayed on screen.

This is a very flexible method for defining several different regions on the screen.


Using this class
----------------

- Create an image file. The file format should be a bitmap (image.bmp) in 24-bit format
  (which means that each pixel is specified as an RGB combination).

  The file doesn't have to be of the same size as the screen.

- Create the LocationColorMap object

- Get the colors of pixels using :func:`~trajtracker.misc.LocationColorMap.get_color_at`

- In this simplest configuration, :func:`~trajtracker.misc.LocationColorMap.get_color_at` will
  tell you the RGB color of the pixel indicated.

  You can also define :attr:`~trajtracker.misc.LocationColorMap.colormap` to map each RGB color to any value
  (e.g., to make :func:`~trajtracker.misc.LocationColorMap.get_color_at` will return meaningful values).

  When using a color map, make sure to set :attr:`~trajtracker.misc.LocationColorMap.use_mapping` to True.




Methods and properties:
-----------------------

.. autoclass:: trajtracker.misc.LocationColorMap
   :members:
   :inherited-members:
   :member-order: alphabetical


