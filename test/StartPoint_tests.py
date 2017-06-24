import unittest

import trajtracker
from trajtracker.movement import StartPoint
from trajtracker.misc import nvshapes


class StartPointTests(unittest.TestCase):


    #------------------------------------------------
    def test_init(self):
        StartPoint(nvshapes.Rectangle((1, 1)))
        self.assertRaises(trajtracker.ValueError, lambda: StartPoint(None))

    #------------------------------------------------
    def test_non_start(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        sp._state = StartPoint.State.mouse_up
        self.assertFalse(sp.check_xy(200, 200))
        self.assertEqual(sp.State.mouse_up, sp._state)

    #------------------------------------------------
    def test_start_and_err(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        sp._state = StartPoint.State.mouse_up
        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertTrue(sp.check_xy(200, 200))
        self.assertEqual(sp.State.error, sp.state)

    #------------------------------------------------
    def test_start_and_ok_up(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        sp._state = StartPoint.State.mouse_up
        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertFalse(sp.check_xy(0, 25))
        self.assertTrue(sp.check_xy(0, 26))
        self.assertEqual(sp.State.start, sp.state)

    #------------------------------------------------
    def test_start_and_ok_down(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="below")
        sp._state = StartPoint.State.mouse_up

        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertFalse(sp.check_xy(0, -25))
        self.assertTrue(sp.check_xy(0, -26))
        self.assertEqual(sp.State.start, sp.state)

    #------------------------------------------------
    def test_start_and_ok_right(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="right")
        sp._state = StartPoint.State.mouse_up

        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertFalse(sp.check_xy(50, 0))
        self.assertTrue(sp.check_xy(51, 0))
        self.assertEqual(sp.State.start, sp.state)

    #------------------------------------------------
    def test_start_and_ok_left(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="left")
        sp._state = StartPoint.State.mouse_up

        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertFalse(sp.check_xy(-50, 0))
        self.assertTrue(sp.check_xy(-51, 0))
        self.assertEqual(sp.State.start, sp.state)


    #------------------------------------------------
    def test_start_with_exit_area_none(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area=None)
        sp._state = StartPoint.State.mouse_up

        self.assertTrue(sp.check_xy(0, 0))
        self.assertEqual(sp.State.init, sp.state)
        self.assertTrue(sp.check_xy(-51, 0))
        self.assertEqual(sp.State.start, sp.state)


if __name__ == '__main__':
    unittest.main()
