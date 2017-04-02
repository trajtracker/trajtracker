import unittest

from trajtracker.validators import _parse_validation_axis, ValidationAxis
from trajtracker import BadFormatError

class validators_tests(unittest.TestCase):

    def test_parse_validation_axis(self):
        self.assertEqual(ValidationAxis.x, _parse_validation_axis('x'))
        self.assertEqual(ValidationAxis.y, _parse_validation_axis('y'))
        self.assertEqual(ValidationAxis.xy, _parse_validation_axis('XY'))

    def test_parse_validation_axis_nochange(self):
        self.assertEqual(ValidationAxis.x, _parse_validation_axis('x'))

    def test_parse_validation_axis_invalid(self):
        self.assertRaises(TypeError, lambda: _parse_validation_axis(1))
        self.assertRaises(BadFormatError, lambda: _parse_validation_axis('1'))


if __name__ == '__main__':
    unittest.main()
