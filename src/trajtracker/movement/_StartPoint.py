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

    State = Enum("State", "reset init start error aborted timeout")


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

        if "position" not in dir(start_area):
            raise ValueError("trajtracker error: invalid start_area provided to {:}.__init__".format(type(self).__name__))

        self._start_area = start_area
        self.exit_area = exit_area

        self.reset()


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
            raise ValueError("trajtracker error: invalid value for %s.exit_area" % type(self).__name__)


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
            raise ValueError("trajtracker error: unsupported exit area '%s'" % name)

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


    #-----------------------------------------------------------------
    def check_xy(self, x_coord, y_coord):
        """
        Check whether the new finger coordinates imply starting a trial

        :return: State.init - if the finger/mouse touched in the start area for the first time
                 State.start - if the finger/mouse left the start area in a valid way (into the exit area)
                 State.error - if the finger/mouse left the start area in an invalid way (not to the exit area)
                 None - if the finger/mouse didn't cause any change in the "start" state
        """

        _u.validate_func_arg_type(self, "check_xy", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "check_xy", "y_coord", y_coord, numbers.Number)

        self._log_func_enters("check_xy", [x_coord, y_coord])

        if self._state == self.State.reset:
            #-- Trial not initialized yet: waiting for a touch inside start_area
            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                self._state = self.State.init
                self._log_func_returns(self._state)
                return self._state
            else:
                self._log_func_returns("None")
                return None

        elif self._state == self.State.init:
            #-- Trial initialized but not started: waiting for a touch outside start_area

            if self._start_area.overlapping_with_position((x_coord, y_coord)):
                # still in the start area
                self._log_func_returns("None")
                return None

            elif self._exit_area.overlapping_with_position((x_coord, y_coord)):
                # Left the start area into the exit area
                self._state = self.State.start

            else:
                # Left the start area into another (invalid) area
                self._state = self.State.error

            self._log_func_returns(self._state)
            return self._state

        self._log_func_returns("None")

        return None



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

        time_started_waiting = u.get_time()

        state = StartPoint.State.reset
        while state != StartPoint.State.init:

            if exp.mouse.check_button_pressed(0):
                finger_pos = exp.mouse.position
            else:
                btn_id, moved, finger_pos, rt = exp.mouse.wait_event(wait_button=True, wait_motion=False, buttons=0,
                                                                     wait_for_buttonup=False)
            state = self.check_xy(finger_pos[0], finger_pos[1])

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._log_func_returns(False)
                return False

            # Invoke custom operations on each loop iteration
            if state == StartPoint.State.init:

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

        self._log_func_returns(True)
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
            self._log_func_returns(self.State.aborted)
            return self.State.aborted

        #-- Wait
        time_started_waiting = u.get_time()
        state = None
        while state not in [StartPoint.State.start, StartPoint.State.error]:

            if exp.mouse.check_button_pressed(0):
                #-- Finger still touching screen
                finger_pos = exp.mouse.position
                state = self.check_xy(finger_pos[0], finger_pos[1])
            else:
                #-- Finger lifted
                self._log_func_returns(self.State.aborted)
                return self.State.aborted

            if max_wait_time is not None and u.get_time() - time_started_waiting >= max_wait_time:
                self._log_func_returns(self.State.timeout)
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

        self._log_func_returns(state)
        return state

