
import unittest

from trajtracker.stimuli import StimulusContainer
from ttrk_testing import DummyStimulus

class StimulusContainerTests(unittest.TestCase):

    #-------------------------------------------
    def test_add_get(self):
        c = StimulusContainer()
        a = DummyStimulus()
        b = DummyStimulus()
        c.add(a, "a")
        c.add(b, "b")

        self.assertEqual(a, c['a'])
        self.assertEqual(b, c['b'])


    #-------------------------------------------
    def test_present(self):
        c = StimulusContainer()
        a = DummyStimulus()
        b = DummyStimulus()
        c.add(a, "a")
        c.add(b, "b")

        c.present()
        self.assertTrue(a.presented)
        self.assertTrue(b.presented)

        self.assertEqual(True, a.presented_args['clear'])
        self.assertEqual(False, a.presented_args['update'])

        self.assertEqual(False, b.presented_args['clear'])
        self.assertEqual(True, b.presented_args['update'])


    #-------------------------------------------
    def test_invisible(self):
        c = StimulusContainer()
        a = DummyStimulus()
        b = DummyStimulus()
        c.add(a, "a")
        c.add(b, "b")
        c["b"].visible = False

        c.present()

        self.assertEqual(True, a.presented)
        self.assertEqual(False, b.presented)

        self.assertEqual(0, len(b.presented_args))

        self.assertEqual(True, a.presented_args['clear'])
        self.assertEqual(True, a.presented_args['update'])




if __name__ == '__main__':
    unittest.main()
