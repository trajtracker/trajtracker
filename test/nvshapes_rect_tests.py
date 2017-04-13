from __future__ import division

import unittest

from numpy import sin, cos, abs, pi
from trajtracker.misc import nvshapes


rad = lambda deg: deg / 180 * pi


class NVRectangleTests(unittest.TestCase):

    #-----------------------------------------------------
    def test_overlap_pos_0(self):

        r = nvshapes.Rectangle(size=(10, 20))
        self.assertTrue(r.overlapping_with_position((0, 0)))
        self.assertTrue(r.overlapping_with_position((5, 10)))
        self.assertTrue(r.overlapping_with_position((-5, 10)))
        self.assertTrue(r.overlapping_with_position((5, -10)))
        self.assertTrue(r.overlapping_with_position((-5, -10)))

        self.assertFalse(r.overlapping_with_position((6, 10)))
        self.assertFalse(r.overlapping_with_position((5, 11)))
        self.assertFalse(r.overlapping_with_position((-6, 10)))
        self.assertFalse(r.overlapping_with_position((-5, 11)))
        self.assertFalse(r.overlapping_with_position((6, -10)))
        self.assertFalse(r.overlapping_with_position((5, -11)))
        self.assertFalse(r.overlapping_with_position((-6, -10)))
        self.assertFalse(r.overlapping_with_position((-5, -11)))


    #-----------------------------------------------------
    def test_overlap_pos_non_0(self):
        r = nvshapes.Rectangle(size=(10, 20), position=(50, 100))
        self.assertTrue(r.overlapping_with_position((50, 100)))
        self.assertTrue(r.overlapping_with_position((55, 110)))
        self.assertTrue(r.overlapping_with_position((45, 110)))
        self.assertTrue(r.overlapping_with_position((55, 90)))
        self.assertTrue(r.overlapping_with_position((45, 90)))

        self.assertFalse(r.overlapping_with_position((56, 110)))
        self.assertFalse(r.overlapping_with_position((55, 111)))
        self.assertFalse(r.overlapping_with_position((44, 110)))
        self.assertFalse(r.overlapping_with_position((45, 111)))
        self.assertFalse(r.overlapping_with_position((44, 90)))
        self.assertFalse(r.overlapping_with_position((45, 89)))
        self.assertFalse(r.overlapping_with_position((44, 90)))
        self.assertFalse(r.overlapping_with_position((45, 89)))


    #-----------------------------------------------------
    def test_overlap_rotation(self):
        r = nvshapes.Rectangle(size=(10, 20), rotation=30)

        # top-mid point, rotated by 30 degrees
        x = 10 * abs(sin(rad(30)))
        y = 10 * abs(cos(rad(30)))

        self.assertTrue(r.overlapping_with_position((x, y)))
        self.assertTrue(r.overlapping_with_position((x-.01, y-.01)))
        self.assertFalse(r.overlapping_with_position((x, y+.01)))
        self.assertFalse(r.overlapping_with_position((x+.01, y)))

        # bottom-mid point, rotated by 30 degrees
        x = -10 * abs(sin(rad(30)))
        y = -10 * abs(cos(rad(30)))

        self.assertTrue(r.overlapping_with_position((x, y)))
        self.assertTrue(r.overlapping_with_position((x+.01, y+.01)))
        self.assertFalse(r.overlapping_with_position((x, y-.01)))
        self.assertFalse(r.overlapping_with_position((x-.01, y)))

        # right-mid point, rotated by 30 degrees
        x = 5 * abs(cos(rad(30)))
        y = - 5 * abs(sin(rad(30)))

        self.assertTrue(r.overlapping_with_position((x, y)))
        self.assertTrue(r.overlapping_with_position((x-1, y+1)))
        self.assertFalse(r.overlapping_with_position((x, y-.01)))
        self.assertFalse(r.overlapping_with_position((x+.01, y)))

        # left-mid point, rotated by 30 degrees
        x = - 5 * abs(cos(rad(30)))
        y = 5 * abs(sin(rad(30)))

        self.assertTrue(r.overlapping_with_position((x, y)))
        self.assertTrue(r.overlapping_with_position((x+1, y-1)))
        self.assertFalse(r.overlapping_with_position((x, y+.01)))
        self.assertFalse(r.overlapping_with_position((x-.01, y)))


if __name__ == '__main__':
    unittest.main()
