from __future__ import division

import unittest
import numpy as np
import xml.etree.ElementTree as ET

import trajtracker
from trajtracker.validators import GlobalSpeedValidator, ValidationAxis, ValidationFailed
from ttrk_testing import DummyStimulus


class GlobalSpeedValidatorTests(unittest.TestCase):

    #=================================================================================
    #             Configure
    #=================================================================================

    #--------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_enabled(self):
        GlobalSpeedValidator()
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(enabled=None))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(enabled=1))


    #--------------------------------------------------
    def test_set_axis(self):
        GlobalSpeedValidator(axis=ValidationAxis.x)
        GlobalSpeedValidator(axis=ValidationAxis.y)
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(axis=ValidationAxis.xy))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(axis=""))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(axis=None))

    #--------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_origin_coord(self):
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(origin_coord=""))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(origin_coord=(1,2)))

        v = GlobalSpeedValidator(origin_coord=1)

        try:
            v.origin_coord = None
            self.fail()
        except TypeError:
            pass

    #--------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_end_coord(self):
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(end_coord=""))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(end_coord=(1,2)))

        v = GlobalSpeedValidator(end_coord=1)

        try:
            v.end_coord = None
            self.fail()
        except TypeError:
            pass

    #--------------------------------------------------
    def test_set_grace_period(self):
        GlobalSpeedValidator(grace_period=1)
        GlobalSpeedValidator(grace_period=0)
        GlobalSpeedValidator(grace_period=None)
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(grace_period=-1))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(grace_period=""))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(grace_period=(1,2)))

    #--------------------------------------------------
    def test_set_max_trial_duration(self):
        GlobalSpeedValidator(max_trial_duration=1)
        GlobalSpeedValidator(max_trial_duration=None)
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(max_trial_duration=0))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(max_trial_duration=""))

    #--------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_show_guide(self):
        GlobalSpeedValidator(show_guide=True)
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(show_guide=1))
        self.assertRaises(TypeError, lambda: GlobalSpeedValidator(show_guide=None))

    #--------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_guide_warning_time_delta(self):
        v = GlobalSpeedValidator()
        v.guide_warning_time_delta = 1
        v.guide_warning_time_delta = 0

        try:
            v.guide_warning_time_delta = None
            self.fail()
        except TypeError:
            pass

        try:
            v.guide_warning_time_delta = ""
            self.fail()
        except TypeError:
            pass

        try:
            v.guide_warning_time_delta = -1
            self.fail()
        except ValueError:
            pass

    # --------------------------------------------------
    # noinspection PyTypeChecker
    def test_set_milestones(self):
        GlobalSpeedValidator(milestones=None)
        GlobalSpeedValidator(milestones=[GlobalSpeedValidator.Milestone(1, 1)])
        GlobalSpeedValidator(
            milestones=[GlobalSpeedValidator.Milestone(.5, .3), GlobalSpeedValidator.Milestone(.5, .7)])

        #-- milestone bounds can't reach 0 or 1
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(.6, 1.01)]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(1.01, .6)]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(.5, 0)]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(0, .5)]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(.5, .5), (.51, .5)]))
        self.assertRaises(ValueError, lambda: GlobalSpeedValidator(milestones=[(.5, .5), (.5, .51)]))

        #-- milestones must progress
        self.assertRaises(ValueError, lambda:
                    GlobalSpeedValidator(
                        milestones=[GlobalSpeedValidator.Milestone(.2, .2), GlobalSpeedValidator.Milestone(.2, .5)]))
        self.assertRaises(ValueError, lambda:
                    GlobalSpeedValidator(
                        milestones=[GlobalSpeedValidator.Milestone(.2, .2), GlobalSpeedValidator.Milestone(.1, .5)]))
        self.assertRaises(ValueError, lambda:
                    GlobalSpeedValidator(
                        milestones=[GlobalSpeedValidator.Milestone(.2, .2), GlobalSpeedValidator.Milestone(.5, .2)]))
        self.assertRaises(ValueError, lambda:
                    GlobalSpeedValidator(
                        milestones=[GlobalSpeedValidator.Milestone(.2, .2), GlobalSpeedValidator.Milestone(.5, .1)]))


    #--------------------------------------------------
    def test_config_from_xml(self):

        v = GlobalSpeedValidator()
        configer = trajtracker.data.XmlConfigUpdater()
        xml = ET.fromstring('''
        <config axis="y" origin_coord="5" end_coord="10" grace_period="0.5" max_trial_duration="3"
                guide_warning_time_delta="0.2">
            <milestones>
                <milestone time="0.5" distance="0.3"/>
                <milestone time="0.5" distance="0.7"/>
            </milestones>
        </config>
        ''')
        configer.configure_object(xml, v)
        self.assertEqual(ValidationAxis.y, v.axis)
        self.assertEqual(5, v.origin_coord)
        self.assertEqual(10, v.end_coord)
        self.assertEqual(0.5, v.grace_period)
        self.assertEqual(3, v.max_trial_duration)
        self.assertEqual(0.2, v.guide_warning_time_delta)
        self.assertEqual(2, len(v.milestones))
        self.assertEqual(0.5, v.milestones[0].time_percentage)
        self.assertEqual(0.3, v.milestones[0].distance_percentage)
        self.assertEqual(0.5, v.milestones[1].time_percentage)
        self.assertEqual(0.7, v.milestones[1].distance_percentage)


    #=================================================================================
    #             Validate
    #=================================================================================

    #--------------------------------------------------
    def test_validate_uninitialized(self):
        v = GlobalSpeedValidator(origin_coord=0, end_coord=100)
        self.assertRaises(trajtracker.InvalidStateError, lambda: v.check_xyt(0, 0, 0))

        v = GlobalSpeedValidator(max_trial_duration=1, end_coord=100)
        self.assertRaises(trajtracker.InvalidStateError, lambda: v.check_xyt(0, 0, 0))

        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0)
        self.assertRaises(trajtracker.InvalidStateError, lambda: v.check_xyt(0, 0, 0))


    #--------------------------------------------------
    def test_validate_one_milestone(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100)

        self.assertEqual(0, v.get_expected_coord_at_time(0))
        self.assertEqual(10, v.get_expected_coord_at_time(.1))
        self.assertEqual(80, v.get_expected_coord_at_time(.8))
        self.assertEqual(100, v.get_expected_coord_at_time(1))
        self.assertEqual(100, v.get_expected_coord_at_time(9))

        v.reset()
        self.assertIsNone(v.check_xyt(0, 50, .5))
        self.assertIsNone(v.check_xyt(0, 100, 1))

        v.reset()
        self.assertIsNotNone(v.check_xyt(0, 49, .5))

        v.reset()
        self.assertIsNotNone(v.check_xyt(0, 99, 1))


    #--------------------------------------------------
    def test_validate_two_milestones(self):
        v = GlobalSpeedValidator(max_trial_duration=6, origin_coord=0, end_coord=100,
                                 milestones=[(.5, .25), (.5, .75)])
        v.reset()
        self.assertIsNone(v.check_xyt(0, 25, 3))
        self.assertIsNone(v.check_xyt(0, 75, 5))
        self.assertIsNone(v.check_xyt(0, 100, 6))

        v.reset()
        self.assertIsNotNone(v.check_xyt(0, 24, 3))
        self.assertIsNotNone(v.check_xyt(0, 74, 5))
        self.assertIsNotNone(v.check_xyt(0, 99, 6))

        self.assertTrue(np.abs(25/3 - v.get_expected_coord_at_time(1)) < .00001)
        self.assertEqual(50, v.get_expected_coord_at_time(4))


    #--------------------------------------------------
    def test_disabled(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100, enabled=False)
        self.assertIsNone(v.check_xyt(0, 49, .5))


    #--------------------------------------------------
    def test_validate_grace_period(self):
        v = GlobalSpeedValidator(max_trial_duration=10, origin_coord=0, end_coord=100, grace_period=3)
        v.reset()
        self.assertIsNone(v.check_xyt(0, 1, 2))
        self.assertIsNone(v.check_xyt(0, 1, 3))
        self.assertIsNotNone(v.check_xyt(0, 1, 3.0001))


    #--------------------------------------------------
    def test_validate_move_backwards(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=100, end_coord=0)

        self.assertEqual(100, v.get_expected_coord_at_time(0))
        self.assertEqual(90, v.get_expected_coord_at_time(.1))
        self.assertEqual(20, v.get_expected_coord_at_time(.8))
        self.assertEqual(0, v.get_expected_coord_at_time(1))
        self.assertEqual(0, v.get_expected_coord_at_time(9))

        v.reset()
        self.assertIsNone(v.check_xyt(0, 50, .5))
        self.assertIsNone(v.check_xyt(0, 0, 1))

        v.reset()
        self.assertIsNotNone(v.check_xyt(0, 51, .5))

        v.reset()
        self.assertIsNotNone(v.check_xyt(0, 1, 1))


    #--------------------------------------------------
    def test_validate_x_axis(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100, axis=ValidationAxis.x)
        v.reset()
        self.assertIsNone(v.check_xyt(50, 0, .5))
        self.assertIsNone(v.check_xyt(100, 0, 1))

        v.reset()
        self.assertIsNotNone(v.check_xyt(49, 0, .5))


    #=================================================================================
    #             Guide
    #=================================================================================

    #--------------------------------------------------
    def test_guide_selects_color(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100, show_guide=True, grace_period=.3)
        v.guide_warning_time_delta = .1
        v._guide = DbgGlobalSpeedGuide(v)

        v.reset()

        v.check_xyt(0, 1, .2)
        self.assertEqual(v.guide.LineMode.Grace, v.guide._guide_line.selected_key)

        v.check_xyt(0, 1, .3)
        self.assertEqual(v.guide.LineMode.Grace, v.guide._guide_line.selected_key)

        v.check_xyt(0, 61, .5)
        self.assertEqual(v.guide.LineMode.OK, v.guide._guide_line.selected_key)

        v.check_xyt(0, 55, .5)
        self.assertEqual(v.guide.LineMode.Error, v.guide._guide_line.selected_key)


    #--------------------------------------------------
    def test_guide_coords_y(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100, show_guide=True)
        v._guide = DbgGlobalSpeedGuide(v)

        v.reset()
        v.check_xyt(0, 99, .5)
        self.assertEqual((0, 50), v.guide._guide_line.active_stimulus.position)

    #--------------------------------------------------
    def test_guide_coords_x(self):
        v = GlobalSpeedValidator(max_trial_duration=1, origin_coord=0, end_coord=100, show_guide=True, axis=ValidationAxis.x)
        v._guide = DbgGlobalSpeedGuide(v)

        v.reset()
        v.check_xyt(99, 0, .5)
        self.assertEqual((50, 0), v.guide._guide_line.active_stimulus.position)




class DbgGlobalSpeedGuide(trajtracker.validators.GlobalSpeedGuide):

    def __init__(self, validator):
        super(DbgGlobalSpeedGuide, self).__init__(validator)

    #--------------------------------------------------
    def _get_line_length(self):
        return 100

    def _create_line(self, start_pt, end_pt, color):
        return DummyStimulus()


if __name__ == '__main__':
    unittest.main()
