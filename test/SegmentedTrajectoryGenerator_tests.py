import unittest

import numpy as np
import trajtracker

from trajtracker.movement import SegmentedTrajectoryGenerator, LineTrajectoryGenerator


def uw(xy):
    x = np.round(xy['x']*1000)/1000
    y = np.round(xy['y']*1000)/1000
    return (x, y)



class SegmentedTrajectoryGeneratorTests(unittest.TestCase):

    #todo: test config

    #============================ generate traj ====================

    #--------------------------------------------------------
    def test_generate_simple(self):
        gen = SegmentedTrajectoryGenerator()
        gen.add_segment(LineTrajectoryGenerator((0, 0), (0, 1), 1), 1)
        gen.add_segment(LineTrajectoryGenerator((0, 1), (1, 1), 1), 1)
        gen.add_segment(LineTrajectoryGenerator((1, 1), (1, 0), 1), 1)

        self.assertEqual((0, 0), uw(gen.get_traj_point(0)))
        self.assertEqual((0, 0.3), uw(gen.get_traj_point(0.3)))
        self.assertEqual((0, 1), uw(gen.get_traj_point(1)))
        self.assertEqual((0.3, 1), uw(gen.get_traj_point(1.3)))
        self.assertEqual((1, 1), uw(gen.get_traj_point(2)))
        self.assertEqual((1, 0.7), uw(gen.get_traj_point(2.3)))
        self.assertEqual((1, 0), uw(gen.get_traj_point(3)))
        self.assertEqual((1, 0), uw(gen.get_traj_point(4)))


    #--------------------------------------------------------
    def test_generate_cyclic(self):
        gen = SegmentedTrajectoryGenerator(cyclic=True)
        gen.add_segment(LineTrajectoryGenerator((0, 0), (0, 1), 1), 1)
        gen.add_segment(LineTrajectoryGenerator((0, 1), (1, 1), 1), 1)
        gen.add_segment(LineTrajectoryGenerator((1, 1), (1, 0), 1), 1)

        self.assertEqual((0, 0), uw(gen.get_traj_point(3)))
        self.assertEqual((0, 0.3), uw(gen.get_traj_point(3.3)))
        self.assertEqual((0, 1), uw(gen.get_traj_point(4)))
        self.assertEqual((0.3, 1), uw(gen.get_traj_point(4.3)))
        self.assertEqual((1, 1), uw(gen.get_traj_point(5)))
        self.assertEqual((1, 0.7), uw(gen.get_traj_point(5.3)))
        self.assertEqual((1, 0), uw(gen.get_traj_point(5.9999)))


if __name__ == '__main__':
    unittest.main()
