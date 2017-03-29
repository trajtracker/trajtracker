import unittest



import trajtracker

from trajtracker.movement import CircularTrajectoryGenerator
from expyriment.misc import geometry

def uw(xy):
    return (xy['x'], xy['y'])


class CircularTrajectoryGeneratorTests(unittest.TestCase):

    #============================ configure ====================

    #--------------------------------------------------------
    def test_create_empty(self):
        CircularTrajectoryGenerator()


    #--------------------------------------------------------
    def test_set_center(self):
        self.assertEqual((1,2), CircularTrajectoryGenerator(center=(1,2)).center)
        self.assertEqual((1,2), CircularTrajectoryGenerator(center=geometry.XYPoint(1, 2)).center)

        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(center=0))
        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(center=(1,2,3)))
        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(center=(0.3, 1)))
        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(center=(0, None)))

    #--------------------------------------------------------
    def test_set_degrees_per_sec(self):
        gen = CircularTrajectoryGenerator(degrees_per_sec=180)
        self.assertEqual(180, gen.degrees_per_sec)
        self.assertEqual(2, gen.full_rotation_duration)

        self.assertRaises(ValueError, lambda: CircularTrajectoryGenerator(degrees_per_sec=0))
        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(degrees_per_sec=""))

        try:
            gen.degrees_per_sec = None
            self.fail()
        except TypeError:
            pass


    #--------------------------------------------------------
    def test_set_full_rotation_duration(self):
        gen = CircularTrajectoryGenerator()
        gen.full_rotation_duration = 2
        self.assertEqual(180, gen.degrees_per_sec)
        self.assertEqual(2, gen.full_rotation_duration)

        try:
            gen.full_rotation_duration = 0
            self.fail()
        except ValueError:
            pass

        try:
            gen.full_rotation_duration = None
            self.fail()
        except TypeError:
            pass

        try:
            gen.full_rotation_duration = ""
            self.fail()
        except TypeError:
            pass


    #--------------------------------------------------------
    def test_set_degrees_at_t0(self):
        gen = CircularTrajectoryGenerator(degrees_at_t0=90)
        self.assertEqual(90, gen.degrees_at_t0)

        self.assertRaises(TypeError, lambda: CircularTrajectoryGenerator(degrees_at_t0=""))

    #============================ generate ====================

    #--------------------------------------------------------
    def test_generate_simple(self):

        gen = CircularTrajectoryGenerator(center=(0,0), radius=100, degrees_per_sec=90)
        self.assertEqual((0, 100), uw(gen.get_traj_point(0)))
        self.assertEqual((71, 71), uw(gen.get_traj_point(0.5)))
        self.assertEqual((100, 0), uw(gen.get_traj_point(1)))
        self.assertEqual((71, -71), uw(gen.get_traj_point(1.5)))
        self.assertEqual((0, -100), uw(gen.get_traj_point(2)))
        self.assertEqual((-71, -71), uw(gen.get_traj_point(2.5)))
        self.assertEqual((-100, 0), uw(gen.get_traj_point(3)))
        self.assertEqual((-71, 71), uw(gen.get_traj_point(3.5)))
        self.assertEqual((100, 0), uw(gen.get_traj_point(5)))

    #--------------------------------------------------------
    def test_generate_change_center(self):
        gen = CircularTrajectoryGenerator(center=(10,-10), radius=100, degrees_per_sec=90)
        self.assertEqual((10, 90), uw(gen.get_traj_point(0)))

    #--------------------------------------------------------
    def test_generate_change_angle0(self):
        gen = CircularTrajectoryGenerator(center=(0,0), radius=100, degrees_per_sec=90, degrees_at_t0=90)
        self.assertEqual((100, 0), uw(gen.get_traj_point(0)))

    #--------------------------------------------------------
    def test_generate_change_duration(self):
        gen = CircularTrajectoryGenerator(center=(0,0), radius=100)
        gen.full_rotation_duration = 4
        self.assertEqual((0, -100), uw(gen.get_traj_point(2)))

    #--------------------------------------------------------
    def test_missing_info(self):
        self.assertRaises(trajtracker.InvalidStateError, lambda: CircularTrajectoryGenerator(center=(0, 0), radius=100).get_traj_point(0))
        self.assertRaises(trajtracker.InvalidStateError, lambda: CircularTrajectoryGenerator(center=(0, 0), degrees_per_sec=90).get_traj_point(0))
        self.assertRaises(trajtracker.InvalidStateError, lambda: CircularTrajectoryGenerator(radius=100, degrees_per_sec=90).get_traj_point(0))



if __name__ == '__main__':
    unittest.main()
