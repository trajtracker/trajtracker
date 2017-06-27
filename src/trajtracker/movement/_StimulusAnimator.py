"""

Stimulus animator: animate a stimulus by moving it

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

import trajtracker
import trajtracker._utils as _u


class StimulusAnimator(trajtracker.TTrkObject):


    def __init__(self, animated_object=None, trajectory_generator=None, position_shift=None):
        """
        Constructor - invoked when you create a new object by writing StimulusAnimator()

        :param animated_object: See :attr:`~trajtracker.movement.StimulusAnimator.animated_object`
        :type animated_object: Expyriment stimulus

        :param trajectory_generator: See :attr:`~trajtracker.movement.StimulusAnimator.trajectory_generator`

        :param position_shift: See :attr:`~trajtracker.movement.StimulusAnimator.position_shift`
        :type position_shift: tuple
        """
        super(StimulusAnimator, self).__init__()

        self.animated_object = animated_object
        self.trajectory_generator = trajectory_generator
        self.position_shift = position_shift
        self.do_clear_screen = False
        self.do_update_screen = False
        self.reset()


    #=======================================================================
    # Move
    #=======================================================================

    #------------------------------------------------------------
    def reset(self, time0=0):
        """
        Reset the movement. This does not move the object, it just resets the time

        :param time0: The time that counts as zero (when calling the position-generator)
        """
        self._time0 = time0


    #------------------------------------------------------------
    def update(self, time):
        """
        Call this function on each frame where you want the animated object to move.

        :param time: The time (typically - time from start of trial)
        """
        _u.validate_func_arg_type(self, "update", "time", time, numbers.Number)

        if self._animated_object is None or self._trajectory_generator is None:
            return

        relative_time = time - self._time0

        traj_point = self._trajectory_generator.get_traj_point(relative_time)
        x = traj_point['x'] if 'x' in traj_point else self._animated_object.position[0]
        y = traj_point['y'] if 'y' in traj_point else self._animated_object.position[1]
        visible = traj_point['visible'] if 'visible' in traj_point else True
        self._animated_object.position = x, y
        if visible:
            self._animated_object.present(update=self._do_update_screen, clear=self._do_clear_screen)


    #=======================================================================
    # Configure
    #=======================================================================

    #------------------------------------------------------------
    @property
    def animated_object(self):
        """
        The object being moved by this animator.
        The object should be an Expyriment visual stimulus - i.e., with a present(clear,update) method and a "position" property
        """
        return self._animated_object

    @animated_object.setter
    def animated_object(self, obj):
        if "present" not in dir(obj):
            raise trajtracker.ValueError("{:}.animated_object must be an object with a present() method".format(_u.get_type_name(self)))
        if "position" not in dir(obj):
            raise trajtracker.ValueError("{:}.animated_object must be an object with a 'position' property".format(_u.get_type_name(self)))

        self._animated_object = obj
        self._log_property_changed("animated_object")

    #------------------------------------------------------------
    @property
    def trajectory_generator(self):
        """
        An object that generates, per time point, the x,y coordinates where the animated object should be moved to
        """
        return self._trajectory_generator

    @trajectory_generator.setter
    def trajectory_generator(self, obj):

        if "get_traj_point" not in dir(obj):
            raise trajtracker.ValueError("{:}.trajectory_generator must be an object with a get_traj_point() method".format(_u.get_type_name(self)))

        self._trajectory_generator = obj

    #------------------------------------------------------------
    @property
    def position_shift(self):
        """
        (x,y) coordinates. The coordinates generated by the :attr:`~trajtracker.movement.StimulusAnimator.trajectory_generator`
        will be shifted by this amount before updating :attr:`~trajtracker.movement.StimulusAnimator.animated_object`

        This property can be set to x,y tuple/list or to an expyriment.geometry.XYPoint
        """
        return self._position_shift

    @position_shift.setter
    def position_shift(self, value):
        value = _u.validate_attr_is_coord(self, "position_shift", value, change_none_to_0=True)
        self._position_shift = value
        self._log_property_changed("position_shift")

    #------------------------------------------------------------
    @property
    def do_clear_screen(self):
        """
        If true, the screen will be cleared on each frame by calling animated_object.present(clear=True)
        """
        return self._do_clear_screen

    @do_clear_screen.setter
    def do_clear_screen(self, value):
        _u.validate_attr_type(self, "do_clear_screen", value, bool)
        self._do_clear_screen = value
        self._log_property_changed("do_clear_screen")

    #------------------------------------------------------------
    @property
    def do_update_screen(self):
        """
        If true, the screen will be updated on each frame by calling animated_object.present(update=True)
        """
        return self._do_update_screen

    @do_update_screen.setter
    def do_update_screen(self, value):
        _u.validate_attr_type(self, "do_update_screen", value, bool)
        self._do_update_screen = value
        self._log_property_changed("do_update_screen")

