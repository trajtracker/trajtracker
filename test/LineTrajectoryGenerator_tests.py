import unittest

import xml.etree.ElementTree as ET

import trajtracker

from trajtracker.movement import LineTrajectoryGenerator
from expyriment.misc import geometry


def uw(xy):
    return (xy['x'], xy['y'])


class LineTrajectoryGeneratorTests(unittest.TestCase):

    #============================ configure ====================

    #-----------------------------------------------
    def test_create_empty(self):
        LineTrajectoryGenerator()


    #-----------------------------------------------
    def test_set_coords(self):
        LineTrajectoryGenerator(start_point=(0, 0))
        LineTrajectoryGenerator(end_point=(0, 0))

    #-----------------------------------------------
    def test_set_bad_coords(self):
        self.assertRaises(trajtracker.TypeError, lambda: LineTrajectoryGenerator(start_point=""))
        self.assertRaises(trajtracker.TypeError, lambda: LineTrajectoryGenerator(start_point=(1,)))

        self.assertRaises(trajtracker.TypeError, lambda: LineTrajectoryGenerator(end_point=""))
        self.assertRaises(trajtracker.TypeError, lambda: LineTrajectoryGenerator(end_point=(1,)))

        gen = LineTrajectoryGenerator()
        try:
            gen.start_point = None
            self.fail()
        except:
            pass

        try:
            gen.end_point = None
            self.fail()
        except:
            pass

    #-----------------------------------------------
    def test_set_duration(self):
        LineTrajectoryGenerator(duration=3)

    #-----------------------------------------------
    def test_set_bad_duration(self):
        self.assertRaises(trajtracker.TypeError, lambda: LineTrajectoryGenerator(duration=""))
        self.assertRaises(trajtracker.ValueError, lambda: LineTrajectoryGenerator(duration=-1))

        gen = LineTrajectoryGenerator()
        try:
            gen.duration = None
            self.fail()
        except:
            pass

    #-----------------------------------------------
    def test_set_bools(self):
        LineTrajectoryGenerator(cyclic=True, return_to_start=True)


    # --------------------------------------------------
    def test_config_from_xml(self):

        gen = LineTrajectoryGenerator()
        configer = trajtracker.data.XmlConfigUpdater()
        xml = ET.fromstring('<config start_point="(1,1)" end_point="(2,2)" duration="3" cyclic="True" return_to_start="True"/>')
        configer.configure_object(xml, gen)
        self.assertEqual(1, gen.start_point[0])
        self.assertEqual(1, gen.start_point[1])
        self.assertEqual(2, gen.end_point[0])
        self.assertEqual(2, gen.end_point[1])
        self.assertEqual(3, gen.duration)
        self.assertEqual(True, gen.cyclic)
        self.assertEqual(True, gen.return_to_start)



    #============================ generate traj ====================


    #--------------------------------------------------------
    def test_generate_simple(self):
        gen = LineTrajectoryGenerator(start_point=(0,0), end_point=(12,120), duration=2)
        self.assertEqual((0, 0), uw(gen.get_traj_point(0)))
        self.assertEqual((3, 30), uw(gen.get_traj_point(0.5)))
        self.assertEqual((6, 60), uw(gen.get_traj_point(1)))
        self.assertEqual((9, 90), uw(gen.get_traj_point(1.5)))
        self.assertEqual((12, 120), uw(gen.get_traj_point(2)))
        self.assertEqual((12, 120), uw(gen.get_traj_point(3)))
        self.assertEqual((12, 120), uw(gen.get_traj_point(5)))

    #--------------------------------------------------------
    def test_generate_return_to_start(self):
        gen = LineTrajectoryGenerator(start_point=(0,0), end_point=(12,120), duration=2, return_to_start=True)
        self.assertEqual((0, 0), uw(gen.get_traj_point(0)))
        self.assertEqual((6, 60), uw(gen.get_traj_point(1)))
        self.assertEqual((12, 120), uw(gen.get_traj_point(2)))
        self.assertEqual((9, 90), uw(gen.get_traj_point(2.5)))
        self.assertEqual((0, 0), uw(gen.get_traj_point(4)))
        self.assertEqual((0, 0), uw(gen.get_traj_point(5)))

    #--------------------------------------------------------
    def test_generate_cyclic(self):
        gen = LineTrajectoryGenerator(start_point=(0,0), end_point=(12,120), duration=2, cyclic=True)
        self.assertEqual((3, 30), uw(gen.get_traj_point(4.5)))
        self.assertEqual((3, 30), uw(gen.get_traj_point(6.5)))

    #--------------------------------------------------------
    def test_generate_cyclic_return_to_start(self):
        gen = LineTrajectoryGenerator(start_point=(0,0), end_point=(12,120), duration=2, return_to_start=True, cyclic=True)
        self.assertEqual((3, 30), uw(gen.get_traj_point(4.5)))
        self.assertEqual((9, 90), uw(gen.get_traj_point(6.5)))



if __name__ == '__main__':
    unittest.main()
