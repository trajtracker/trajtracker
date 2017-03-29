import unittest


from trajtracker.validators import MovementAngleValidator, ValidationFailed


class DirectionValidatorTestCase(unittest.TestCase):

    #------------------------------------------
    def test_validation_disabled(self):
        val = MovementAngleValidator(1, min_angle=0, max_angle=180, enabled=False)
        val.check_xyt(0, 0, 0)
        self.assertIsNone(val.check_xyt(-1, 0, 1))

    #------------------------------------------
    def test_validation_basic(self):
        val = MovementAngleValidator(1, min_angle=0, max_angle=180)
        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(1, 0, 1))
        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNotNone(val.check_xyt(-1, 0, 1))

    #------------------------------------------
    def test_config(self):
        val = MovementAngleValidator(1)
        self.assertTrue(val.enabled)
        val.enabled = False
        self.assertFalse(val.enabled)

        val.min_angle = 10
        self.assertEqual(10, val.min_angle)
        val.min_angle = -10
        self.assertEqual(350, val.min_angle)
        val.min_angle = 360
        self.assertEqual(0, val.min_angle)

        val.max_angle = 10
        self.assertEqual(10, val.max_angle)
        val.max_angle = -10
        self.assertEqual(350, val.max_angle)
        val.max_angle = 360
        self.assertEqual(0, val.max_angle)

    #------------------------------------------
    def test_invalid_config(self):
        val = MovementAngleValidator(1)

        self.assertSetFails(val, "min_angle", "")
        self.assertSetSucceeds(val, "min_angle", None)
        self.assertSetSucceeds(val, "min_angle", 90000)

        self.assertSetFails(val, "max_angle", "")
        self.assertSetSucceeds(val, "max_angle", None)
        self.assertSetSucceeds(val, "max_angle", 90000)

        self.assertSetFails(val, "enabled", "")
        self.assertSetFails(val, "enabled", 0)
        self.assertSetFails(val, "enabled", None)

        self.assertSetFails(val, "calc_angle_interval", "")
        self.assertSetFails(val, "calc_angle_interval", None)
        self.assertSetFails(val, "calc_angle_interval", -1)
        self.assertSetSucceeds(val, "calc_angle_interval", 0)


    def assertSetFails(self, validator, attr_name, value):
        try:
            setattr(validator, attr_name, value)
            self.fail("Succeeded setting {0} to {1}".format(attr_name, type(value)))
        except(Exception):
            pass

    def assertSetSucceeds(self, validator, attr_name, value):
        try:
            setattr(validator, attr_name, value)
        except(Exception):
            self.fail("Failed setting {0} to {1} ({2})".format(attr_name, type(value), value))

    #------------------------------------------
    def test_range_crosses_zero(self):
        val = MovementAngleValidator(1, min_angle=-45, max_angle=45)

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNotNone(val.check_xyt(1.01, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNotNone(val.check_xyt(-1.01, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(0.99, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(-0.99, 1, 1))

    #------------------------------------------
    def test_min_gt_max(self):
        val = MovementAngleValidator(1, min_angle=45, max_angle=-45)

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(1.01, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(-1.01, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNotNone(val.check_xyt(0.99, 1, 1))

        val.reset()
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNotNone(val.check_xyt(-0.99, 1, 1))

    #------------------------------------------
    # Movement exactly towards min_angle or max_angle - is considered as valid
    def test_threshold_is_valid(self):
        val = MovementAngleValidator(1, min_angle=-45, max_angle=45)
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(1, 1, 1))

        val = MovementAngleValidator(1, min_angle=45, max_angle=-45)
        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(1, 1, 1))

    #------------------------------------------
    def test_movement_continues(self):
        val = MovementAngleValidator(1, min_angle=-45, max_angle=45)

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(0, 1, 1))
        self.assertIsNotNone(val.check_xyt(1.01, 2, 1))

    #------------------------------------------
    def test_grace(self):
        val = MovementAngleValidator(1, min_angle=-45, max_angle=45, grace_period=1)

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(0, -1, 1))  # in grace period
        self.assertIsNotNone(val.check_xyt(0, -2, 1.01))   # Now we get the error

    #------------------------------------------
    def test_min_distance(self):
        val = MovementAngleValidator(1, min_angle=-45, max_angle=45)
        val.calc_angle_interval = 1.5

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(0, -1, 0.1))  # Too close to calculate direction

        self.assertIsNotNone(val.check_xyt(0, -2, 0.2))   # Now we get the error

        self.assertIsNone(val.check_xyt(0, 1, 0.3))   # Moving back in a valid direction

    #------------------------------------------
    def test_units_per_mm(self):
        val = MovementAngleValidator(2, min_angle=-45, max_angle=45)
        val.calc_angle_interval = 1

        self.assertIsNone(val.check_xyt(0, 0, 0))
        self.assertIsNone(val.check_xyt(1.98, 0, 0.1))  # Too close to calculate direction: 1.98 units = 0.99 mm
        self.assertIsNotNone(val.check_xyt(2.02, 0, 0.2))  # Far enough




if __name__ == '__main__':
    unittest.main()
