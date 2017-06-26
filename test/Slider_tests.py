import unittest

import trajtracker as ttrk
from trajtracker.stimuli import Slider, Orientation
from ttrk_testing import DummyStimulus



class SliderTests(unittest.TestCase):


    #=============================================================================
    # Configure the slider
    #=============================================================================

    #-----------------------------------------------------------------------
    def test_create(self):
        Slider(DummyStimulus(), DummyStimulus())


    #-----------------------------------------------------------------------
    def test_create_bad_stimulus(self):
        self.assertRaises(ttrk.TypeError, lambda: Slider(5, DummyStimulus()))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), 5))


    #-----------------------------------------------------------------------
    def test_set_visible(self):
        Slider(DummyStimulus(), DummyStimulus(), visible=True)
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), visible=None))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), visible=1))


    #-----------------------------------------------------------------------
    def test_visible_works(self):
        bgnd = DummyStimulus()
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge)

        self.assertFalse(bgnd.visible)
        self.assertFalse(gauge.visible)

        slider.current_value = 5

        self.assertFalse(bgnd.visible)
        self.assertFalse(gauge.visible)

        slider.visible = True
        self.assertTrue(bgnd.visible)
        self.assertTrue(gauge.visible)

        slider.visible = False
        self.assertFalse(bgnd.visible)
        self.assertFalse(gauge.visible)


    #-----------------------------------------------------------------------
    def test_visible_with_curr_val(self):
        bgnd = DummyStimulus()
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge)

        slider.visible = True
        self.assertTrue(bgnd.visible)
        self.assertFalse(gauge.visible)

        slider.current_value = 5
        self.assertTrue(gauge.visible)

        slider.current_value = None
        self.assertFalse(gauge.visible)

        slider.current_value = 5
        slider.visible = False
        self.assertFalse(gauge.visible)

        slider.visible = True
        self.assertTrue(gauge.visible)


    #-----------------------------------------------------------------------
    def test_set_locked(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        slider.locked = True

        try:
            slider.locked = None
            self.fail("Succeeded setting an invalid value")
        except ttrk.TypeError:
            pass

        try:
            slider.locked = 1
            self.fail("Succeeded setting an invalid value")
        except ttrk.TypeError:
            pass


    #-----------------------------------------------------------------------
    def test_set_orientation(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        self.assertEqual(slider._orientation_ind, 0)

        slider = Slider(DummyStimulus(), DummyStimulus(), orientation=Orientation.Vertical)
        self.assertEqual(slider._orientation_ind, 1)

        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), orientation=None))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), orientation=""))


    #-----------------------------------------------------------------------
    def test_set_min_value(self):
        Slider(DummyStimulus(), DummyStimulus(), min_value=10)
        Slider(DummyStimulus(), DummyStimulus(), min_value=10.0)
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), min_value=None))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), min_value=""))


    #-----------------------------------------------------------------------
    def test_set_max_value(self):
        Slider(DummyStimulus(), DummyStimulus(), max_value=10)
        Slider(DummyStimulus(), DummyStimulus(), max_value=10.0)
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), max_value=None))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), max_value=""))


    #-----------------------------------------------------------------------
    def test_set_default_value(self):
        Slider(DummyStimulus(), DummyStimulus(), default_value=None)
        Slider(DummyStimulus(), DummyStimulus(), default_value=10)
        Slider(DummyStimulus(), DummyStimulus(), default_value=10.0)
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), default_value=""))


    #-----------------------------------------------------------------------
    def test_set_max_moves(self):
        Slider(DummyStimulus(), DummyStimulus(), max_moves=None)
        Slider(DummyStimulus(), DummyStimulus(), max_moves=10)
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), max_moves=""))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), max_moves=1.5))


    #-----------------------------------------------------------------------
    def test_set_position(self):
        bgnd_stim = DummyStimulus(position=(1, 1))

        slider = Slider(bgnd_stim, DummyStimulus(), position=None)
        self.assertEqual(bgnd_stim.position, (1, 1))
        self.assertEqual(slider.position, (1, 1))

        Slider(bgnd_stim, DummyStimulus(), position=(0, 0))
        self.assertEqual(bgnd_stim.position, (0, 0))


    #-----------------------------------------------------------------------
    def test_get_size(self):
        slider = Slider(DummyStimulus(size=(100, 100)), DummyStimulus())
        self.assertEqual(slider.size, (100, 100))


    #-----------------------------------------------------------------------
    def test_set_slidable_range(self):
        Slider(DummyStimulus(), DummyStimulus(), slidable_range=None)
        Slider(DummyStimulus(), DummyStimulus(), slidable_range=[-10, 10])
        Slider(DummyStimulus(), DummyStimulus(), slidable_range=(-10, 10))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), slidable_range=""))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), slidable_range=('a', 1)))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), slidable_range=(1, 'a')))
        self.assertRaises(ttrk.TypeError, lambda: Slider(DummyStimulus(), DummyStimulus(), slidable_range=(None, 'a')))


    #-----------------------------------------------------------------------
    def test_set_clickable_area(self):
        slider = Slider(DummyStimulus(), DummyStimulus())

        slider.set_clickable_area(ttrk.misc.nvshapes.Rectangle((10, 10), (0, 0)))
        slider.set_clickable_area(None)
        self.assertRaises(ttrk.TypeError, lambda: slider.set_clickable_area(1))


    #-----------------------------------------------------------------------
    def test_set_drag_area(self):
        slider = Slider(DummyStimulus(), DummyStimulus())

        slider.set_drag_area(ttrk.misc.nvshapes.Rectangle((10, 10), (0, 0)))
        slider.set_drag_area(None)
        self.assertRaises(ttrk.TypeError, lambda: slider.set_drag_area(1))


    #=============================================================================
    #     Test functions that handle the slider scale
    #=============================================================================


    #-----------------------------------------------------------------------
    def test_gauge_min_max_coords_default_horizontal(self):
        slider = Slider(DummyStimulus(position=(10, 0), size=(20, 50)), DummyStimulus(), orientation=Orientation.Horizontal)
        self.assertEqual(slider._get_gauge_min_max_coords(), (0, 20))


    #-----------------------------------------------------------------------
    def test_gauge_min_max_coords_default_vertical(self):
        slider = Slider(DummyStimulus(position=(10, 30), size=(20, 50)), DummyStimulus(), orientation=Orientation.Vertical)
        self.assertEqual(slider._get_gauge_min_max_coords(), (5, 55))


    #-----------------------------------------------------------------------
    def test_gauge_min_max_coords_explicit(self):
        slider = Slider(DummyStimulus(), DummyStimulus(), slidable_range=[-90, 90])
        self.assertEqual(slider._get_gauge_min_max_coords(), (-90, 90))


    #-----------------------------------------------------------------------
    def test_crop_value(self):
        slider = Slider(DummyStimulus(), DummyStimulus(), min_value=5, max_value=15)
        self.assertEqual(slider._crop_value(5), 5)
        self.assertEqual(slider._crop_value(3), 5)
        self.assertEqual(slider._crop_value(15), 15)
        self.assertEqual(slider._crop_value(16.5), 15)

        slider = Slider(DummyStimulus(), DummyStimulus(), min_value=15, max_value=5)
        self.assertEqual(slider._crop_value(5), 5)
        self.assertEqual(slider._crop_value(3), 5)
        self.assertEqual(slider._crop_value(15), 15)
        self.assertEqual(slider._crop_value(16.5), 15)


    #-----------------------------------------------------------------------
    def test_set_current_value_none(self):
        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(size=(1000, 10), position=(10, 0)), gauge, min_value=0, max_value=100,
                        orientation=Orientation.Horizontal)
        slider.current_value = None
        self.assertIsNone(slider.current_value)
        self.assertFalse(gauge.visible)


    #-----------------------------------------------------------------------
    def test_set_current_value(self):
        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(size=(1000, 10), position=(10, 0)), gauge, min_value=0, max_value=100,
                        orientation=Orientation.Horizontal)
        slider.current_value = 75
        self.assertEqual(slider.current_value, 75)
        self.assertEqual(gauge.position, (260, 0))

        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(size=(10, 1000), position=(0, 10)), gauge, min_value=0, max_value=100,
                        orientation=Orientation.Vertical)
        slider.current_value = 75
        self.assertEqual(slider.current_value, 75)
        self.assertEqual(gauge.position, (0, 260))


    #-----------------------------------------------------------------------
    def test_set_current_value_reversed(self):
        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(size=(1000, 10), position=(10, 0)), gauge, min_value=100, max_value=0,
                        orientation=Orientation.Horizontal)
        slider.current_value = 75
        self.assertEqual(slider.current_value, 75)
        self.assertEqual(gauge.position, (-240, 0))

        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(size=(10, 1000), position=(0, 10)), gauge, min_value=100, max_value=0,
                        orientation=Orientation.Vertical)
        slider.current_value = 75
        self.assertEqual(slider.current_value, 75)
        self.assertEqual(gauge.position, (0, -240))


    #-----------------------------------------------------------------------
    def test_set_current_value_none(self):
        gauge = DummyStimulus()
        slider = Slider(DummyStimulus(), gauge)
        slider.current_value = None
        self.assertFalse(gauge.visible)


    #-----------------------------------------------------------------------
    def test_set_current_value_when_locked(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        slider.locked = True

        try:
            slider.current_value = None
            self.fail("Succeeded running an invalid operation")
        except ttrk.InvalidStateError:
            pass


    #=============================================================================
    #     Test click/drag areas
    #=============================================================================

    #-----------------------------------------------------------------------
    def test_valid_click_area_explicit(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        slider.set_clickable_area(ttrk.misc.nvshapes.Rectangle(size=(30, 20), position=(0, 0)))
        slider._now_dragging = False
        self.assertTrue(slider._is_valid_mouse_pos((15, 10)))
        self.assertFalse(slider._is_valid_mouse_pos((16, 10)))

    #-----------------------------------------------------------------------
    def test_valid_click_area_default(self):
        slider = Slider(DummyStimulus(size=(30, 20), position=(0, 0)), DummyStimulus())
        slider.set_clickable_area(None)
        slider._now_dragging = False
        self.assertTrue(slider._is_valid_mouse_pos((15, 10)))
        self.assertFalse(slider._is_valid_mouse_pos((16, 10)))

    #-----------------------------------------------------------------------
    def test_valid_drag_area_explicit(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        slider.set_drag_area(ttrk.misc.nvshapes.Rectangle(size=(30, 20), position=(0, 0)))
        slider._now_dragging = True
        self.assertTrue(slider._is_valid_mouse_pos((15, 10)))
        self.assertFalse(slider._is_valid_mouse_pos((16, 10)))

    #-----------------------------------------------------------------------
    def test_valid_drag_area_default(self):
        slider = Slider(DummyStimulus(), DummyStimulus())
        slider.set_drag_area(None)
        slider._now_dragging = True
        self.assertTrue(slider._is_valid_mouse_pos((1000, -1000)))

    #=============================================================================
    #     Test runtime API
    #=============================================================================

    #-----------------------------------------------------------------------
    def test_reset(self):
        slider = Slider(DummyStimulus(), DummyStimulus(), default_value=5)
        slider.locked = True
        slider._n_moves = 3

        slider.reset()
        self.assertFalse(slider.locked)
        self.assertEqual(slider.current_value, 5)
        self.assertEqual(slider.n_moves, 0)


    #-----------------------------------------------------------------------
    def test_update_noclick(self):
        slider = Slider(DummyStimulus(), DummyStimulus(), orientation=Orientation.Horizontal, default_value=None)
        slider.update(False, (0, 0))
        self.assertEqual(slider._now_dragging, False)
        self.assertEqual(slider.current_value, None)


    #-----------------------------------------------------------------------
    def test_update(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)

        slider.update(True, (10, 4))
        self.assertEqual(slider.current_value, 6)
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(slider.locked, False)
        self.assertEqual(gauge.position, (10, 0))

        slider.update(True, (20, -4))
        self.assertEqual(slider.current_value, 7)
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(gauge.position, (20, 0))


    #-----------------------------------------------------------------------
    def test_update_drag_to_out_of_gauge_range(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)

        slider.update(True, (20, -4))
        slider.update(True, (200, -4))
        self.assertEqual(slider.current_value, 10)
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(gauge.position, (50, 0))


    #-----------------------------------------------------------------------
    def test_update_n_moves(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)

        slider.update(True, (0, 0))
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(slider._now_dragging, True)

        slider.update(False, (0, 0))
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(slider._now_dragging, False)

        slider.update(True, (0, 0))
        self.assertEqual(slider.n_moves, 2)

        slider.update(False, (0, 0))
        self.assertEqual(slider.n_moves, 2)

        slider.update(True, (0, 0))
        self.assertEqual(slider.n_moves, 3)

        slider.update(False, (0, 0))
        self.assertEqual(slider.n_moves, 3)


    #-----------------------------------------------------------------------
    def test_update_ignored_when_out_of_range(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)

        slider.update(True, (200, -4))
        self.assertEqual(slider.current_value, None)
        self.assertEqual(slider.n_moves, 0)


    #-----------------------------------------------------------------------
    def test_update_ignored_when_locked(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)
        slider.locked = True

        slider.update(True, (0, 0))
        self.assertEqual(slider.current_value, None)
        self.assertEqual(slider.n_moves, 0)



    #-----------------------------------------------------------------------
    def test_update_to_out_of_drag_range(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10)
        slider.set_drag_area(ttrk.misc.nvshapes.Rectangle(size=(200, 20)))

        slider.update(True, (0, 0))
        self.assertEqual(slider.current_value, 5)
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(slider._now_dragging, True)
        self.assertEqual(gauge.position, (0, 0))

        slider.update(True, (10, 50))
        self.assertEqual(slider.current_value, 5)
        self.assertEqual(slider.n_moves, 1)
        self.assertEqual(slider._now_dragging, False)
        self.assertEqual(gauge.position, (0, 0))

        slider.update(True, (0, 0))
        slider.update(True, (200, 0))
        self.assertEqual(slider.current_value, 5)
        self.assertEqual(slider._now_dragging, False)
        self.assertEqual(gauge.position, (0, 0))



    #-----------------------------------------------------------------------
    def test_lock_on_max_moves_exceeded(self):
        bgnd = DummyStimulus(size=(100, 10), position=(0, 0))
        gauge = DummyStimulus()
        slider = Slider(bgnd, gauge, orientation=Orientation.Horizontal, min_value=0, max_value=10, max_moves=2)

        # First gauge-move
        slider.update(True, (0, 0))
        slider.update(False, (0, 0))
        self.assertEqual(slider.locked, False)

        # Second gauge-move
        slider.update(True, (0, 0))
        slider.update(False, (0, 0))
        self.assertEqual(slider.locked, True)



if __name__ == '__main__':
    unittest.main()
