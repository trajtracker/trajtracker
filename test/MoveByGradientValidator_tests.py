import unittest

import xml.etree.ElementTree as ET

import trajtracker
from trajtracker.validators import MoveByGradientValidator, ValidationFailed

grad = [[(0, 0, i) for i in range(0,100)]]



class MoveByGradientValidatorTests(unittest.TestCase):

    #-------------------------------------------------------
    def test_set_pos(self):
        val = MoveByGradientValidator(grad)

        val.position = (1, 1)
        val.position = (-1, -1)

        try:
            val.position = ""
        except TypeError:
            pass

        try:
            val.position = 1
        except TypeError:
            pass

        try:
            val.position = ("", "")
        except TypeError:
            pass

        try:
            val.position = (0.1, 0)
        except TypeError:
            pass

    #-------------------------------------------------------
    def test_set_enabled(self):
        val = MoveByGradientValidator(grad)

        val.enabled = True

        try:
            val.enabled = 1
        except TypeError:
            pass

        try:
            val.enabled = None
        except TypeError:
            pass


    # -------------------------------------------------------
    def test_set_last_validated_rgb(self):
        val = MoveByGradientValidator(grad)

        val.last_validated_rgb = (0, 0, 50)
        val.last_validated_rgb = 50

        try:
            val.last_validated_rgb = (-1, 0, 50)
        except TypeError:
            pass

        try:
            val.last_validated_rgb = (0, 0, 256)
        except TypeError:
            pass

        try:
            val.last_validated_rgb = (1.5, 0, 50)
        except TypeError:
            pass

        try:
            val.last_validated_rgb = ("", 0, 50)
        except TypeError:
            pass

        try:
            val.last_validated_rgb = (0, 0)
        except TypeError:
            pass

        try:
            val.last_validated_rgb = -1
        except ValueError:
            pass

        try:
            val.last_validated_rgb = 65536
        except ValueError:
            pass

        try:
            val.last_validated_rgb = ""
        except TypeError:
            pass

        try:
            val.last_validated_rgb = None
        except TypeError:
            pass


    # -------------------------------------------------------
    def test_set_max_valid_back_movement(self):
        val = MoveByGradientValidator(grad)

        val.max_valid_back_movement = 0
        val.max_valid_back_movement = 200

        try:
            val.max_valid_back_movement = None
        except TypeError:
            pass

        try:
            val.max_valid_back_movement = -1
        except ValueError:
            pass

        try:
            val.max_valid_back_movement = ""
        except TypeError:
            pass


    # -------------------------------------------------------
    def test_set_rgb_should_ascend(self):
        val = MoveByGradientValidator(grad)
        val.rgb_should_ascend = True

        try:
            val.rgb_should_ascend = 0
        except TypeError:
            pass

        try:
            val.rgb_should_ascend = None
        except TypeError:
            pass

    # --------------------------------------------------
    def test_config_from_xml(self):

        v = MoveByGradientValidator([[]])
        configer = trajtracker.data.XmlConfigUpdater()
        xml = ET.fromstring('''
        <config max_valid_back_movement="0.5" position="(1,2)" rgb_should_ascend="True"
                last_validated_rgb="(0, 0, 100)"/>
        ''')
        configer.configure_object(xml, v)
        self.assertEqual(0.5, v.max_valid_back_movement)
        self.assertEqual((1,2), v.position)
        self.assertEqual(True, v.rgb_should_ascend)
        self.assertEqual(100, v.last_validated_rgb)

    #-------------------------------------------------------
    def test_validate_basic(self):
        val = MoveByGradientValidator(grad)
        self.assertIsNone(val.check_xyt(0, 0))
        self.assertIsNone(val.check_xyt(10, 0))
        self.assertIsNotNone(val.check_xyt(9, 0))


    #-------------------------------------------------------
    def test_validator_disabled(self):
        val = MoveByGradientValidator(grad, enabled=False)
        self.assertIsNone(val.check_xyt(0, 0))
        self.assertIsNone(val.check_xyt(-1, 0))


    #-------------------------------------------------------
    def test_validate_out_of_range(self):
        val = MoveByGradientValidator(grad)
        self.assertIsNone(val.check_xyt(0, 0))
        self.assertIsNone(val.check_xyt(-100, 0))


    #-------------------------------------------------------
    def test_validate_small_back_movement(self):
        val = MoveByGradientValidator(grad)
        val.max_valid_back_movement = 3
        self.assertIsNone(val.check_xyt(0, 0))
        self.assertIsNone(val.check_xyt(-3, 0))
        self.assertIsNotNone(val.check_xyt(-4, 0))


    # -------------------------------------------------------
    def test_validate_descending(self):
        val = MoveByGradientValidator(grad, rgb_should_ascend=False)
        self.assertIsNone(val.check_xyt(0, 0))
        self.assertIsNone(val.check_xyt(-10, 0))
        self.assertIsNotNone(val.check_xyt(-9, 0))


    #-------------------------------------------------------
    def test_validate_cross_zero(self):
        val = MoveByGradientValidator(grad, last_validated_rgb=(0, 0, 90))
        self.assertIsNone(val.check_xyt(0, 0))   # the color here is 50
        self.assertIsNone(val.check_xyt(40, 0))  # the color here is 90
        self.assertIsNone(val.check_xyt(45, 0))  # the color here is 95
        self.assertIsNone(val.check_xyt(-45, 0))  # the color here is 5

        val = MoveByGradientValidator(grad, last_validated_rgb=(0, 0, 90))
        self.assertIsNone(val.check_xyt(0, 0))   # the color here is 50
        self.assertIsNone(val.check_xyt(39, 0))  # the color here is 89
        self.assertIsNotNone(val.check_xyt(-45, 0))



if __name__ == '__main__':
    unittest.main()
