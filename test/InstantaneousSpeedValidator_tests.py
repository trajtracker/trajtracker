import unittest

import xml.etree.ElementTree as ET

import trajtracker


from trajtracker.validators import InstantaneousSpeedValidator, ValidationAxis, ExperimentError



class InstantaneousSpeedValidatorTests(unittest.TestCase):

    #------------------------------------------
    def test_min_speed(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y)
        validator.min_speed = 1

        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((0, 2), 1))
        self.assertIsNone(validator.update_xyt((0, 3), 2))

        e = validator.update_xyt((0, 3.9), 3)
        self.assertIsNotNone(e)
        self.assertEqual(InstantaneousSpeedValidator.err_too_slow, e.err_code)

    #------------------------------------------
    def test_max_speed(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y)
        validator.max_speed = 1

        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((0, 0.5), 1))
        self.assertIsNone(validator.update_xyt((0, 1.5), 2))

        e = validator.update_xyt((0, 2.6), 3)
        self.assertIsNotNone(e)
        self.assertEqual(InstantaneousSpeedValidator.err_too_fast, e.err_code)


    #------------------------------------------
    def test_grace(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y)
        validator.min_speed = 1
        validator.grace_period = 2

        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((0, 1), 2))
        self.assertIsNotNone(validator.update_xyt((0, 2), 4))


    #------------------------------------------
    def test_disabled(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y, enabled=False)
        validator.min_speed = 1

        self.assertIsNone(validator.update_xyt((0, 0), 0))
        validator.enabled = True
        self.assertIsNone(validator.update_xyt((0, 1), 2))
        self.assertIsNotNone(validator.update_xyt((0, 2), 4))


    #------------------------------------------
    def test_reset(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y)
        validator.min_speed = 1

        self.assertIsNone(validator.update_xyt((0, 0), 0))
        validator.reset()
        self.assertIsNone(validator.update_xyt((0, 1), 2))
        self.assertIsNotNone(validator.update_xyt((0, 2), 4))


    #------------------------------------------
    def test_interval(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y)
        validator.min_speed = 1
        validator.calculation_interval = 3
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((0, 1), 2))
        self.assertIsNotNone(validator.update_xyt((0, 2), 4))


    #------------------------------------------
    def test_speed_y(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.y, min_speed=1)
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((0, 1), 1))

        e = validator.update_xyt((1, 1.5), 2)
        self.assertIsNotNone(e)
        self.assertEqual(.5, e.arg(InstantaneousSpeedValidator.arg_speed))


    #------------------------------------------
    def test_speed_x(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.x, min_speed=1)
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((1, 0), 1))

        e = validator.update_xyt((1.5, 1), 2)
        self.assertIsNotNone(e)
        self.assertEqual(.5, e.arg(InstantaneousSpeedValidator.arg_speed))


    #------------------------------------------
    def test_speed_xy(self):
        validator = InstantaneousSpeedValidator(axis=ValidationAxis.xy, min_speed=5)
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNone(validator.update_xyt((3, 4), 1))

        validator.reset()
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNotNone(validator.update_xyt((3, 3.99), 1))

        validator.reset()
        self.assertIsNone(validator.update_xyt((0, 0), 0))
        self.assertIsNotNone(validator.update_xyt((2.99, 4), 1))



if __name__ == '__main__':
    unittest.main()
