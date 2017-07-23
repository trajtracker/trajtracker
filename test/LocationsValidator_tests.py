import unittest

import xml.etree.ElementTree as ET

import trajtracker
from trajtracker.utils import color_rgb_to_num
from trajtracker.validators import LocationsValidator

z = (0, 0, 0)
w = (255, 255, 255)

testimage = [
    [z, z, z, z, z],
    [z, w, w, w, w],
    [z, w, w, w, w],
    [z, w, w, w, w],
    [z, z, z, z, z],
]

class LocationsValidatorTests(unittest.TestCase):

    #------------------------------------------------------------
    def test_set_properties(self):
        val = LocationsValidator(testimage)
        val.default_valid = True
        val.valid_colors = w
        val.valid_colors = [w, z]
        val.valid_colors = (w, z)
        val.valid_colors = {w, z}
        val.invalid_colors = w
        val.invalid_colors = [w, z]
        val.invalid_colors = (w, z)
        val.invalid_colors = {w, z}


    #------------------------------------------------------------
    def test_set_bad_colors(self):
        val = LocationsValidator(testimage)

        try:
            val.valid_colors = 3
            self.fail()
        except:
            pass

        try:
            val.valid_colors = (1,2)
            self.fail()
        except:
            pass

        try:
            val.valid_colors = (0,0,256)
            self.fail()
        except:
            pass

        try:
            val.valid_colors = (0,-1,255)
            self.fail()
        except:
            pass


    #------------------------------------------------------------
    def test_set_bad_default(self):
        val = LocationsValidator(testimage)

        try:
            val.default_valid = None
            self.fail()
        except:
            pass

        try:
            val.default_valid = ""
            self.fail()
        except:
            pass


    #------------------------------------------------------------
    def test_validate_default_invalid(self):
        val = LocationsValidator(testimage)
        val.valid_colors = w

        self.assertIsNotNone(val.update_xyt((0, -2)))
        self.assertIsNotNone(val.update_xyt((0, 2)))
        self.assertIsNotNone(val.update_xyt((-2, 0)))
        self.assertIsNone(val.update_xyt((2, 0)))
        self.assertIsNotNone(val.update_xyt((10, 10)))  # out of image


    #------------------------------------------------------------
    def test_validate_default_valid(self):
        val = LocationsValidator(testimage, default_valid=True)
        val.invalid_colors = z

        self.assertIsNotNone(val.update_xyt((0, -2)))
        self.assertIsNotNone(val.update_xyt((0, 2)))
        self.assertIsNotNone(val.update_xyt((-2, 0)))
        self.assertIsNone(val.update_xyt((2, 0)))
        self.assertIsNone(val.update_xyt((10, 10))) # out of image

    #------------------------------------------------------------
    def test_disabled(self):
        val = LocationsValidator(testimage, enabled=False)
        val.valid_colors = w
        self.assertIsNone(val.update_xyt((0, -2)))

    #------------------------------------------------------------
    def test_validate_color(self):
        val = LocationsValidator(testimage)
        val.valid_colors = w

        e = val.update_xyt((0, -2))
        self.assertIsNotNone(e)
        self.assertEqual(e.arg(LocationsValidator.arg_color), color_rgb_to_num(z))


if __name__ == '__main__':
    unittest.main()
