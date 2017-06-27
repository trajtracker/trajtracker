"""

Trajectory Tracker: track mouse/finger movement

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan

This file is part of TrajTracker.

TrajTracker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TrajTracker is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with TrajTracker.  If not, see <http://www.gnu.org/licenses/>.
"""

import numbers

import expyriment

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.misc import EnabledDisabledObj


# noinspection PyAttributeOutsideInit,PyProtectedMember
class TrajectoryTracker(ttrk.TTrkObject, EnabledDisabledObj):


    #----------------------------------------------------
    def __init__(self, filename=None, enabled=False, track_if_no_movement=False):
        """
        Constructor - invoked when you create a new object by writing TrajectoryTracker()

        :param filename: The file to which the trajectory information will be saved (CSV).
        :param enabled: See :attr:`~trajtracker.movement.TrajectoryTracker.enabled`
        :param track_if_no_movement: See :attr:`~trajtracker.movement.TrajectoryTracker.track_if_no_movement`
        """
        ttrk.TTrkObject.__init__(self)
        EnabledDisabledObj.__init__(self, enabled=enabled)

        self.reset()
        self._filename = filename
        self._out_file_initialized = False
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

        self._log_func_enters("reset", [time0])

        self._trajectory = dict(x=[], y=[], time=[])
        self._last_coord = None


    #----------------------------------------------------
    def update_xyt(self, position, time_in_trial, time_in_session=None):
        """
        Track a point. If tracking is currently inactive, this function will do nothing.
        
        :param time_in_session: ignored
        """

        if not self._enabled:
            return

        _u.update_xyt_validate_and_log(self, position, time_in_trial)
        x_coord, y_coord = position

        if not self._track_if_no_movement and len(self._trajectory['x']) > 0 and  \
            self._trajectory['x'][-1] == x_coord and \
                self._trajectory['y'][-1] == y_coord:
            return

        self._trajectory['x'].append(x_coord)
        self._trajectory['y'].append(y_coord)
        self._trajectory['time'].append(time_in_trial)

        if self._should_log(ttrk.log_trace):
            self._log_write("Track trajectory: pos=({:},{:}), time={:}".format(x_coord, y_coord, time_in_trial), True)

        return None


    #----------------------------------------------------
    def get_xyt(self):
        """
        Get a list of (x,y,time) tuples - one per tracked point
        """
        trj = self._trajectory
        return list(zip(trj['x'], trj['y'], trj['time']))


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
            raise ttrk.ValueError("filename was not provided to {:}.init_output_file()".format(_u.get_type_name(self)))

        self._xy_precision = xy_precision
        self._time_precision = time_precision

        fh = self._open_file(self._filename, 'w')
        fh.write('trial,time,x,y\n')
        fh.close()

        self._out_file_initialized = True

        self._log_write_if(ttrk.log_debug, "Initializing output file %s" % self._filename, True)

    #----------------------------------------------------
    def save_to_file(self, trial_num):
        """
        Save the tracked trajectory (ever since the last reset() call) to a CSV file

        :param trial_num:
        :return: The number of rows printed to the file
        """
        if not self._out_file_initialized:
            raise ttrk.InvalidStateError('TrajectoryTracker.save_to_file() was called before calling init_output_file()')

        fh = self._open_file(self._filename, 'a')

        rows = self.get_xyt()
        for x, y, t in rows:
            x = ('%d' % x) if isinstance(x, int) else '%.*f' % (self._xy_precision, x)
            y = ('%d' % y) if isinstance(y, int) else '%.*f' % (self._xy_precision, y)
            fh.write("%d,%.*f,%s,%s\n" % (trial_num, self._time_precision, t, x, y))

        fh.close()

        self._log_write_if(ttrk.log_debug, "Saved trial #{:} (with {:} rows) to {:}".format(trial_num, len(rows), self._filename), True)

        return len(rows)

    #----------------------------------------------------
    # Default implementation for opening an output file
    #
    def _open_file(self, filename, mode):
        return open(filename, mode)
