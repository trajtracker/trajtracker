import unittest

import trajtracker

from trajtracker.events import Event


class EventTests(unittest.TestCase):

    #===============================================
    # Define events
    #===============================================

    def test_create_event(self):
        e = Event("a")
        self.assertEqual("a", e.event_id)
        self.assertEqual(0, e.offset)


    def test_change_offset(self):
        e = (Event("a") + 2.5) + 0
        self.assertEqual("a", e.event_id)
        self.assertEqual(2.5, e.offset)


    def test_negative_offset(self):
        self.assertRaises(trajtracker.ValueError, lambda: Event("a") + (-3))


    #===============================================
    # Parse from string
    #===============================================

    def test_parse_no_offset(self):
        e = Event.parse(" a ")
        self.assertEqual("a", e.event_id)
        self.assertEqual(0, e.offset)


    def test_parse_with_offset(self):
        e = Event.parse(" a + 2.5")
        self.assertEqual("a", e.event_id)
        self.assertEqual(2.5, e.offset)


    def test_parse_none(self):
        self.assertIsNone(Event.parse(" nOnE "))


    def test_parse_bad_id(self):
        self.assertRaises(trajtracker.ValueError, lambda: Event.parse(" {} "))


    def test_parse_bad_offset(self):
        self.assertRaises(trajtracker.ValueError, lambda: Event.parse(" a + b "))


    def test_parse_bad_format(self):
        self.assertRaises(trajtracker.ValueError, lambda: Event.parse(" a - 3 "))



if __name__ == '__main__':
    unittest.main()
