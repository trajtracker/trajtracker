"""

 The starting point for finger/mouse movement

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers
from enum import Enum

import trajtracker
import trajtracker.utils as u
import trajtracker._utils as _u
from trajtracker.misc import nvshapes


class StartPoint(trajtracker._TTrkObject):

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
            raise trajtracker.ValueError("invalid start_area provided to {:}.__init__".format(type(self).__name__))

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
        ("above" = -45 degrees to 45 degrees; the others accordingly),
        """
        return self._exit_area


    @exit_area.setter
    def exit_area(self, value):
        if isinstance(value, str):
            self._exit_area = self._create_default_exit_area(value)
            self._log_property_changed("exit_area", value=value)
        elif "overlapping_with_position" in dir(value):
            self._exit_area = value
            self._log_property_changed("exit_area", value="shape")
        else:
            raise trajtracker.ValueError("invalid value for %s.exit_area" % type(self).__name__)

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
            raise trajtracker.ValueError("unsupported exit area '%s'" % name)

        return nvshapes.Sector(self._start_area.position[0], self._start_area.position[1], 10000, f, t)


    #==========================================================================
    #   Runtime API
    #==========================================================================


    #-----------------------------------------------------------------
    def reset(self):
        """
        Reset this object. This method should be called when the trial is initialized.
        """
        self._log_func_enters("reset")
        self._state = self.State.reset
        self._last_checked_coords = (None, None)


    #-----------------------------------------------------------------
    def check_xy(self, x_coord, y_coord):
        """
        Check whether the new finger coordinates imply starting a trial

        :return: bool - whether the state was changed 
        """

        #todo write somewhere:
        #State.init - if the finger/mouse touched in the start area for the first time
        #State.start - if the finger/mouse left the start area in a valid way (into the exit area)
        #State.error - if the finger/mouse left the start area in an invalid way (not to the exit area)

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

        elif self._state == self.State.mouse_up:
            # Trial not initialized yet, the mouse/finger was last observed unclicked:
            # waiting for a touch inside start_area
            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                self._state = self.State.init
                if self._should_log(self.log_info):
                    self._log_write("touched in start area: ({:},{:}). Setting state=init".format(x_coord, y_coord), True)
                self._log_func_returns("check_xy", True)
                return True
            else:
                self._log_func_returns("check_xy", False)
                return False

        elif self._state == self.State.init:
            #-- Trial initialized but not started: waiting for a touch outside start_area

            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                # still in the start area
                self._log_func_returns("check_xy", False)
                if self._should_log(self.log_debug):
                    self._log_write("still in start area: ({:},{:})".format(x_coord, y_coord), True)
                return False

            elif self._exit_area.overlapping_with_position((x_coord, y_coord)):
                # Left the start area into the exit area
                if self._should_log(self.log_info):
                    self._log_write("touched in exit area: ({:},{:}). Setting state=start".format(x_coord, y_coord), True)
                self._state = self.State.start

            else:
                # Left the start area into another (invalid) area
                if self._should_log(self.log_info):
                    self._log_write("touched in invalid area: ({:},{:}). Setting state=error".format(x_coord, y_coord), True)
                self._state = self.State.error

            self._log_func_returns("check_xy", True)
            return True

        self._log_func_returns("check_xy", False)
        return False



    #-----------------------------------------------------------------
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
        :return: True if touched the start area, False if max_wait_time expired
        """

        self._log_func_enters("wait_until_startpoint_touched",
                              ["exp", on_loop_callback, on_loop_present, event_manager])

        _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time, numbers.Number, none_allowed=True)
        _u.validate_func_arg_not_negative(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time)
        if event_manager is not None:
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "trial_start_time", trial_start_time, numbers.Number)
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "session_start_time", session_start_time, numbers.Number)

        if self._state != StartPoint.State.reset:
            raise trajtracker.InvalidStateError(
                "{:}.wait_until_startpoint_touched() was called without calling reset() first".format(_u.get_type_name(self)))

        time_started_waiting = u.get_time()

        # The "StartPoint" object is expected to run through these states, in this order:
        # State.reset - after the trial initialized
        # State.mouse_up - after the mouse/finger was unclicked/lifted
        # State.init - when the screen was touched/clicked (this is when this function returns)

        while True:

            if not exp.mouse.check_button_pressed(0) and self._state == StartPoint.State.reset:
                # Mouse/finger is UP
                self._state = StartPoint.State.mouse_up
                if self._should_log(self.log_info):
                    self._log_write("Mouse unclicked. Setting state=mouse_up", True)

            elif exp.mouse.check_button_pressed(0) and self._state == StartPoint.State.mouse_up:
                # Mouse/finger touched the screen
                finger_pos = exp.mouse.position
                self.check_xy(finger_pos[0], finger_pos[1])

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._log_func_returns("wait_until_startpoint_touched", False)
                return False

            if self._state == StartPoint.State.init:
                break  # Screen touched - we're done here

            # Invoke custom operations on each loop iteration

            if on_loop_callback is not None:
                retval = on_loop_callback()
                if retval is not None:
                    return retval

            if event_manager is not None:
                curr_time = u.get_time()
                event_manager.on_frame(curr_time - trial_start_time, curr_time - session_start_time)

            if on_loop_present is not None:
                on_loop_present.present()

            if on_loop_present is None and on_loop_callback is None:
                exp.clock.wait(15)

        self._log_func_returns("wait_until_startpoint_touched", True)
        return True

    #------------------------------------------------
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
        :param on_loop_callback: A function (without arguments) to call on each loop iteration. 
                                 If the function returns any value other than *None*, the waiting will
                                 be terminated and that value will be returned.
        :param on_loop_present: A visual object that will be present()ed on each loop iteration.
        :param event_manager: The event manager's on_frame() will be called on each loop iteration.
                              If you provide an event manager, you also have to provide trial_start_time and
                              session_start_time (whose values were obtained by :func:`trajtracker.utils.get_time` 
        :param max_wait_time: Maximal time (in seconds) to wait
        :returns: State.start if left the start area in the correct direction; State.error if not; State.aborted if
                  the finger was lifted; State.timeout if max_wait_time has expired
        """

        self._log_func_enters("wait_until_exit", ["exp", on_loop_callback, on_loop_present, event_manager])

        _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time, numbers.Number, none_allowed=True)
        _u.validate_func_arg_not_negative(self, "wait_until_startpoint_touched", "max_wait_time", max_wait_time)
        if event_manager is not None:
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "trial_start_time", trial_start_time, numbers.Number)
            _u.validate_func_arg_type(self, "wait_until_startpoint_touched", "session_start_time", session_start_time, numbers.Number)

        if not exp.mouse.check_button_pressed(0):
            # -- Finger lifted
            self._log_func_returns("wait_until_exit", self.State.aborted)
            self._state = StartPoint.State.aborted
            return self.State.aborted

        #-- Wait
        time_started_waiting = u.get_time()

        while self._state not in [StartPoint.State.start, StartPoint.State.error]:

            if exp.mouse.check_button_pressed(0):
                #-- Finger still touching screen
                finger_pos = exp.mouse.position
                self.check_xy(finger_pos[0], finger_pos[1])
            else:
                #-- Finger lifted
                self._log_func_returns("wait_until_exit", self.State.aborted)
                self._state = StartPoint.State.aborted
                return self.State.aborted

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._state = StartPoint.State.timeout
                self._log_func_returns("wait_until_exit", self.State.timeout)
                return self.State.timeout

            # Invoke custom operations on each loop iteration
            if on_loop_callback is not None:
                retval = on_loop_callback()
                if retval is not None:
                    return retval

            if event_manager is not None:
                curr_time = u.get_time()
                event_manager.on_frame(curr_time - trial_start_time, curr_time - session_start_time)

            if on_loop_present is not None:
                on_loop_present.present()

            if on_loop_present is None and on_loop_callback is None:
                exp.clock.wait(15)

        self._log_func_returns("wait_until_exit", self._state)
        return self._state

