import unittest
from trajtracker.validators import FingerLiftedValidator
import trajtracker as ttrk


class MyTestCase(unittest.TestCase):


    #--------------------------------------------------------
    def test_default_constructor(self):
        FingerLiftedValidator()


    #--------------------------------------------------------
    def test_set_enabled(self):
        FingerLiftedValidator(enabled=True)
        self.assertRaises(ttrk.TypeError, lambda: FingerLiftedValidator(enabled=None))
        self.assertRaises(ttrk.TypeError, lambda: FingerLiftedValidator(enabled=""))


    #--------------------------------------------------------
    def test_set_max_offscreen_duration(self):
        FingerLiftedValidator(max_offscreen_duration=1)
        self.assertRaises(ttrk.TypeError, lambda: FingerLiftedValidator(max_offscreen_duration=None))
        self.assertRaises(ttrk.TypeError, lambda: FingerLiftedValidator(max_offscreen_duration=""))
        self.assertRaises(ttrk.ValueError, lambda: FingerLiftedValidator(max_offscreen_duration=-1))


    #--------------------------------------------------------
    def test_error_immediate(self):
        v = FingerLiftedValidator(max_offscreen_duration=0)
        v.reset()
        self.assertIsNone(v.update_touching(True, 0, 1))
        self.assertIsNone(v.update_touching(True, 0, 2))
        self.assertIsNotNone(v.update_touching(False, 0, 2))
        self.assertIsNotNone(v.update_touching(False, 0, 2.0001))


    #--------------------------------------------------------
    def test_error_delayed(self):
        v = FingerLiftedValidator(max_offscreen_duration=1)
        v.reset()
        self.assertIsNone(v.update_touching(True, 0, 1))
        self.assertIsNone(v.update_touching(True, 0, 2))
        self.assertIsNone(v.update_touching(False, 0, 3))
        self.assertIsNotNone(v.update_touching(False, 0, 3.0001))


    #--------------------------------------------------------
    def test_disabled(self):
        v = FingerLiftedValidator(max_offscreen_duration=1, enabled=False)
        v.reset()
        self.assertIsNone(v.update_touching(True, 0, 1))
        self.assertIsNone(v.update_touching(True, 0, 2))
        self.assertIsNone(v.update_touching(False, 0, 5))
        v.enabled = True
        self.assertIsNotNone(v.update_touching(False, 0, 5))



if __name__ == '__main__':
    unittest.main()
