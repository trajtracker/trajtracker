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
from trajtracker.misc import EnabledDisabledObj


# noinspection PyAttributeOutsideInit,PyProtectedMember
class TrajectoryTracker(trajtracker._TTrkObject, EnabledDisabledObj):


    #----------------------------------------------------
    def __init__(self, filename=None, enabled=False, track_if_no_movement=False):
        """
        Constructor - invoked when you create a new object by writing TrajectoryTracker()

        :param filename: The file to which the trajectory information will be saved (CSV).
        :param enabled: See :attr:`~trajtracker.movement.TrajectoryTracker.enabled`
        :param track_if_no_movement: See :attr:`~trajtracker.movement.TrajectoryTracker.track_if_no_movement`
        """
        trajtracker._TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        self.reset()
        self._filename = filename
        self.enabled = enabled
        self.track_if_no_movement = track_if_no_movement


    #==============================================================================
    #    Properties
    #==============================================================================

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
        self._log_property_changed("track_if_no_movement")


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
    def update_xyt(self, x_coord, y_coord, time_in_trial):
        """
        Track a point. If tracking is currently inactive, this function will do nothing.
        """

        if not self._enabled:
            return

        _u.validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time_in_trial, numbers.Number)
        _u.validate_func_arg_not_negative(self, "update_xyt", "time_in_trial", time_in_trial)

        if not self._track_if_no_movement and len(self._trajectory['x']) > 0 and  \
            self._trajectory['x'][-1] == x_coord and \
                self._trajectory['y'][-1] == y_coord:
            return

        self._trajectory['x'].append(x_coord)
        self._trajectory['y'].append(y_coord)
        self._trajectory['time'].append(time_in_trial)

        if self._log_level:
            self._log_write("Trajectory,Track_xyt,{0},{1},{2}".format(x_coord, y_coord, time_in_trial))

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
