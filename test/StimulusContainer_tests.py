
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


    #-------------------------------------------
    def test_callback_non_recurring(self):

        c = StimulusContainer()
        c.add(DummyStimulus(), "a")
        c.add(DummyStimulus(), "b", visible=False)
        cbk = StimContainerCallback()

        c.register_callback(cbk)

        #-- Make sure callback was called
        c.present()
        self.assertEqual(1, cbk.n_times_called)
        self.assertEqual(('a',), cbk.visible_stim_ids)
        self.assertEqual(c, cbk.stim_container)

        c.present()
        self.assertEqual(1, cbk.n_times_called)


    #-------------------------------------------
    def test_callback_recurring(self):

        c = StimulusContainer()
        c.add(DummyStimulus(), "a")
        c.add(DummyStimulus(), "b", visible=False)
        cbk = StimContainerCallback()

        c.register_callback(cbk, recurring=True, func_id="cb")

        #-- Make sure callback was called
        c.present()
        self.assertEqual(1, cbk.n_times_called)
        self.assertEqual(('a',), cbk.visible_stim_ids)

        c.present()
        self.assertEqual(2, cbk.n_times_called)


    #-------------------------------------------
    def test_unregister_recurring_callback(self):

        c = StimulusContainer()
        c.add(DummyStimulus(), "a")
        c.add(DummyStimulus(), "b", visible=False)
        cbk = StimContainerCallback()

        c.register_callback(cbk, recurring=True, func_id="cb")
        self.assertTrue(c.unregister_recurring_callback("cb"))

        c.present()
        self.assertEqual(0, cbk.n_times_called)


#-------------------------------------------------------
class StimContainerCallback(object):

    def __init__(self):
        self.visible_stim_ids = ()
        self.n_times_called = 0
        self.stim_container = None


    def __call__(self, stim_container, visible_stim_ids, time):
        self.visible_stim_ids = visible_stim_ids
        self.n_times_called += 1
        self.stim_container = stim_container


if __name__ == '__main__':
    unittest.main()
