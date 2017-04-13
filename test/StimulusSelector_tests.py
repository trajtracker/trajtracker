import unittest


import trajtracker
from trajtracker.stimuli import StimulusSelector
from ttrk_testing import DummyStimulus


class StimulusSelectorTests(unittest.TestCase):

    def test_select(self):
        a = DummyStimulus()
        b = DummyStimulus()
        sel = StimulusSelector([["a", a], ["b", b]])
        self.assertIsNone(sel.active_stimulus)

        sel.activate("a")
        self.assertEqual(a, sel.active_stimulus)

        sel.activate("b")
        self.assertEqual(b, sel.active_stimulus)


    def test_select_invalid(self):
        a = DummyStimulus()
        sel = StimulusSelector([["a", a]])
        self.assertRaises(trajtracker.ValueError, lambda: sel.activate("c"))


if __name__ == '__main__':
    unittest.main()
