import unittest

import trajtracker as ttrk
from trajtracker.misc.nvshapes import Rectangle
from trajtracker.movement import Hotspot
from trajtracker.events import EventManager


class HotspotTests(unittest.TestCase):


    #==========================================================================
    # Configuration
    #==========================================================================

    #------------------------------------------------
    def test_create_empty(self):
        Hotspot()

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

    #todo: add tests

if __name__ == '__main__':
    unittest.main()
