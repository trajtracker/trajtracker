import unittest

import trajtracker as ttrk
from trajtracker.stimuli import FixationZoom


#----------------------------------------------------------
class MyDot(ttrk.misc.nvshapes.Circle):

    def __init__(self):
        super(MyDot, self).__init__(0, 0, 1)

    def present(self, c=True, u=True):
        pass


#----------------------------------------------------------
def generate_dot(fixation):
    return MyDot()


#----------------------------------------------------------
def n_visible_dots(fixation):
    return sum([dot.visible for dot in fixation._dots])



class FixationZoomTests(unittest.TestCase):

    #============================================================================
    #         Set properties
    #============================================================================

    #---------------------------------------------------------
    def test_configure(self):
        FixationZoom()


    #---------------------------------------------------------
    def test_set_position(self):
        FixationZoom(position=(0, 0))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(position='a'))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(position=None))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(position=(0, 'a')))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(position=(0, 0.1)))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(position=(0, 0, 3)))


    #---------------------------------------------------------
    def test_set_box_size(self):
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(box_size='a'))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(box_size=None))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(box_size=(0, 'a')))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(box_size=(0, 0, 3)))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(box_size=(0.1, 0)))
        self.assertRaises(ttrk.ValueError, lambda: FixationZoom(box_size=(-10, 0)))


    #---------------------------------------------------------
    def test_set_dot_radius(self):
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_radius='a'))
        self.assertRaises(ttrk.ValueError, lambda: FixationZoom(dot_radius=0))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_radius=None))


    #---------------------------------------------------------
    def test_set_dot_colour(self):
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_colour='a'))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_colour=0))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_colour=None))


    #---------------------------------------------------------
    def test_set_dot_generator(self):
        FixationZoom(dot_generator=generate_dot)
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(dot_generator='a'))


    #---------------------------------------------------------
    def test_set_zoom_duration(self):
        FixationZoom(zoom_duration=1)
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(zoom_duration='a'))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(zoom_duration=None))
        self.assertRaises(ttrk.ValueError, lambda: FixationZoom(zoom_duration=-1))
        self.assertRaises(ttrk.ValueError, lambda: FixationZoom(zoom_duration=0))


    #---------------------------------------------------------
    def test_set_stay_duration(self):
        FixationZoom(stay_duration=1)
        FixationZoom(stay_duration=0)
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(stay_duration='a'))
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(stay_duration=None))
        self.assertRaises(ttrk.ValueError, lambda: FixationZoom(stay_duration=-1))


    #---------------------------------------------------------
    def test_set_show_event(self):
        FixationZoom(show_event=ttrk.events.TRIAL_ENDED)
        FixationZoom(show_event=None)
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(show_event='a'))


    #---------------------------------------------------------
    def test_set_start_zoom_event(self):
        FixationZoom(start_zoom_event=ttrk.events.TRIAL_ENDED)
        FixationZoom(start_zoom_event=None)
        self.assertRaises(ttrk.TypeError, lambda: FixationZoom(start_zoom_event='a'))


    #============================================================================
    #         Run
    #============================================================================


    #----------------------------------------------------------------
    def test_generator(self):
        fix = FixationZoom(dot_generator=generate_dot)
        fix.reset(0)
        self.assertEqual(MyDot, type(fix._dots[0]))


    #----------------------------------------------------------------
    def test_show(self):
        fix = FixationZoom(zoom_duration=10, stay_duration=1, box_size=(10, 20),
                           position=(100, 200), dot_generator=generate_dot)

        fix.reset(10)
        self.assertEqual(0, n_visible_dots(fix))

        topleft = fix._dots[0]
        topright = fix._dots[1]
        bottomleft = fix._dots[2]
        bottomright = fix._dots[3]

        fix.show()
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((95, 190), topleft.position)
        self.assertEqual((105, 190), topright.position)
        self.assertEqual((95, 210), bottomleft.position)
        self.assertEqual((105, 210), bottomright.position)

        fix.start_zoom(1000)
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((95, 190), topleft.position)
        self.assertEqual((105, 190), topright.position)
        self.assertEqual((95, 210), bottomleft.position)
        self.assertEqual((105, 210), bottomright.position)

        #-- No movement yet
        fix.update(1000)
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((95, 190), topleft.position)
        self.assertEqual((105, 190), topright.position)
        self.assertEqual((95, 210), bottomleft.position)
        self.assertEqual((105, 210), bottomright.position)

        #-- Moved 40%
        fix.update(1004)
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((97, 194), topleft.position)
        self.assertEqual((103, 194), topright.position)
        self.assertEqual((97, 206), bottomleft.position)
        self.assertEqual((103, 206), bottomright.position)

        #-- Moved 100%
        fix.update(1010)
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((100, 200), topleft.position)
        self.assertEqual((100, 200), topright.position)
        self.assertEqual((100, 200), bottomleft.position)
        self.assertEqual((100, 200), bottomright.position)

        #-- Still visible
        fix.update(1011)
        self.assertEqual(4, n_visible_dots(fix))
        self.assertEqual((100, 200), topleft.position)
        self.assertEqual((100, 200), topright.position)
        self.assertEqual((100, 200), bottomleft.position)
        self.assertEqual((100, 200), bottomright.position)

        #-- Hidden
        fix.update(1011.01)
        self.assertEqual(0, n_visible_dots(fix))



if __name__ == '__main__':
    unittest.main()
