import unittest

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u

from trajtracker import BadFormatError


class _UtilsTests(unittest.TestCase):

    def test_parse_coords(self):
        self.assertEqual((1, 2), _u.parse_coord('(1,2)'))
        self.assertEqual((1, 2), _u.parse_coord('(1, 2)'))
        self.assertEqual((1, 2), _u.parse_coord('( 1,2)'))
        self.assertEqual((1, 2), _u.parse_coord('  ( 1 , 2 )  '))


    def test_parse_coords_bad_format(self):
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_coord('1,2)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_coord('(x,2)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_coord('(,2)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_coord('(2,)'))



    def test_parse_rgb(self):
        self.assertEqual((1, 2, 3), _u.parse_rgb('(1,2,3)'))
        self.assertEqual((1, 2, 3), _u.parse_rgb('(1, 2, 3)'))
        self.assertEqual((1, 2, 3), _u.parse_rgb('  ( 1 , 2 , 3 )  '))


    def test_parse_rgb_bad_format(self):
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_rgb('1,2,3)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_rgb('(x,2,2)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_rgb('(,2,2)'))
        self.assertRaises(trajtracker.ValueError, lambda: _u.parse_rgb('(2,,3)'))



if __name__ == '__main__':
    unittest.main()
