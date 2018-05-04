import unittest

import trajtracker as ttrk
from trajtracker.misc.nvshapes import Rectangle
from trajtracker.movement import Hotspot
from trajtracker.events import EventManager



class CallbackObj(object):

    def __init__(self):
        self.called = 0

    def __call__(self, *args, **kwargs):
        self.called += 1


class DbgEventManager(object):

    def __init__(self):
        self.dispatched = 0

    def dispatch_event(self, event, time_in_trial, time_in_session):
        self.dispatched += 1


class HotspotTests(unittest.TestCase):

    #==========================================================================
    # Configuration
    #==========================================================================

    #------------------------------------------------
    def test_create_empty(self):
        Hotspot()

    #------------------------------------------------
    def test_set_name(self):
        Hotspot(name='a')
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(name=None))
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(name=3))

    #------------------------------------------------
    def test_set_enabled(self):
        Hotspot(enabled=False)
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(enabled=""))
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(enabled=None))

    #------------------------------------------------
    def test_set_area(self):
        Hotspot(area=Rectangle((10, 10)))
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(area=""))

    #------------------------------------------------
    def test_set_min_touch_duration(self):
        Hotspot(min_touch_duration=3.5)
        Hotspot(min_touch_duration=0)
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(min_touch_duration=""))
        self.assertRaises(ttrk.ValueError, lambda: Hotspot(min_touch_duration=-4))

    #------------------------------------------------
    def test_on_touched_callback(self):
        Hotspot(on_touched_callback=lambda t: 1)
        self.assertRaises(ttrk.TypeError, lambda: Hotspot(on_touched_callback=""))

    #------------------------------------------------
    def test_on_touched_event(self):
        Hotspot(event_manager=EventManager(), on_touched_dispatch_event="event")

        self.assertRaises(ttrk.TypeError, lambda: Hotspot(event_manager=EventManager(), on_touched_dispatch_event=3))
        self.assertRaises(ttrk.ValueError, lambda: Hotspot(on_touched_dispatch_event="event"))


    #==========================================================================
    # Touch
    #==========================================================================

    #------------------------------------------------
    def test_call_action(self):
        cb = CallbackObj()
        spot = Hotspot(area=Rectangle((10, 10)), on_touched_callback=cb)

        # Action not invoked
        spot.update_xyt((20, 20), 1)
        self.assertEquals(0, cb.called)

        # Action invoked
        spot.update_xyt((4, 4), 1)
        self.assertEquals(1, cb.called)


    #------------------------------------------------
    def test_dispatch_event(self):
        em = DbgEventManager()
        spot = Hotspot(em, area=Rectangle((10, 10)), on_touched_dispatch_event="a")

        spot.update_xyt((4, 4), 1, 1)
        self.assertEquals(1, em.dispatched)


    #------------------------------------------------
    def test_disabled(self):
        em = DbgEventManager()
        cb = CallbackObj()
        spot = Hotspot(em, area=Rectangle((10, 10)), on_touched_callback=cb, on_touched_dispatch_event="a", enabled=False)

        spot.update_xyt((4, 4), 1, 1)
        self.assertEquals(0, em.dispatched)
        self.assertEquals(0, cb.called)


    #------------------------------------------------
    def test_call_action_delayed(self):
        cb = CallbackObj()
        spot = Hotspot(area=Rectangle((10, 10)), on_touched_callback=cb, min_touch_duration=10)

        spot.update_xyt((20, 20), 0)   # not touched

        # touching for less than 10 sec: not called
        spot.update_xyt((4, 4), 1)
        spot.update_xyt((1, 1), 10)
        self.assertEquals(0, cb.called)

        # touching for 10 sec - should call
        spot.update_xyt((1, 1), 11)
        self.assertEquals(1, cb.called)

        # touching for longer - not called again
        spot.update_xyt((1, 1), 12)
        spot.update_xyt((1, 1), 13)
        self.assertEquals(1, cb.called)

    #------------------------------------------------
    def test_call_action_delayed_aborted(self):
        cb = CallbackObj()
        spot = Hotspot(area=Rectangle((10, 10)), on_touched_callback=cb, min_touch_duration=10)

        spot.update_xyt((20, 20), 0)  # not touched

        # touching for less than 10 sec, then aborting touch
        spot.update_xyt((4, 4), 1)
        spot.update_xyt((1, 1), 10)
        spot.update_xyt((1, 10), 15)
        self.assertEquals(0, cb.called)

        # touching again - time count is restarted
        spot.update_xyt((1, 1), 16)
        spot.update_xyt((1, 1), 25)
        self.assertEquals(0, cb.called)
        spot.update_xyt((1, 1), 26)
        self.assertEquals(1, cb.called)




            #todo: add tests

if __name__ == '__main__':
    unittest.main()
