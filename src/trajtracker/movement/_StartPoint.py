"""

 The starting point for finger/mouse movement

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

import numbers
from enum import Enum

import trajtracker
import trajtracker._utils as _u
from trajtracker.misc import shapes


class StartPoint(trajtracker._TTrkObject):
    """
    A rectangular starting point.
    The starting point defines two areas:
    - start area: where you must touch/click to initiate a trial
    - exit area: for successful start, you must drag the mouse/finger from the start area directly into this area
    """

    default_exit_area_size = 100

    State = Enum("State", "reset init start error aborted")


    #-----------------------------------------------------------
    def __init__(self, start_area, exit_area="above"):
        """
        Constructor

        :param start_area: The area where you must touch/click to initiate a trial.
                           This object must support an overlapping_with_position() method and a "center" property.
                           It can be an expyriment stimulus, a shape from :func:`~trajtracker.misc.shapes`, or your own object
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
        an expyriment stimulus, a shape from :func:`~trajtracker.misc.shapes`, or your own object.
        Also, you can use any of the predefined keywords "above", "below", "right" and "left". Each of those
        define a region that is a 90-degrees sector, centered on start_area's center
        ("above" = -45 degrees to 45 degrees; the others accordingly),
        """
        return self._exit_area


    @exit_area.setter
    def exit_area(self, value):
        if isinstance(value, str):
            self._exit_area = self._create_default_exit_area(value)
            self._log_setter("exit_area", value=value)
        elif "overlapping_with_position" in dir(value):
            self._exit_area = value
            self._log_setter("exit_area", value="shape")
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

        return shapes.Sector(self._start_area.position[0], self._start_area.position[1], 10000, f, t)


    #==========================================================================
    #   Runtime API
    #==========================================================================


    #-----------------------------------------------------------------
    def reset(self):
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
    def wait_until_touched(self, exp, on_loop=None):
        """
        Wait until the starting point is touched

        :param exp: The Expyriment experiment object
        :param on_loop: Defines what to do on each iteration on the loop that waits for the area to be touched. This can be:
                        (1) A callback function to call on each loop. Ideally, this function should include some delaying;
                        or (2) or a visual object with a present() method, which will be called.
                        If "None" is provided, the function will wait for 15 ms on each loop iteration.
        """

        self._log_func_enters("wait_until_touched", ["exp", on_loop])

        if on_loop is None:
            on_loop = lambda: exp.clock.wait(15)
        elif "present" in dir(on_loop):
            stim = on_loop
            on_loop = lambda: stim.present()
        elif type(on_loop) != type(lambda:1):
            raise TypeError(("trajtracker error: invalid on_loop argument provided to {:}.wait_until_touched() - " +
                             "expecting either a visual object or a function").format(type(self).__name__))

        state = StartPoint.State.reset
        first_time = True
        while state != StartPoint.State.init:

            if not first_time:
                on_loop()
            first_time = False

            if exp.mouse.check_button_pressed(0):
                finger_pos = exp.mouse.position
            else:
                btn_id, moved, finger_pos, rt = exp.mouse.wait_event(wait_button=True, wait_motion=False, buttons=0,
                                                                     wait_for_buttonup=False)
            state = self.check_xy(finger_pos[0], finger_pos[1])


    #------------------------------------------------
    def wait_until_exit(self, exp, on_loop=None):
        """
        Wait until the finger leaves the starting area

        :param exp: The Expyriment experiment object
        :param on_loop: Defines what to do on each iteration on the loop that waits for the finger to leave the starting point.
                        This can be:
                        (1) A callback function to call on each loop. Ideally, this function should include some delaying;
                        or (2) or a visual object with a present() method, which will be called.
                        If "None" is provided, the function will wait for 15 ms on each loop iteration.
        :returns: State.start if left the start area in the correct direction; State.error if not; State.aborted if
                  the finger was lifted.
        """

        self._log_func_enters("wait_until_exit", ["exp", on_loop])

        if not exp.mouse.check_button_pressed(0):
            # -- Finger lifted
            self._log_func_returns(self.State.aborted)
            return self.State.aborted

        if on_loop is None:
            on_loop = lambda: exp.clock.wait(10)
        elif "present" in dir(on_loop):
            stim = on_loop
            on_loop = lambda: stim.present()
        elif type(on_loop) != type(lambda:1):
            raise TypeError(("trajtracker error: invalid on_loop argument provided to {:}.wait_until_exit() - " +
                             "expecting either a visual object or a function").format(type(self).__name__))

        #-- Wait
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

            on_loop()

        self._log_func_returns(state)
        return state

