import unittest

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u

from expyriment.misc.geometry import XYPoint


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

    #------------------------------------------------------------------------------
    def test_is_coord_int(self):
        self.assertEqual(True, _u.is_coord((5, 4)))
        self.assertEqual(True, _u.is_coord([5, 4]))
        self.assertEqual(True, _u.is_coord(XYPoint(5, 4)))

    def test_is_coord_float(self):
        self.assertEqual(True, _u.is_coord((5.0, 4.0)))
        self.assertEqual(True, _u.is_coord([5.0, 4.0]))
        self.assertEqual(True, _u.is_coord(XYPoint(5.0, 4.0)))

    def test_is_coord_float_not_allowed(self):
        self.assertEqual(False, _u.is_coord((5.1, 4.1)))
        self.assertEqual(False, _u.is_coord([5.1, 4.1]))
        self.assertEqual(True, _u.is_coord(XYPoint(5.1, 4.1)))

    def test_is_coord_float_allowed(self):
        self.assertEqual(True, _u.is_coord((5.1, 4.1), allow_float=True))
        self.assertEqual(True, _u.is_coord([5.1, 4.1], allow_float=True))
        self.assertEqual(True, _u.is_coord(XYPoint(5.1, 4.1), allow_float=True))



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
