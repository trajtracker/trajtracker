import unittest

import trajtracker
from trajtracker.misc import LocationColorMap

# Remember this is upside down.
testimage = [
    [0, 2, 0, 17, 15, 15, 0],
    [0, 2, 0, 15, 15, 15, 0],
    [0, 0, 0, 30, 0, 0, 0],
    [0, 5, 0, 20, 20, 0, 0],
    [0, 0, 0, 10, 10, 10, 0],
]

testimage =  [[(0, 0, cell) for cell in row] for row in testimage]
all_colors = {0, 2, 5, 10, 15, 17, 20, 30}



class LocationColorMapTests(unittest.TestCase):


    #=====================================================================================
    #         Test class configuration and properties
    #=====================================================================================

    #-------------------------------------------------------------------------
    def test_get_default_props(self):
        lcm = LocationColorMap(testimage)
        self.assertEqual(frozenset([(0, 0, c) for c in all_colors]), lcm.available_colors)
        self.assertIsNone(lcm.colormap)

    #-------------------------------------------------------------------------
    def test_colormap_good(self):
        lcm = LocationColorMap(testimage)
        lcm.colormap = self.get_good_colormap()


    def get_good_colormap(self):
        codes = {}
        i = 0
        for c in all_colors:
            codes[(0, 0, c)] = i
            i += 1
        return codes

    #-------------------------------------------------------------------------
    def test_colormap_missing_colors(self):
        lcm = LocationColorMap(testimage)
        codes = {}
        i = 0
        for c in {0, 2, 5, 10}:
            codes[(0, 0, c)] = i
            i += 1

        try:
            lcm.colormap = codes
            self.fail("Succeeded setting an invalid value")
        except trajtracker.ValueError:
            pass

    #-------------------------------------------------------------------------
    def test_colormap_default(self):
        lcm = LocationColorMap(testimage)
        lcm.colormap = "default"
        print("Default colormap:")
        print(lcm.colormap)
        self.assertEqual(lcm.colormap[(0, 0, 0)], 0)
        self.assertEqual(lcm.colormap[(0, 0, 2)], 1)
        self.assertEqual(lcm.colormap[(0, 0, 30)], len(all_colors)-1)

    #-------------------------------------------------------------------------
    def test_colormap_rgb(self):
        lcm = LocationColorMap([[(0,0,255), (0,255,0), (255,0,0)]])
        lcm.colormap = "RGB"
        print("RGB colormap:")
        print(lcm.colormap)
        self.assertEqual(lcm.colormap[(0,0,255)], 255)
        self.assertEqual(lcm.colormap[(0,255,0)], 255*256)
        self.assertEqual(lcm.colormap[(255,0,0)], 255*256*256)

    #-------------------------------------------------------------------------
    def test_use_mapping_invalid(self):
        lcm = LocationColorMap(testimage)
        lcm.use_mapping = True
        lcm.use_mapping = False

        try:
            lcm.use_mapping = ""
            self.fail("Succeeded setting an invalid value for LocationColorMap.use_mapping")
        except trajtracker.TypeError:
            pass

        try:
            lcm.use_mapping = None
            self.fail("Succeeded setting an invalid value for LocationColorMap.use_mapping")
        except trajtracker.TypeError:
            pass



    #=====================================================================================
    #         Test the get_color_at() function
    #=====================================================================================

    #-------------------------------------------------------------------------
    def test_get_raw_colors(self):
        lcm = LocationColorMap(testimage)
        self.assertEqual(lcm.get_color_at(-3, -2), (0, 0, 0))
        self.assertEqual(lcm.get_color_at(0, 0), (0, 0, 30))
        self.assertEqual(lcm.get_color_at(2, 1), (0, 0, 15))

        self.assertIsNone(lcm.get_color_at(-4, 0))
        self.assertIsNone(lcm.get_color_at(4, 0))
        self.assertIsNone(lcm.get_color_at(0, -3))
        self.assertIsNone(lcm.get_color_at(0, 3))

    #-------------------------------------------------------------------------
    def test_get_with_coord(self):
        lcm = LocationColorMap(testimage, position=(3,2))
        self.assertEqual(lcm.get_color_at(0, 0), (0, 0, 0))
        self.assertEqual(lcm.get_color_at(3, 2), (0, 0, 30))
        self.assertEqual(lcm.get_color_at(3, 4), (0, 0, 17))

        self.assertIsNone(lcm.get_color_at(7, 0))
        self.assertIsNone(lcm.get_color_at(-1, 0))
        self.assertIsNone(lcm.get_color_at(0, -1))
        self.assertIsNone(lcm.get_color_at(0, 5))

    #-------------------------------------------------------------------------
    def test_get_even_size(self):
        img1 = [r[:-1] for r in testimage[1:]]  # remove last row and column

        lcm = LocationColorMap(img1)
        self.assertEqual(lcm.get_color_at(-1, 0), (0, 0, 5))

    #-------------------------------------------------------------------------
    def test_get_mapped_colors(self):
        lcm = LocationColorMap(testimage)
        codes = dict(zip([(0, 0, c) for c in all_colors], all_colors))
        lcm.colormap = codes
        self.assertEqual(lcm.get_color_at(-3, -2, use_mapping=True), 0)
        lcm.use_mapping = True
        self.assertEqual(lcm.get_color_at(0, 0), 30)
        self.assertEqual(lcm.get_color_at(2, 1), 15)

        self.assertIsNone(lcm.get_color_at(4, 0))
        self.assertIsNone(lcm.get_color_at(4, 0, use_mapping=True))


    #-------------------------------------------------------------------------
    def test_invalid_get_color_at_args(self):
        lcm = LocationColorMap(testimage)
        self.assertRaises(trajtracker.TypeError, lambda: lcm.get_color_at("", 0))
        self.assertRaises(trajtracker.TypeError, lambda: lcm.get_color_at(0.5, 0))
        self.assertRaises(trajtracker.TypeError, lambda: lcm.get_color_at(0, ""))
        self.assertRaises(trajtracker.TypeError, lambda: lcm.get_color_at(0, 0.5))
        self.assertRaises(trajtracker.TypeError, lambda: lcm.get_color_at(0, 0, use_mapping=""))


    #-------------------------------------------------------------------------
    def test_colormap_missing(self):
        lcm = LocationColorMap(testimage)
        self.assertRaises(trajtracker.ValueError, lambda: lcm.get_color_at(0, 0, use_mapping=True))

    #-------------------------------------------------------------------------
    def test_rgb_mapping(self):
        lcm = LocationColorMap([[(0,0,255), (0,255,0), (255,0,0), (1,2,4), (0,0,0)]])
        lcm.colormap = "RGB"
        lcm.use_mapping = True
        self.assertEqual(lcm.get_color_at(-2, 0), 255)
        self.assertEqual(lcm.get_color_at(-1, 0), 255*256)
        self.assertEqual(lcm.get_color_at(0, 0), 255*256*256)
        self.assertEqual(lcm.get_color_at(1, 0), 4 + 2*256 + 1*256*256)




if __name__ == '__main__':
    unittest.main()
