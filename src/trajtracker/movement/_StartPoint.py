"""

 The starting point for finger/mouse movement

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

from __future__ import division

import numbers
from enum import Enum

import expyriment as xpy

import trajtracker as ttrk
import trajtracker.utils as u
# noinspection PyProtectedMember
import trajtracker._utils as _u
from trajtracker.misc import nvshapes


class StartPoint(ttrk.TTrkObject):

    default_exit_area_size = 100

    State = Enum("State", "reset mouse_up init start error aborted timeout")


    #-----------------------------------------------------------
    def __init__(self, start_area, exit_area="above"):
        """
        Constructor - invoked when you create a new object by writing StartPoint()

        :param start_area: The area where you must touch/click to initiate a trial.
                           This object must support an overlapping_with_position() method and a "center" property.
                           It can be an expyriment stimulus, a shape from :func:`~trajtracker.misc.nvshapes`,
                           or your own object
        :param exit_area: See :attr:`~trajtracker.misc.RectStartPoint.exit_area`
        """

        super(StartPoint, self).__init__()

        self._log_func_enters("__init__", [start_area, exit_area])

        if "position" not in dir(start_area):
            raise ttrk.ValueError("invalid start_area provided to {:}.__init__".format(_u.get_type_name(self)))

        self._start_area = start_area
        self.exit_area = exit_area

        self.reset()


    #-----------------------------------------------------------
    @property
    def start_area(self):
        return self._start_area

    #-----------------------------------------------------------
    @property
    def exit_area(self):
        """
        After the mouse/finger leaves the start area, it must enter immediately the exit_area in order
        for the trial to start. Otherwise, it would count as an error.
        This object must support the overlapping_with_position() method. It can be
        an expyriment stimulus, a shape from :func:`~trajtracker.misc.nvshapes`, or your own object.
        
        Also, you can use any of the predefined keywords "above", "below", "right" and "left". Each of those
        define a region that is a 90-degrees sector, centered on start_area's center
        ("above" = -45 degrees to 45 degrees; the others accordingly)
        
        Setting exit_area to None means that any exit direction from the start point would be valid. 
        """
        return self._exit_area


    @exit_area.setter
    def exit_area(self, value):
        if value is None:
            self._exit_area = None
        elif isinstance(value, str):
            self._exit_area = self._create_default_exit_area(value)
            self._log_property_changed("exit_area", value=value)
        elif "overlapping_with_position" in dir(value):
            self._exit_area = value
            self._log_property_changed("exit_area", value="shape")
        else:
            raise ttrk.ValueError("invalid value for %s.exit_area" % _u.get_type_name(self))

        self._log_property_changed("exit_area")


    def _create_default_exit_area(self, name):
        name = name.lower()
        if name == "above":
            f, t = -45, 45

        elif name == "right":
            f, t = 45, 135

        elif name == "below":
            f, t = 135, 215

        elif name == "left":
            f, t = 215, -45

        else:
            raise ttrk.ValueError("unsupported exit area '%s'" % name)

        return nvshapes.Sector(self._start_area.position[0], self._start_area.position[1], 10000, f, t)


    #==========================================================================
    #   Runtime API
    #==========================================================================


    #-----------------------------------------------------------------
    @property
    def state(self):
        """
        The current state of starting the trial - a value of the **StartPoint.State** enum
        
        - *State.reset* - The trial was just initialized, finger/mouse did not touch the screen yet
        - *State.mouse_up* - The mouse was unclicked (or finger lifted from the screen) since the trial was initialized.
                             This is to enforce that the subject raises the finger before starting a new trial.
        - *State.init* - The finger touched the screen (or mouse clicked), indicating that the trial started 
        - *State.start* - The finger/mouse left the start area in a valid way (into the exit area) 
        - *State.error* -  The finger/mouse left the start area in an invalid way (not into the exit area)
        - *State.aborted* - The trial was aborted - finger lifted before it started moving 
        - *State.timeout* - The timeout for starting a trial has expired 
        """
        return self._state


    #-----------------------------------------------------------------
    def mark_as_initialized(self):
        """
        Force the StartPoint object into an "init" :attr:`~trajtracker.movement.StartPoint.State`, as if
        it was touched by the mouse/finger. This is useful in case trial initiation was triggered in another way.
        """
        if self._state not in (StartPoint.State.reset, StartPoint.State.mouse_up):
            raise ttrk.InvalidStateError("StartPoint.mark_as_initialized() called but the StartPoint's present state is {:}".
                                         format(self._state))

        self._state = StartPoint.State.init


    #-----------------------------------------------------------------
    def reset(self):
        """
        Reset this object. This method should be called when the trial is initialized.
        """
        self._log_func_enters("reset")
        self._state = StartPoint.State.reset
        self._last_checked_coords = (None, None)


    #-----------------------------------------------------------------
    def check_xy(self, x_coord, y_coord):
        """
        Check whether the new finger coordinates imply starting a trial

        :return: bool - whether the state was changed 
        """

        if x_coord == self._last_checked_coords[0] and y_coord == self._last_checked_coords[1]:
            # save time - don't retest the same coordinates
            return False

        _u.validate_func_arg_type(self, "check_xy", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "check_xy", "y_coord", y_coord, numbers.Number)

        self._log_func_enters("check_xy", [x_coord, y_coord])

        self._last_checked_coords = (x_coord, y_coord)

        if self._state == StartPoint.State.reset:
            # Trial not initialized yet, and finger not touching screen: WTF???
            raise Exception("trajtracker internal error: {:}.check_xy() was called when state=reset".format(
                _u.get_type_name(self)))

        elif self._state == StartPoint.State.mouse_up:
            # Trial not initialized yet, the mouse/finger was last observed unclicked:
            # waiting for a touch inside start_area
            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                self._state = StartPoint.State.init
                self._log_write_if(ttrk.log_debug, "touched in start area: ({:},{:}). Setting state=init".format(x_coord, y_coord), True)
                self._log_func_returns("check_xy", True)
                return True
            else:
                self._log_func_returns("check_xy", False)
                return False

        elif self._state == StartPoint.State.init:
            #-- Trial initialized but not started: waiting for a touch outside start_area

            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                # still in the start area
                self._log_func_returns("check_xy", False)
                self._log_write_if(ttrk.log_debug, "still in start area: ({:},{:})".format(x_coord, y_coord), True)
                return False

            elif self._exit_area is None or self._exit_area.overlapping_with_position((x_coord, y_coord)):
                # Left the start area into the exit area
                self._log_write_if(ttrk.log_debug, "touched in exit area: ({:},{:}). Setting state=start".format(x_coord, y_coord), True)
                self._state = StartPoint.State.start

            else:
                # Left the start area into another (invalid) area
                self._log_write_if(ttrk.log_debug, "touched in invalid area: ({:},{:}). Setting state=error".format(x_coord, y_coord), True)
                self._state = StartPoint.State.error

            self._log_func_returns("check_xy", True)
            return True

        self._log_func_returns("check_xy", False)
        return False


    #-----------------------------------------------------------------
    # noinspection PyIncorrectDocstring
    def wait_until_startpoint_touched(self, exp, on_loop_callback=None, on_loop_present=None,
                                      event_manager=None, trial_start_time=None, session_start_time=None,
                                      max_wait_time=None):
        """
        Wait until the starting point is touched.
        
        The *on_loop_xxx* and *event_manager* parameters define what to do on each iteration of the loop that  
        waits for the area to be touched. 
        If neither on_loop_callback nor on_loop_present are provided, the function will wait for 15 ms 
        on each loop iteration.
        
        If several on_loop parameters are provided, they will be invoked in this order:
        *callback - event manager.on_frame() - present()*.
        
        :param exp: The Expyriment experiment object
        :param on_loop_callback: A function (without arguments) to call on each loop iteration.
                                If the function returns any value other than *None*, the waiting will
                                be terminated and that value will be returned.
        :param on_loop_present: A visual object that will be present()ed on each loop iteration.
        :param event_manager: The event manager's on_frame() will be called on each loop iteration.
                              If you provide an event manager, you also have to provide trial_start_time and
                              session_start_time (whose values were obtained by :func:`trajtracker.utils.get_time`
        :param max_wait_time: Maximal time (in seconds) to wait
        :return: The value returned by the on_loop_callback function (in case it returned anything other than None).
                 Otherwise the function returns None. Use :attr:`~trajtracker.movement.StartPoint.state` to
                 learn about the StartPoint's exit status.
        """

        self._log_func_enters("wait_until_startpoint_touched",
                              ["exp", on_loop_callback, on_loop_present, event_manager])

        _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time, numbers.Number, none_allowed=True)
        _u.validate_func_arg_not_negative(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time)
        if event_manager is not None:
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "trial_start_time", trial_start_time, numbers.Number, none_allowed=True)
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "session_start_time", session_start_time, numbers.Number)

        if self._state != StartPoint.State.reset:
            raise ttrk.InvalidStateError(
                "{:}.wait_until_startpoint_touched() was called without calling reset() first".format(_u.get_type_name(self)))

        time_started_waiting = u.get_time()

        # The "StartPoint" object is expected to run through these states, in this order:
        # State.reset - after the trial initialized
        # State.mouse_up - after the mouse/finger was unclicked/lifted
        # State.init - when the screen was touched/clicked (this is when this function returns)

        while True:

            if not ttrk.env.mouse.check_button_pressed(0) and self._state == StartPoint.State.reset:
                # Mouse/finger is UP
                self._state = StartPoint.State.mouse_up
                self._log_write_if(ttrk.log_debug, "Mouse unclicked. Setting state=mouse_up", True)

            elif ttrk.env.mouse.check_button_pressed(0) and self._state == StartPoint.State.mouse_up:
                # Mouse/finger touched the screen
                finger_pos = ttrk.env.mouse.position
                self.check_xy(finger_pos[0], finger_pos[1])

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._log_func_returns("wait_until_startpoint_touched", False)
                self._state = StartPoint.State.timeout
                return None

            if self._state == StartPoint.State.init:
                break  # Screen touched - we're done here

            # Invoke custom operations on each loop iteration

            if on_loop_callback is not None:
                retval = on_loop_callback()
                if retval is not None:
                    return retval

            if event_manager is not None:
                curr_time = u.get_time()
                event_manager.on_frame(None if trial_start_time is None else curr_time - trial_start_time,
                                       curr_time - session_start_time)

            if on_loop_present is not None:
                on_loop_present.present()

            if on_loop_present is None and on_loop_callback is None:
                exp.clock.wait(15)

            xpy.io.Keyboard.process_control_keys()

        self._log_func_returns("wait_until_startpoint_touched", True)
        return None

    #------------------------------------------------
    # noinspection PyIncorrectDocstring
    def wait_until_exit(self, exp, on_loop_callback=None, on_loop_present=None, event_manager=None,
                        trial_start_time=None, session_start_time=None, max_wait_time=None):
        """
        Wait until the finger leaves the starting area
    
        The *on_loop_xxx* and *event_manager* parameters define what to do on each iteration of the loop that  
        waits for the area to be touched. 
        If neither on_loop_callback nor on_loop_present are provided, the function will wait for 15 ms 
        on each loop iteration.
        
        If several on_loop parameters are provided, they will be invoked in this order:
        *callback - event manager.on_frame() - present()*.
        
        :param exp: The Expyriment experiment object
        :param on_loop_callback: A function to call on each loop iteration. 
                                 If the function returns any value other than *None*, the waiting will
                                 be terminated and that value will be returned.
                                 The function gets 2 arguments: time_in_trial, time_in_session
        :param on_loop_present: A visual object that will be present()ed on each loop iteration.
        :param event_manager: The event manager's on_frame() will be called on each loop iteration.
                              If you provide an event manager, you also have to provide trial_start_time and
                              session_start_time (whose values were obtained by :func:`trajtracker.utils.get_time` 
        :param max_wait_time: Maximal time (in seconds) to wait
        :return: The value returned by the on_loop_callback function (in case it returned anything other than None).
                 Otherwise the function returns None. Use :attr:`~trajtracker.movement.StartPoint.state` to
                 learn about the StartPoint's exit status.
        """

        self._log_func_enters("wait_until_exit", ["exp", on_loop_callback, on_loop_present, event_manager])

        _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time, numbers.Number, none_allowed=True)
        _u.validate_func_arg_not_negative(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time)
        if event_manager is not None:
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "trial_start_time", trial_start_time, numbers.Number, none_allowed=True)
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "session_start_time", session_start_time, numbers.Number)

        time_started_waiting = u.get_time()

        #-- Wait
        while self._state not in [StartPoint.State.start, StartPoint.State.error]:

            curr_time = u.get_time()
            time_in_trial = None if trial_start_time is None else curr_time - trial_start_time
            time_in_session = None if session_start_time is None else curr_time - session_start_time

            if ttrk.env.mouse.check_button_pressed(0):
                #-- Finger still touching screen
                finger_pos = ttrk.env.mouse.position
                self.check_xy(finger_pos[0], finger_pos[1])
            else:
                #-- Finger lifted
                self._log_func_returns("wait_until_exit", StartPoint.State.aborted)
                self._state = StartPoint.State.aborted
                return None

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._state = StartPoint.State.timeout
                self._log_func_returns("wait_until_exit", StartPoint.State.timeout)
                return None

            # Invoke custom operations on each loop iteration
            if on_loop_callback is not None:
                retval = on_loop_callback(time_in_trial, time_in_session)
                if retval is not None:
                    return retval

            if event_manager is not None:
                event_manager.on_frame(time_in_trial, time_in_session)

            if on_loop_present is not None:
                on_loop_present.present()

            if on_loop_present is None and on_loop_callback is None:
                exp.clock.wait(15)

            xpy.io.Keyboard.process_control_keys()

        self._log_func_returns("wait_until_exit", self._state)
        return None
