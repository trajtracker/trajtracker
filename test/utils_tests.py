import unittest

import numpy as np

import trajtracker.utils as u


class UtilsTests(unittest.TestCase):

    def test_rgb(self):
        self.assertTrue(u.is_rgb([255, 0, 255]))
        self.assertTrue(np.array(u.is_rgb([255, 0, 255])))
        self.assertTrue(u.is_rgb((0.0, 1.5, 255.0)))

        self.assertFalse(u.is_rgb(None))
        self.assertFalse(u.is_rgb(1000))
        self.assertFalse(u.is_rgb([255, 0, 255, 0]))
        self.assertFalse(u.is_rgb([255, 0]))
        self.assertFalse(u.is_rgb([]))
        self.assertFalse(u.is_rgb(['x', 0, 255]))
        self.assertFalse(u.is_rgb([255, 0, 'x']))
        self.assertFalse(u.is_rgb([255.1, 0, 255]))
        self.assertFalse(u.is_rgb([255, -0.5, 255]))


if __name__ == '__main__':
    unittest.main()
