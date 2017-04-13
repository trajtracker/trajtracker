import unittest

from trajtracker.movement import StartPoint
from trajtracker.misc import nvshapes


class StartPointTests(unittest.TestCase):


    #------------------------------------------------
    def test_init(self):
        StartPoint(nvshapes.Rectangle((1, 1)))
        self.assertRaises(ValueError, lambda: StartPoint(None))

    #------------------------------------------------
    def test_non_start(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        self.assertIsNone(sp.check_xy(200, 200))
        self.assertEqual(sp.State.reset, sp._state)

    #------------------------------------------------
    def test_start_and_err(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        self.assertEqual(sp.State.init, sp.check_xy(0, 0))
        self.assertEqual(sp.State.error, sp.check_xy(200, 200))

    #------------------------------------------------
    def test_start_and_ok_up(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)))
        self.assertEqual(sp.State.init, sp.check_xy(0, 0))
        self.assertIsNone(sp.check_xy(0, 25))
        self.assertEqual(sp.State.start, sp.check_xy(0, 26))

    #------------------------------------------------
    def test_start_and_ok_down(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="below")
        self.assertEqual(sp.State.init, sp.check_xy(0, 0))
        self.assertIsNone(sp.check_xy(0, -25))
        self.assertEqual(sp.State.start, sp.check_xy(0, -26))

    #------------------------------------------------
    def test_start_and_ok_right(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="right")
        self.assertEqual(sp.State.init, sp.check_xy(0, 0))
        self.assertIsNone(sp.check_xy(50, 0))
        self.assertEqual(sp.State.start, sp.check_xy(51, 0))

    #------------------------------------------------
    def test_start_and_ok_left(self):
        sp = StartPoint(nvshapes.Rectangle((100, 50)), exit_area="left")
        self.assertEqual(sp.State.init, sp.check_xy(0, 0))
        self.assertIsNone(sp.check_xy(-50, 0))
        self.assertEqual(sp.State.start, sp.check_xy(-51, 0))


if __name__ == '__main__':
    unittest.main()
