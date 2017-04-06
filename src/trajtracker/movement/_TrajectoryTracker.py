"""

Trajectory Tracker: track mouse/finger movement

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers

import expyriment

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.data import fromXML


# noinspection PyAttributeOutsideInit,PyProtectedMember
class TrajectoryTracker(trajtracker._TTrkObject):


    #----------------------------------------------------
    def __init__(self, filename=None, tracking_active=False, track_if_no_movement=False):
        """
        Constructor - invoked when you create a new object by writing TrajectoryTracker()

        :param filename: See :attr:`~trajtracker.movement.TrajectoryTracker.filename`
        :param tracking_active: See :attr:`~trajtracker.movement.TrajectoryTracker.tracking_active`
        :param track_if_no_movement: See :attr:`~trajtracker.movement.TrajectoryTracker.track_if_no_movement`
        """
        super(TrajectoryTracker, self).__init__()
        self.reset()
        self._filename = filename
        self.tracking_active = tracking_active
        self.track_if_no_movement = track_if_no_movement


    #==============================================================================
    #    Properties
    #==============================================================================

    #----------------------------------------------------
    @property
    def tracking_active(self):
        """
        Whether tracking is currently active (boolean). When inactive, calls to
        :func:`~trajtracker.movement.TrajectoryTracker.update_xyt` will be ignored.
        """
        return self._tracking_active

    @tracking_active.setter
    @fromXML(bool)
    def tracking_active(self, value):
        _u.validate_attr_type(self, "tracking_active", value, bool)
        self._tracking_active = value
        self._log_setter("tracking_active")


    #----------------------------------------------------
    @property
    def track_if_no_movement(self):
        """
        Whether to record x,y,t if the coordinates did not change
        """
        return self._track_if_no_movement

    @track_if_no_movement.setter
    @fromXML(bool)
    def track_if_no_movement(self, value):
        _u.validate_attr_type(self, "track_if_no_movement", value, bool)
        self._track_if_no_movement = value
        self._log_setter("track_if_no_movement")


    #==============================================================================
    #    Runtime API
    #==============================================================================

    #----------------------------------------------------
    # noinspection PyUnusedLocal
    def reset(self, time0=None):
        """
        Forget any previously-tracked points.

        :param time0: ignored
        """

        self._trajectory = dict(x=[], y=[], time=[])
        self._last_coord = None

        if self._log_level:
            self._log_write("TrajectoryTracker,Reset")

    #----------------------------------------------------
    def update_xyt(self, x_coord, y_coord, time):
        """
        Track a point. If tracking is currently inactive, this function will do nothing.
        """

        if not self._tracking_active:
            return

        _u.validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time, numbers.Number)
        _u.validate_func_arg_not_negative(self, "update_xyt", "time", time)

        if not self._track_if_no_movement and len(self._trajectory['x']) > 0 and  \
            self._trajectory['x'][-1] == x_coord and \
                self._trajectory['y'][-1] == y_coord:
            return

        self._trajectory['x'].append(x_coord)
        self._trajectory['y'].append(y_coord)
        self._trajectory['time'].append(time)

        if self._log_level:
            self._log_write("Trajectory,Track_xyt,{0},{1},{2}".format(x_coord, y_coord, time))

        return None


    #----------------------------------------------------
    def get_xyt(self):
        """
        Get a list of (x,y,time) tuples - one per tracked point
        """
        trj = self._trajectory
        return zip(trj['x'], trj['y'], trj['time'])


    #----------------------------------------------------
    def init_output_file(self, filename=None, xy_precision=5, time_precision=3):
        """
        Initialize a new CSV output file for saving the results

        :param filename: Full path
        :param xy_precision: Precision of x,y coordinates (default: 5)
        :param time_precision: Precision of time (default: 3)
        """
        if filename is not None:
            self._filename = filename

        if self._filename is None:
            raise ValueError("trajtracker error: filename was not provided to {:}.init_output_file()".format(type(self).__name__))

        self._xy_precision = xy_precision
        self._time_precision = time_precision

        fh = self._open_file(self._filename, 'w')
        fh.write('trial,time,x,y\n')
        fh.close()

        if self._log_level:
            self._log_write("Trajectory,InitOutputFile,%s" % self._filename)

    #----------------------------------------------------
    def save_to_file(self, trial_num):
        """
        Save the tracked trajectory (ever since the last reset() call) to a CSV file

        :param trial_num:
        :return: The number of rows printed to the file
        """
        if self._filename is None:
            raise trajtracker.InvalidStateError('TrajectoryTracker.save_to_file() was called before calling init_output_file()')

        fh = self._open_file(self._filename, 'a')

        rows = self.get_xyt()
        for x, y, t in rows:
            x = ('%d' % x) if isinstance(x, int) else '%.*f' % (self._xy_precision, x)
            y = ('%d' % y) if isinstance(y, int) else '%.*f' % (self._xy_precision, y)
            fh.write("%d,%.*f,%s,%s\n" % (trial_num, self._time_precision, t, x, y))

        fh.close()

        if self._log_level:
            self._log_write("Trajectory,SavedTrial,%s,%d,%d" % (self._filename, trial_num, len(rows)))

        return len(rows)

    #----------------------------------------------------
    # Default implementation for opening an output file
    #
    def _open_file(self, filename, mode):
        return open(filename, mode)
