import unittest

import trajtracker as ttrk
from trajtracker.movement import CustomTrajectoryGenerator


class CustomTrajectoryGeneratorTests(unittest.TestCase):

    #==========================================================================
    # Configure
    #==========================================================================

    #----------------------------------------------------------
    def test_create_empty(self):
        CustomTrajectoryGenerator()


    #----------------------------------------------------------
    def test_set_cyclic(self):
        gen = CustomTrajectoryGenerator()
        gen.cyclic = True

        self.assertRaises(ttrk.TypeError, lambda: CustomTrajectoryGenerator(cyclic=1))
        self.assertRaises(ttrk.TypeError, lambda: CustomTrajectoryGenerator(cyclic=None))


    #----------------------------------------------------------
    def test_set_interpolate(self):
        gen = CustomTrajectoryGenerator()
        gen.interpolate = True

        self.assertRaises(ttrk.TypeError, lambda: CustomTrajectoryGenerator(interpolate=1))
        self.assertRaises(ttrk.TypeError, lambda: CustomTrajectoryGenerator(interpolate=None))

    #----------------------------------------------------------
    def test_set_good_trajectory(self):
        gen = CustomTrajectoryGenerator()
        gen.set_trajectory(1, [(1, 0, 0, True)])
        gen.set_trajectory(2, [(0, 0, 0), (0.5, 0, 0)])

    #----------------------------------------------------------
    def test_set_active_traj(self):
        gen = CustomTrajectoryGenerator()
        gen.set_trajectory(1, [(1, 0, 0, True)])
        gen.set_trajectory(2, [(0, 0, 0), (1, 0, 0)])
        gen.active_traj_id = 1
        self.assertEqual(1, gen.active_traj_id)
        gen.active_traj_id = None

        try:
            gen.active_traj_id = 3
            self.fail()
        except ttrk.ValueError:
            pass


    #----------------------------------------------------------
    def test_set_empty_traj(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, []))

    #----------------------------------------------------------
    def test_set_traj_invalid_time_point(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [""]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(1, 2)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(1, 2, 3, 4, 5)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(None, 0, 0)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [("", 0, 0)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, 0.1, 0)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, None, 0)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0.1)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, 0, None)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0, None)]))
        self.assertRaises(ttrk.TypeError, lambda: gen.set_trajectory(1, [(0, 0, 0, 1)]))


    #----------------------------------------------------------
    def test_set_unordered_time_points(self):
        gen = CustomTrajectoryGenerator()
        self.assertRaises(ttrk.ValueError, lambda: gen.set_trajectory(1, [(1, 0, 0), (1, 0, 0)]))
        self.assertRaises(ttrk.ValueError, lambda: gen.set_trajectory(1, [(1, 0, 0), (0.5, 0, 0)]))


    #==========================================================================
    # Get trajectory data
    #==========================================================================

    #----------------------------------------------------------
    def test_get_traj_data_no_interpolate(self):

        gen = CustomTrajectoryGenerator(interpolate=False)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 1, 2, False), (2, 2, 3, True), (3, 3, 4, False)])

        pt = gen.get_traj_point(2)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.3)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.6)
        self.assertEqual(2, pt[0])
        self.assertEqual(3, pt[1])
        self.assertEqual(True, pt[2])


    #----------------------------------------------------------
    def test_get_traj_data_interpolate(self):

        gen = CustomTrajectoryGenerator(interpolate=True)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 10, 20, False), (2, 20, 30, True), (3, 30, 40, False)])

        pt = gen.get_traj_point(2)
        self.assertEqual(20, pt[0])
        self.assertEqual(30, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.33)
        self.assertEqual(23, pt[0])
        self.assertEqual(33, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.66)
        self.assertEqual(27, pt[0])
        self.assertEqual(37, pt[1])
        self.assertEqual(False, pt[2])

    #----------------------------------------------------------
    def test_time_does_not_start_at_0(self):

        gen = CustomTrajectoryGenerator(interpolate=False)
        gen.set_trajectory(1, [(1, 1, 2, False), (2, 2, 3, True)])

        gen.validate()

        gen.cyclic = True

        self.assertRaises(ttrk.ValueError, lambda: gen.validate())
        self.assertRaises(ttrk.ValueError, lambda: gen.get_traj_point(0.5))
        gen._validation_err = None
        self.assertRaises(ttrk.ValueError, lambda: gen.get_traj_point(0.5))

        gen.cyclic = False
        gen.validate()


    #----------------------------------------------------------
    def test_get_traj_data_cyclic(self):

        gen = CustomTrajectoryGenerator(interpolate=True, cyclic=True)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 10, 20, False), (2, 20, 30, True)])

        pt = gen.get_traj_point(1)
        self.assertEqual(10, pt[0])
        self.assertEqual(20, pt[1])
        self.assertEqual(False, pt[2])

        pt = gen.get_traj_point(2)
        self.assertEqual(20, pt[0])
        self.assertEqual(30, pt[1])
        self.assertEqual(True, pt[2])

        pt = gen.get_traj_point(2.4)
        self.assertEqual(4, pt[0])
        self.assertEqual(9, pt[1])
        self.assertEqual(True, pt[2])


    #----------------------------------------------------------
    def test_get_traj_data_noncyclic_too_large(self):

        gen = CustomTrajectoryGenerator(interpolate=True)
        gen.set_trajectory(1, [(0, 0, 1, True), (1, 10, 20, False)])

        pt = gen.get_traj_point(8.5)
        self.assertEqual(10, pt[0])
        self.assertEqual(20, pt[1])
        self.assertEqual(False, pt[2])


    #==========================================================================
    # Load from file
    #==========================================================================

    #----------------------------------------------------------
    def test_load_from_csv_one_traj(self):

        gen = CustomTrajectoryGeneratorDbg(['time', 'x', 'y'], [(0, 0, 1), (0.5, 1, 2)])
        gen.load_from_csv("nothing")

        gen.active_traj_id = 1

        self.assertEqual((0, 1, True), gen.get_traj_point(0))
        self.assertEqual((1, 2, True), gen.get_traj_point(0.5))

    #----------------------------------------------------------
    def test_load_from_csv_multiple_traj(self):

        filedata = [(1, 0, 0, 1), (1, 0.5, 1, 2),
                    (2, 0, 10, 11), (2, 0.5, 11, 12)]
        gen = CustomTrajectoryGeneratorDbg(['traj_id', 'time', 'x', 'y'], filedata)
        gen.load_from_csv("nothing")

        gen.active_traj_id = '1'
        self.assertEqual((0, 1, True), gen.get_traj_point(0))
        self.assertEqual((1, 2, True), gen.get_traj_point(0.5))

        gen.active_traj_id = '2'
        self.assertEqual((10, 11, True), gen.get_traj_point(0))
        self.assertEqual((11, 12, True), gen.get_traj_point(0.5))


    #----------------------------------------------------------
    def test_load_from_csv_cast_traj_id(self):

        filedata = [(1, 0, 0, 1), (1, 0.5, 1, 2)]

        gen = CustomTrajectoryGeneratorDbg(['traj_id', 'time', 'x', 'y'], filedata)
        gen.load_from_csv("nothing")
        gen.active_traj_id = '1'

        gen = CustomTrajectoryGeneratorDbg(['traj_id', 'time', 'x', 'y'], filedata)
        gen.load_from_csv("nothing", id_type=int)
        gen.active_traj_id = 1

        gen = CustomTrajectoryGeneratorDbg(['traj_id', 'time', 'x', 'y'], [('True', 0, 0, 1)])
        gen.load_from_csv("nothing", id_type=bool)
        gen.active_traj_id = True


    #----------------------------------------------------------
    def test_load_from_csv_invalid_traj_order(self):

        filedata = [(1, 0, 0, 1), (2, 0.5, 1, 2),
                    (3, 0, 10, 11), (1, 0.5, 11, 12)]
        gen = CustomTrajectoryGeneratorDbg(['traj_id', 'time', 'x', 'y'], filedata)
        self.assertRaises(ttrk.BadFormatError, lambda: gen.load_from_csv("nothing"))



#==========================================================================
# Helper class - allows loading from a virtual CSV file
#
class CustomTrajectoryGeneratorDbg(CustomTrajectoryGenerator):

    def __init__(self, fieldnames, file_contents, cyclic=False, interpolate=True):
        super(CustomTrajectoryGeneratorDbg, self).__init__(cyclic, interpolate)
        self._fieldnames = fieldnames
        self._file_contents = file_contents


    def _open_and_get_reader(self, filename):

        rows = []
        for line in self._file_contents:
            row = dict([(self._fieldnames[i], line[i]) for i in range(len(self._fieldnames))])
            rows.append(row)

        return self, self.MyReader(self._fieldnames, rows)


    def close(self):
        pass


    class MyReader(object):

        def __init__(self, fieldnames, rows):
            self.fieldnames = fieldnames
            self._rows = rows

        def __iter__(self):
            return self._rows.__iter__()



if __name__ == '__main__':
    unittest.main()
