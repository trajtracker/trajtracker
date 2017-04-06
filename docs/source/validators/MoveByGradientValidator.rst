.. TrajTracker : MoveByGradientValidator.py

MoveByGradientValidator class
=============================

This validator gets an image, and allows mouse to move only according to it -
from a light color to a darker color (or vice versa).

**Note:** The validator expects a BMP image in 24-bit format (i.e., RGB format: for each pixel, the image specifies
the values of the red, green, and blue components, each on a 0-255 scale).

RGB colors are represented in Python as (red, green, blue) tuples. The tuple can be converted to a single numeric value
by calculating

.. code-block:: python
   numeric_value = red * 256 * 256 + green * 256 + blue

This is the value used by the validator to determine the gradient.


Features
--------

* The validator can require movement to comply with ascending or descending RGB directions - see
  :attr:`~trajtracker.validators.MoveByGradientValidator.rgb_should_ascend`. Yet even when asking
  for movement in certain direction, you may allow for minor movement in the opposite direction - see
  :attr:`~trajtracker.validators.MoveByGradientValidator.max_valid_back_movement`.

* You can tell the validator to use only one of the colors (red/green/blue) to determine the validated gradient.
  This means that the validator will consider only pixels that are purely on this scale (e.g., if you choose blue,
  pixels that have non-0 red or green components will be ignored).
  See :attr:`~trajtracker.validators.MoveByGradientValidator.single_color` for more details.

* When the movement reaches the highest RGB value (65535 when all colors are used; 255 when a single color is used)
  and then goes back to a 0-pixel, you may still want to consider this as an ascedning-gradient movement).
  This would be typically the case when your gradient creates a cyclic path on screen (see the "ImageValidators"
  sample experiment - have a look at gradient.bmp, which serves for validation in that sample).
  For more details, see :attr:`~trajtracker.validators.MoveByGradientValidator.cyclic` and the "under the hood"
  section at the bottom of this page.


Methods and properties:
-----------------------

.. autoclass:: trajtracker.validators.MoveByGradientValidator
   :members:
   :inherited-members:
   :member-order: bysource



Under the hood:
---------------

* **MoveByGradientValidator.max_irrelevant_color_value** (default: 10): define the threshold for a the irrelevant colors when using
  :attr:`~trajtracker.validators.MoveByGradientValidator.single_color`. If you set *single_color=blue*, the validator
  will consider as the relevant (blue) pixels all pixels whose red and green components are not higher than
  *max_irrelevant_color_value*.

* **MoveByGradientValidator.cyclic_ratio** (default: 5): This definition is relevant when using
  :attr:`~trajtracker.validators.MoveByGradientValidator.cyclic` = *True*. The idea is as follows:
  Each color is a number between 0 and 65,535. Setting "cyclic" means that if the finger/mouse moves from a pixel
  with value=65,535 to value=0, we want it to be considered as an ascending-gradient movement. But what about
  moving from 65,535 to 5,000? Did the value ascend by 5,000 (the "cyclic distance") or descend by 60,535
  (the "non-cyclic distance")? The decision is made as follows: if the cyclic distance is shorter than the
  non-cyclic distance by more than this ratio (cyclic_ratio), we assume that the movement was in the cyclic direction.
  in the above example (from 65,535 to 5,000), the cyclic distance is 5000, the non-cyclic distance is 60,535,
  and indeed 60535 / 5000 > 5, so this movement would be interpreted as cyclic.

  If you use :attr:`~trajtracker.validators.MoveByGradientValidator.single_color`, the same logic applies but
  the scale is 0-255.
