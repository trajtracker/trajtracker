import unittest

import trajtracker
from trajtracker.movement import RectStartPoint
from trajtracker.misc import nvshapes


class RectStartPointDbg(RectStartPoint):
    def _create_start_area(self):
        return nvshapes.Rectangle(size=self._size, position=self._position, rotation=self._rotation)




class RectStartPointTests(unittest.TestCase):

    #============================================================================
    # Configuration
    #============================================================================

    #------------------------------------------------------------
    def test_set_size(self):
        RectStartPointDbg(size=(10, 10))
        RectStartPointDbg(size=None)

        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(size=""))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(size=(1, 2, 3)))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(size=("", 2)))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(size=(1, "")))


    #------------------------------------------------------------
    def test_set_position(self):
        RectStartPointDbg(position=(10, 10))
        RectStartPointDbg(position=None)

        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(position=""))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(position=(1, 2, 3)))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(position=("", 2)))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(position=(1, "")))


    #------------------------------------------------------------
    def test_set_rotation(self):
        RectStartPointDbg(rotation=10)
        RectStartPointDbg(rotation=-900)

        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(rotation=""))
        self.assertRaises(trajtracker.TypeError, lambda: RectStartPointDbg(rotation=None))


    #============================================================================
    # Check areas
    #============================================================================

    #------------------------------------------------------------
    def test_start_area(self):

        sp = RectStartPointDbg(size=(20, 40))
        sp.preload()
        start_area = sp._start_point._start_area

        self.assertEquals(20, start_area.size[0])
        self.assertEquals(40, start_area.size[1])

        self.assertTrue(start_area.overlapping_with_position((10, 20)))
        self.assertTrue(start_area.overlapping_with_position((10, -20)))
        self.assertTrue(start_area.overlapping_with_position((-10, 20)))
        self.assertTrue(start_area.overlapping_with_position((-10, -20)))

        self.assertFalse(start_area.overlapping_with_position((11, 20)))
        self.assertFalse(start_area.overlapping_with_position((10, 21)))
        self.assertFalse(start_area.overlapping_with_position((11, -20)))
        self.assertFalse(start_area.overlapping_with_position((10, -21)))
        self.assertFalse(start_area.overlapping_with_position((-11, 20)))
        self.assertFalse(start_area.overlapping_with_position((-10, 21)))
        self.assertFalse(start_area.overlapping_with_position((-11, -20)))
        self.assertFalse(start_area.overlapping_with_position((-10, -21)))


if __name__ == '__main__':
    unittest.main()
