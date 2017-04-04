import unittest

from trajtracker.validators import ValidationAxis
from trajtracker import BadFormatError

class validators_tests(unittest.TestCase):

    def test_parse_validation_axis(self):
        self.assertEqual(ValidationAxis.x, ValidationAxis.parse('x'))
        self.assertEqual(ValidationAxis.y, ValidationAxis.parse('y'))
        self.assertEqual(ValidationAxis.xy, ValidationAxis.parse('XY'))

    def test_parse_validation_axis_nochange(self):
        self.assertEqual(ValidationAxis.x, ValidationAxis.parse('x'))

    def test_parse_validation_axis_invalid(self):
        self.assertRaises(TypeError, lambda: ValidationAxis.parse(1))
        self.assertRaises(BadFormatError, lambda: ValidationAxis.parse('1'))


if __name__ == '__main__':
    unittest.main()
