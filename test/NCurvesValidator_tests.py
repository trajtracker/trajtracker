import unittest

import xml.etree.ElementTree as ET

import trajtracker
from trajtracker.validators import NCurvesValidator, ExperimentError


class NCurvesValidatorTests(unittest.TestCase):

    #===============================================================
    # Configure
    #===============================================================

    def test_create(self):
        NCurvesValidator()

    def test_set_max_curves_per_trial(self):
        v = NCurvesValidator(max_curves_per_trial=3)
        v.max_curves_per_trial = None

        self.assertRaises(TypeError, lambda: NCurvesValidator(max_curves_per_trial=""))
        self.assertRaises(ValueError, lambda: NCurvesValidator(max_curves_per_trial=-1))

    #--------------------------------------------------
    def test_config_from_xml(self):

        v = NCurvesValidator()
        configer = trajtracker.data.XmlConfigUpdater()
        xml = ET.fromstring('<config max_curves_per_trial="3" min_distance="2.5" min_angle_change_per_curve="10.5"/>')
        configer.configure_object(xml, v)
        self.assertEqual(3, v.max_curves_per_trial)
        self.assertEqual(2.5, v.min_distance)
        self.assertEqual(10.5, v.min_angle_change_per_curve)


    #===============================================================
    # Validate
    #===============================================================

    #-------------------------------------------
    def test_validate(self):
        val = NCurvesValidator(direction_monitor=DirectionMonitorDbg(2), max_curves_per_trial=2)
        self.assertIsNone(val.check_xyt(0, 0, 0))

        val.max_curves_per_trial = 1
        self.assertIsNotNone(val.check_xyt(0, 0, 0))

    #-------------------------------------------
    def test_disabled(self):
        val = NCurvesValidator(direction_monitor=DirectionMonitorDbg(2), max_curves_per_trial=1, enabled=False)
        self.assertIsNone(val.check_xyt(0, 0, 0))



#-----------------------------------------------------------
class DirectionMonitorDbg(object):

    def __init__(self, n_curves):
        self._n_curves = n_curves

    def reset(self):
        pass

    def update_xyt(self, x_coord, y_coord, time):
        pass

    @property
    def n_curves(self):
        return self._n_curves


if __name__ == '__main__':
    unittest.main()
