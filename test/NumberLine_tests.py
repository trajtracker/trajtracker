import unittest

import trajtracker
from trajtracker.stimuli import NumberLine


class NumberLineTestCase(unittest.TestCase):

    #=======================================================================
    #          Configure
    #=======================================================================

    #-- Create a NumberLine object, test default values
    def test_default_propertie(self):
        nl = NumberLine((10,20), 1000, 100)
        self.assertEqual(nl.position[0], 10)
        self.assertEqual(nl.position[1], 20)
        self.assertEqual(nl.min_value, 0)
        self.assertEqual(nl.max_value, 100)
        self.assertEqual(nl.line_length, 1000)
        self.assertEqual(nl.orientation, NumberLine.Orientation.Horizontal)


    #-- Validate() should fail when min>max
    def test_invalid_min_max(self):
        nl = NumberLine((10,20), 1000, min_value=100, max_value=100)
        self.assertRaises(trajtracker.ValueError, lambda: nl.validate())

    #-- Validate() should fail when some data is missing
    def test_missing_labels(self):
        nl = NumberLine((10,20), 1000, 100)
        nl.labels_visible = True
        self.assertRaises(trajtracker.ValueError, lambda: nl.validate())

        nl.show_labels(box_size=(10,10), font_name='Arial', font_size=3, font_colour=(255,0,0))
        nl.validate()


    #=======================================================================
    #          Detect touches
    #=======================================================================

    #-----------------------------------------------------------------
    #-- Touch mode = undirectioned, horizontal line
    def test_touch_line_undirectioned_horizontal(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = False
        nl.touch_distance = 10

        #-- touch twice from the same direction
        nl.reset()
        nl.update_xyt((0, 11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, 9))
        self.assertTrue(nl.touched)

        #-- touch twice from two different directions
        nl.reset()
        nl.update_xyt((0, 11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, -9))
        self.assertTrue(nl.touched)


    #-----------------------------------------------------------------
    #-- Touch mode = undirectioned, vertical line
    def test_touch_line_undirectioned_vertical(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Vertical)
        nl.touch_directioned = False
        nl.touch_distance = 10

        #-- touch twice from the same direction
        nl.reset()
        nl.update_xyt((11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((9, 0))
        self.assertTrue(nl.touched)

        #-- touch twice from two different directions
        nl.reset()
        nl.update_xyt((11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((-9, 0))
        self.assertTrue(nl.touched)


    #-----------------------------------------------------------------
    #-- Touch mode = directioned, horizontal line
    def test_touch_line_directioned_horizontal(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = True
        nl.touch_distance = 10

        #-- Get closer to the line
        nl.reset()
        nl.update_xyt((0, 11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, 9))
        self.assertTrue(nl.touched)

        #-- Cross the line
        nl.reset()
        nl.update_xyt((0, 11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, -100))
        self.assertTrue(nl.touched)

        #--- Now, from the other direction

        #-- Get closer to the line
        nl.reset()
        nl.update_xyt((0, -11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, -9))
        self.assertTrue(nl.touched)

        #-- Cross the line
        nl.reset()
        nl.update_xyt((0, -11))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, 100))
        self.assertTrue(nl.touched)


    #-----------------------------------------------------------------
    #-- Touch mode = directioned, vertical line
    def test_touch_line_directioned_vertical(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Vertical)
        nl.touch_directioned = True
        nl.touch_distance = 10

        #-- Get closer to the line
        nl.reset()
        nl.update_xyt((11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((9, 0))
        self.assertTrue(nl.touched)

        #-- Cross the line
        nl.reset()
        nl.update_xyt((11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((-100, 0))
        self.assertTrue(nl.touched)

        #--- Now, from the other direction

        #-- Get closer to the line
        nl.reset()
        nl.update_xyt((-11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((-9, 0))
        self.assertTrue(nl.touched)

        #-- Cross the line
        nl.reset()
        nl.update_xyt((-11, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((100, 0))
        self.assertTrue(nl.touched)


    #-----------------------------------------------------------------
    #-- Touch mode = directioned, negative distance
    def test_touch_line_directioned_negative_distance(self):
        nl = NumberLine((0,0), 100, 100, orientation=NumberLine.Orientation.Horizontal)
        nl.touch_directioned = True
        nl.touch_distance = -10

        #-- Get closer to the line
        nl.reset()
        nl.update_xyt((0, 10))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, 1))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, 0))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, -5))
        self.assertFalse(nl.touched)
        nl.update_xyt((0, -11))
        self.assertTrue(nl.touched)


    #-----------------------------------------------------------------
    def test_response_coord(self):
        nl = NumberLine((0,0), 100, 40, orientation=NumberLine.Orientation.Horizontal)

        self.assertIsNone(nl.response_coord)
        self.assertIsNone(nl.response_value)

        nl.reset()
        nl.update_xyt((0, -1))
        nl.update_xyt((0, 1))

        self.assertEqual(0, nl.response_coord)
        self.assertEqual(20, nl.response_value)

        nl.reset()
        self.assertIsNone(nl.response_coord)
        self.assertIsNone(nl.response_value)

        nl.update_xyt((25, -1))
        nl.update_xyt((25, 1))

        self.assertEqual(25, nl.response_coord)
        self.assertEqual(30, nl.response_value)

    #-----------------------------------------------------------------
    def test_value_to_coord(self):
        nl = NumberLine((10, 50), 100, 50, orientation=NumberLine.Orientation.Horizontal)
        self.assertEqual(-20, nl.value_to_coord(10))
        self.assertEqual(-42, nl.value_to_coord(-1))

        nl = NumberLine((50, 10), 100, 50, orientation=NumberLine.Orientation.Vertical)
        self.assertEqual(-20, nl.value_to_coord(10))
        self.assertEqual(-42, nl.value_to_coord(-1))

    #-----------------------------------------------------------------
    def test_value_to_coords(self):
        nl = NumberLine((10, 50), 100, 50, orientation=NumberLine.Orientation.Horizontal)
        self.assertEqual((-20, 50), nl.value_to_coords(10))
        self.assertEqual((-42, 50), nl.value_to_coords(-1))

        nl = NumberLine((50, 10), 100, 50, orientation=NumberLine.Orientation.Vertical)
        self.assertEqual((50, -20), nl.value_to_coords(10))
        self.assertEqual((50, -42), nl.value_to_coords(-1))


    #-----------------------------------------------------------------
    # noinspection PyTypeChecker
    def test_coord_to_value(self):
        nl = NumberLine((10, 50), 100, 50, orientation=NumberLine.Orientation.Horizontal)
        self.assertTrue(nl.coord_to_value(-20) - 10 < .0000001)
        self.assertTrue(nl.coord_to_value(-42) - (-1) < .000001)

        nl = NumberLine((50, 10), 100, 50, orientation=NumberLine.Orientation.Vertical)
        self.assertTrue(nl.coord_to_value(-20) - 10 < .0000001)
        self.assertTrue(nl.coord_to_value(-42) - (-1) < .000001)



if __name__ == '__main__':
    unittest.main()
