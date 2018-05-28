import unittest

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u

from expyriment.misc.geometry import XYPoint


from trajtracker import BadFormatError


class _UtilsTests(unittest.TestCase):

    #------------------------------------------------------------------------------
    def test_parse_coords(self):
        self.assertEqual((1, 2), _u.parse_coord('(1,2)'))
        self.assertEqual((1, 2), _u.parse_coord('(1, 2)'))
        self.assertEqual((1, 2), _u.parse_coord('( 1,2)'))
        self.assertEqual((1, 2), _u.parse_coord('  ( 1 , 2 )  '))


    def test_parse_coords_bad_format(self):
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_coord('1,2)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_coord('(x,2)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_coord('(,2)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_coord('(2,)'))

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

    def test_is_coord_invalid_type(self):
        self.assertEqual(False, _u.is_coord([4]))
        self.assertEqual(False, _u.is_coord(['a', 'b']))
        self.assertEqual(False, _u.is_coord('a'))


    #------------------------------------------------------------------------------
    def test_validate_attr_type_is_coord(self):
        _u.validate_attr_is_coord(object(), 'test', [5, 3])
        self.assertEqual((5, 3), _u.validate_attr_is_coord(object(), 'test', [5.0, 3.0]))
        self.assertEqual([5.1, 3.1], _u.validate_attr_is_coord(object(), 'test', [5.1, 3.1], allow_float=True))

    def test_validate_attr_type_is_coord_invalid_type(self):
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_coord('object', 'test_attr', 'xxxxxxx'))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_coord('object', 'test_attr', [5]))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_coord('object', 'test_attr', ['a', 'b']))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_coord('object', 'test_attr', [5.1, 0]))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_coord('object', 'test_attr', [0, 5.1]))

    def test_validate_func_arg_type_is_coord_invalid_type(self):
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_coord('object', 'func', 'test_attr', 'xxxxxxx'))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_coord('object', 'func', 'test_attr', [5]))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_coord('object', 'func', 'test_attr', ['a', 'b']))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_coord('object', 'func', 'test_attr', [5.1, 0]))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_coord('object', 'func', 'test_attr', [0, 5.1]))


    #------------------------------------------------------------------------------
    def test_is_collection(self):
        self.assertEqual(True, _u.is_collection([]))
        self.assertEqual(True, _u.is_collection(tuple()))
        self.assertEqual(True, _u.is_collection(set()))
        self.assertEqual(False, _u.is_collection(5))
        self.assertEqual(False, _u.is_collection(None))

    def test_validate_attr_is_collection(self):
        _u.validate_attr_is_collection(object(), 'test', [])
        _u.validate_attr_is_collection(object(), 'test', [1, 2])
        _u.validate_attr_is_collection(object(), 'test', (4, 5))
        _u.validate_attr_is_collection(object(), 'test', {4, 5}, allow_set=True)
        _u.validate_attr_is_collection(object(), 'test', None, none_allowed=True)

    def test_validate_attr_is_not_collection(self):
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_collection(object(), 'test', 'x'))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_collection(object(), 'test', None))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_collection(object(), 'test', {5}))

    def test_validate_attr_collection_min_length(self):
        _u.validate_attr_is_collection(object(), 'test', [2, 3], min_length=2)
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_collection(object(), 'test', [2, 3], min_length=3))

    def test_validate_attr_collection_max_length(self):
        _u.validate_attr_is_collection(object(), 'test', [2, 3], max_length=2)
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_attr_is_collection(object(), 'test', [2, 3], max_length=1))


    def test_validate_func_arg_is_collection(self):
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', [])
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', [1, 2])
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', (4, 5))
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', {4, 5}, allow_set=True)
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', None, none_allowed=True)

    def test_validate_func_arg_is_not_collection(self):
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_collection(object(), 'test', 'arg', 'x'))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_collection(object(), 'test', 'arg', None))
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_collection(object(), 'test', 'arg', {5}))

    def test_validate_func_arg_collection_min_length(self):
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', [2, 3], min_length=2)
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_collection(object(), 'test', 'arg', [2, 3], min_length=3))

    def test_validate_func_arg_collection_max_length(self):
        _u.validate_func_arg_is_collection(object(), 'test', 'arg', [2, 3], max_length=2)
        self.assertRaises(ttrk.TypeError, lambda: _u.validate_func_arg_is_collection(object(), 'test', 'arg', [2, 3], max_length=1))


    #------------------------------------------------------------------------------
    def test_parse_rgb(self):
        self.assertEqual((1, 2, 3), _u.parse_rgb('(1,2,3)'))
        self.assertEqual((1, 2, 3), _u.parse_rgb('(1, 2, 3)'))
        self.assertEqual((1, 2, 3), _u.parse_rgb('  ( 1 , 2 , 3 )  '))


    def test_parse_rgb_bad_format(self):
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_rgb('1,2,3)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_rgb('(x,2,2)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_rgb('(,2,2)'))
        self.assertRaises(ttrk.ValueError, lambda: _u.parse_rgb('(2,,3)'))

    #------------------------------------------------------------------------------
    def test_is_whole_number(self):
        self.assertEqual(True, _u.is_whole_number(1))
        self.assertEqual(True, _u.is_whole_number(-2))
        self.assertEqual(True, _u.is_whole_number(1.0))
        self.assertEqual(True, _u.is_whole_number(-2.0))
        self.assertEqual(False, _u.is_whole_number(-2.5))
        self.assertEqual(False, _u.is_whole_number(2.3))
        self.assertEqual(False, _u.is_whole_number('r'))
        self.assertEqual(False, _u.is_whole_number(None))

if __name__ == '__main__':
    unittest.main()
