import unittest

import numpy as np

from trajtracker.utils import get_angle


class MovementTestCase(unittest.TestCase):

    def assertAngleIs(self, expected, actual):
        actual *= 360 / np.pi / 2
        if actual > 360:
            actual -= 360
        if actual < 0:
            actual += 360

        self.assertTrue(np.abs(expected-actual) < .001)


    def test_get_angle(self):
        self.assertAngleIs(0, get_angle((0,0), (0,1)))
        self.assertAngleIs(45, get_angle((0,0), (1,1)))
        self.assertAngleIs(90, get_angle((0,0), (1,0)))
        self.assertAngleIs(135, get_angle((0,0), (1,-1)))
        self.assertAngleIs(180, get_angle((0,0), (0,-1)))
        self.assertAngleIs(225, get_angle((0,0), (-1,-1)))
        self.assertAngleIs(270, get_angle((0,0), (-1,0)))
        self.assertAngleIs(315, get_angle((0,0), (-1,1)))

        self.assertEqual(0, get_angle((0, 0), (0, 1)))



if __name__ == '__main__':
    unittest.main()
