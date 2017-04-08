import unittest


import trajtracker
from trajtracker.stimuli import RSVPText
from trajtracker.events import *


class RSVPTextTests(unittest.TestCase):


    def setUp(self):
        trajtracker._TTrkObject.log_to_console = True


    #==============================================================================
    #   Configure stimulus properties
    #==============================================================================

    #---------------------------------------------------
    def test_create_empty(self):
        RSVPText()

    #---------------------------------------------------
    def test_set_text(self):
        rsvp = RSVPText(text=['a', 'b'])
        self.assertEqual(['a', 'b'], rsvp.text)
        rsvp.text = 'a',
        rsvp.text = None

    def test_set_text_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text='hi'))
        self.assertRaises(TypeError, lambda: RSVPText(text=5))
        self.assertRaises(TypeError, lambda: RSVPText(text=[5]))
        self.assertRaises(TypeError, lambda: RSVPText(text=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text=[None]))

    #---------------------------------------------------
    def test_set_text_font(self):
        rsvp = RSVPText(text_font='Arial')
        self.assertEqual('Arial', rsvp.text_font)
        rsvp.text_font = 'Arial','Barial'
        rsvp.text_font = None

    def test_set_text_font_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_font=5))
        self.assertRaises(TypeError, lambda: RSVPText(text_font=[5]))
        self.assertRaises(TypeError, lambda: RSVPText(text_font=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_font=[None]))

    #---------------------------------------------------
    def test_set_text_size(self):
        rsvp = RSVPText(text_size=10)
        self.assertEqual(10, rsvp.text_size)
        rsvp.text_size = 3, 5
        rsvp.text_size = None

    def test_set_text_size_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_size='a'))
        self.assertRaises(TypeError, lambda: RSVPText(text_size=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(text_size=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_size=[None]))

    #---------------------------------------------------
    def test_set_text_bold(self):
        rsvp = RSVPText(text_bold=True)
        self.assertEqual(True, rsvp.text_bold)
        rsvp.text_bold = True, True

    def test_set_text_bold_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_bold=None))
        self.assertRaises(TypeError, lambda: RSVPText(text_bold='a'))
        self.assertRaises(TypeError, lambda: RSVPText(text_bold=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(text_bold=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_bold=[None]))

    #---------------------------------------------------
    def test_set_text_italic(self):
        rsvp = RSVPText(text_italic=True)
        self.assertEqual(True, rsvp.text_italic)
        rsvp.text_italic = True, True

    def test_set_text_italic_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_italic=None))
        self.assertRaises(TypeError, lambda: RSVPText(text_italic='a'))
        self.assertRaises(TypeError, lambda: RSVPText(text_italic=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(text_italic=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_italic=[None]))

    #---------------------------------------------------
    def test_set_text_underline(self):
        rsvp = RSVPText(text_underline=True)
        self.assertEqual(True, rsvp.text_underline)
        rsvp.text_underline = True, True

    def test_set_text_underline_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_underline=None))
        self.assertRaises(TypeError, lambda: RSVPText(text_underline='a'))
        self.assertRaises(TypeError, lambda: RSVPText(text_underline=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(text_underline=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_underline=[None]))

    #---------------------------------------------------
    def test_set_text_colour(self):
        rsvp = RSVPText(text_colour=(1,2,3))
        self.assertEqual((1,2,3), rsvp.text_colour)
        rsvp.text_colour = (1, 2, 3), (4, 5, 6)
        rsvp.text_colour = None

    def test_set_text_colour_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(text_colour='a'))
        self.assertRaises(TypeError, lambda: RSVPText(text_colour=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(text_colour=[]))
        self.assertRaises(TypeError, lambda: RSVPText(text_colour=[None]))

    #---------------------------------------------------
    def test_set_background_colour(self):
        rsvp = RSVPText(background_colour=(1,2,3))
        self.assertEqual((1,2,3), rsvp.background_colour)
        rsvp.background_colour = (1, 2, 3), (4, 5, 6)
        rsvp.background_colour = None

    def test_set_background_colour_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(background_colour='a'))
        self.assertRaises(TypeError, lambda: RSVPText(background_colour=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(background_colour=[]))
        self.assertRaises(TypeError, lambda: RSVPText(background_colour=[None]))

    #---------------------------------------------------
    def test_set_size(self):
        rsvp = RSVPText(size=(10, 10))
        self.assertEqual((10, 10), rsvp.size)
        rsvp.size = (1, 2), (4, 5)
        rsvp.size = None

    def test_set_size_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(size=(1, )))
        self.assertRaises(TypeError, lambda: RSVPText(size=('a', 'b')))
        self.assertRaises(TypeError, lambda: RSVPText(size='a'))
        self.assertRaises(TypeError, lambda: RSVPText(size=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(size=[(1,)]))
        self.assertRaises(TypeError, lambda: RSVPText(size=[('a','b')]))
        self.assertRaises(TypeError, lambda: RSVPText(size=[]))
        self.assertRaises(TypeError, lambda: RSVPText(size=[None]))

    #---------------------------------------------------
    def test_set_position(self):
        rsvp = RSVPText(position=(10, 10))
        self.assertEqual((10, 10), rsvp.position)
        rsvp.position = (1, 2), (4, 5)
        rsvp.position = None

    def test_set_position_invalid(self):
        self.assertRaises(TypeError, lambda: RSVPText(position=(1, )))
        self.assertRaises(TypeError, lambda: RSVPText(position=('a', 'b')))
        self.assertRaises(TypeError, lambda: RSVPText(position='a'))
        self.assertRaises(TypeError, lambda: RSVPText(position=['a']))
        self.assertRaises(TypeError, lambda: RSVPText(position=[(1,)]))
        self.assertRaises(TypeError, lambda: RSVPText(position=[('a','b')]))
        self.assertRaises(TypeError, lambda: RSVPText(position=[]))
        self.assertRaises(TypeError, lambda: RSVPText(position=[None]))

    #==============================================================================
    #   Configure RSVP properties
    #==============================================================================

    #---------------------------------------------------
    def test_set_onset_time(self):
        rsvp = RSVPText(onset_time=(1, 2))
        self.assertEqual((1, 2), rsvp.onset_time)
        rsvp.onset_time = None

    def test_set_onset_time_invalid(self):
        self.assertRaises(ValueError, lambda: RSVPText(onset_time=[-5]))
        self.assertRaises(TypeError, lambda: RSVPText(onset_time=5))
        self.assertRaises(TypeError, lambda: RSVPText(onset_time='hi'))
        self.assertRaises(TypeError, lambda: RSVPText(onset_time=['hi']))
        self.assertRaises(TypeError, lambda: RSVPText(onset_time=[]))
        self.assertRaises(TypeError, lambda: RSVPText(onset_time=[None]))

    #---------------------------------------------------
    def test_set_duration(self):
        rsvp = RSVPText(duration=(1, 2))
        self.assertEqual((1, 2), rsvp.duration)
        rsvp.duration = 5
        rsvp.duration = None

    def test_set_duration_invalid(self):
        self.assertRaises(ValueError, lambda: RSVPText(duration=[-5]))
        self.assertRaises(ValueError, lambda: RSVPText(duration=[0]))
        self.assertRaises(TypeError, lambda: RSVPText(duration='hi'))
        self.assertRaises(TypeError, lambda: RSVPText(duration=['hi']))
        self.assertRaises(TypeError, lambda: RSVPText(duration=[]))
        self.assertRaises(TypeError, lambda: RSVPText(duration=[None]))

    #==============================================================================
    #   Validation function for RSVP properties
    #==============================================================================

    def _create_good_rsvp(self, text=('a', 'b', 'c'), text_font='Arial', text_size=1, text_justification="center",
                        text_colour=(255, 255, 255), background_colour=(0, 0, 0), size=(20, 20), position=(0, 0),
                        text_bold=False, text_italic=False, text_underline=False,
                        onset_time=(0, 1, 2), duration=1, start_event=TRIAL_STARTED):

        return RSVPText(text=text, text_font=text_font, text_size=text_size, text_justification=text_justification,
                        text_bold=text_bold, text_italic=text_italic, text_underline=text_underline,
                        text_colour=text_colour, background_colour=background_colour,
                        size=size, position=position, onset_time=onset_time, duration=duration,
                        start_rsvp_event=start_event)

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_ok(self):
        self._create_good_rsvp()._validate()
        self._create_good_rsvp(text_font=('Arial','Arial','Arial','Arial'))._validate()

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_font(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_font=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_font=('A', 'B'))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_size(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_size=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_size=(1,2))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_bold(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_bold=(True,True))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_italic(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_italic=(True,True))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_underline(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_underline=(True,True))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_justification(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_justification=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_justification=('center', 'center'))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_text_colour(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_colour=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(text_colour=((1, 2, 3), ))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_background_colour(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(background_colour=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(background_colour=((1, 2, 3), ))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_size(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(size=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(size=((10, 10), ))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_position(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(position=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(position=((10, 10), ))._validate())

    #---------------------------------------------------
    # noinspection PyTypeChecker
    def test_validate_bad_duration(self):
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(duration=None)._validate())
        self.assertRaises(ValueError, lambda: self._create_good_rsvp(duration=(10, 10))._validate())

    #==============================================================================
    #   Working without event manager
    #==============================================================================

    #---------------------------------------------------
    def test_noevents_one_stim_onset_time0(self):
        rsvp = self._create_good_rsvp(text=['a'], onset_time=[0], duration=1)
        rsvp.init_for_trial()
        self.assertEqual([False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        rsvp.start_showing(10)
        self.assertEqual([True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)
        rsvp.update_rsvp(10.99)
        self.assertEqual([True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)
        rsvp.update_rsvp(11)
        self.assertEqual([False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        rsvp.update_rsvp(20)
        self.assertEqual([False], rsvp.stim_visibility)

    #---------------------------------------------------
    def test_noevents_one_stim_onset_time_gt_0(self):
        rsvp = self._create_good_rsvp(text=['a'], onset_time=[1], duration=1)
        rsvp.init_for_trial()
        rsvp.start_showing(10)
        self.assertEqual([False], rsvp.stim_visibility)
        rsvp.update_rsvp(10.5)
        self.assertEqual([False], rsvp.stim_visibility)
        rsvp.update_rsvp(11)
        self.assertEqual([True], rsvp.stim_visibility)
        rsvp.update_rsvp(11.99)
        self.assertEqual([True], rsvp.stim_visibility)
        rsvp.update_rsvp(12)
        self.assertEqual([False], rsvp.stim_visibility)

    #---------------------------------------------------
    def test_noevents_two_stim_onset_time(self):
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[0, 3], duration=1)

        rsvp.init_for_trial()
        self.assertEqual([False, False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        self.assertEqual(False, rsvp._stimuli[1].visible)

        rsvp.start_showing(10)
        self.assertEqual([True, False], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)
        self.assertEqual(False, rsvp._stimuli[1].visible)

        rsvp.update_rsvp(10.99)
        self.assertEqual([True, False], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)
        self.assertEqual(False, rsvp._stimuli[1].visible)

        rsvp.update_rsvp(11)
        self.assertEqual([False, False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        self.assertEqual(False, rsvp._stimuli[1].visible)

        rsvp.update_rsvp(13)
        self.assertEqual([False, True], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        self.assertEqual(True, rsvp._stimuli[1].visible)

        rsvp.update_rsvp(13.99)
        self.assertEqual([False, True], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        self.assertEqual(True, rsvp._stimuli[1].visible)

        rsvp.update_rsvp(14)
        self.assertEqual([False, False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)
        self.assertEqual(False, rsvp._stimuli[1].visible)


    #---------------------------------------------------
    def test_noevents_last_stim_remains(self):
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[0, 3], duration=1)
        rsvp.last_stimulus_remains = True

        rsvp.init_for_trial()
        rsvp.start_showing(10)
        rsvp.update_rsvp(30)
        self.assertEqual([False, True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[1].visible)


    #---------------------------------------------------
    def test_noevents_cleanup(self):
        rsvp = self._create_good_rsvp(text=['a'], onset_time=[0, 3], duration=1)

        rsvp.init_for_trial()
        rsvp.start_showing(10)
        rsvp.update_rsvp(10.5)

        self.assertEqual(1, len(rsvp._show_hide_operations))  # SHOW was performed; only the HIDE operation remains
        rsvp.update_rsvp(15)
        self.assertEqual(0, len(rsvp._show_hide_operations))  # No operation remained

        rsvp.init_for_trial()
        self.assertEqual(2, len(rsvp._show_hide_operations))  # Both SHOW and HIDE


    #==============================================================================
    #   Working with event manager
    #==============================================================================

    #---------------------------------------------------
    def test_events_one_stim_onset_time0(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a'], onset_time=[0], duration=1)
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        self.assertEqual([False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)

        em.dispatch_event(TRIAL_STARTED, time_in_trial=10, time_in_session=10)
        self.assertEqual([True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)

        em.on_frame(time_in_trial=10.99, time_in_session=10.99)
        self.assertEqual([True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[0].visible)

        em.on_frame(time_in_trial=11, time_in_session=11)
        self.assertEqual([False], rsvp.stim_visibility)
        self.assertEqual(False, rsvp._stimuli[0].visible)

        em.on_frame(time_in_trial=20, time_in_session=20)
        self.assertEqual([False], rsvp.stim_visibility)


    #---------------------------------------------------
    def test_events_one_stim_onset_time_gt_0(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a'], onset_time=[1], duration=1)
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        self.assertEqual([False], rsvp.stim_visibility)

        em.dispatch_event(TRIAL_STARTED, time_in_trial=0, time_in_session=10)
        self.assertEqual([False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=10.99)
        self.assertEqual([False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=11)
        self.assertEqual([True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=11.99)
        self.assertEqual([True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=12)
        self.assertEqual([False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=20)
        self.assertEqual([False], rsvp.stim_visibility)

    #---------------------------------------------------
    def test_events_two_stim_onset_time(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[0, 3], duration=1)
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.dispatch_event(TRIAL_STARTED, time_in_trial=0, time_in_session=10)
        self.assertEqual([True, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=10.99)
        self.assertEqual([True, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=11)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=13)
        self.assertEqual([False, True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=13.99)
        self.assertEqual([False, True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=14)
        self.assertEqual([False, False], rsvp.stim_visibility)

    #---------------------------------------------------
    def test_events_last_stim_remains(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[0, 3], duration=1)
        rsvp.last_stimulus_remains = True
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        em.dispatch_event(TRIAL_STARTED, time_in_trial=0, time_in_session=10)
        em.on_frame(time_in_trial=0, time_in_session=30)
        self.assertEqual([False, True], rsvp.stim_visibility)
        self.assertEqual(True, rsvp._stimuli[1].visible)


    #---------------------------------------------------
    def test_events_simultaneous_events(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[1, 0], duration=2)
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.dispatch_event(TRIAL_STARTED, time_in_trial=0, time_in_session=10)
        self.assertEqual([False, True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=11)
        self.assertEqual([True, True], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=12)
        self.assertEqual([True, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=13)
        self.assertEqual([False, False], rsvp.stim_visibility)


    #---------------------------------------------------
    def test_events_cancel(self):
        em = EventManager()
        em.log_level = em.log_trace
        rsvp = self._create_good_rsvp(text=['a', 'b'], onset_time=[1, 0], duration=2)
        em.register(rsvp)

        em.dispatch_event(TRIAL_INITIALIZED, time_in_trial=1, time_in_session=1)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.dispatch_event(TRIAL_STARTED, time_in_trial=0, time_in_session=10)
        self.assertEqual([False, True], rsvp.stim_visibility)

        em.dispatch_event(TRIAL_SUCCEEDED, time_in_trial=0, time_in_session=10.5)

        em.on_frame(time_in_trial=0, time_in_session=11)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=12)
        self.assertEqual([False, False], rsvp.stim_visibility)

        em.on_frame(time_in_trial=0, time_in_session=13)
        self.assertEqual([False, False], rsvp.stim_visibility)



if __name__ == '__main__':
    unittest.main()
