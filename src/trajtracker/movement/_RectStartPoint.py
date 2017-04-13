"""

 The starting point for finger/mouse movement - a rectangular point

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""


from __future__ import division

import numbers
import numpy as np
from enum import Enum

import expyriment as xpy

import trajtracker as ttrk
import trajtracker._utils as _u
from trajtracker.misc import nvshapes


EXIT_AREA_HEIGHT = 200


class RectStartPoint(ttrk._TTrkObject):

    def __init__(self, size=None, position=(0,0), rotation=0, colour=xpy.misc.constants.C_GREY):
        super(RectStartPoint, self).__init__()

        self._preloaded = False
        self._start_rect = None

        self.size = size
        self.position = position
        self.rotation = rotation
        self.colour = colour


    #-------------------------------------------------
    def preload(self):
        """
        Prepare the stimuli. 
        
        Once this is done, you cannot modify :attr:`~trajtracker.movement.RectStartPoint.size` ,
        :attr:`~trajtracker.movement.RectStartPoint.position` , and :attr:`~trajtracker.movement.RectStartPoint.rotation`
        
        This method is automatically called if you call :func:`~trajtracker.movement.RectStartPoint.reset` or
        :func:`~trajtracker.movement.RectStartPoint.check_xy`, however, it is a better practice to call it yourself
        before the experiment starts, because the method is more time-consuming than other methods. 
        """

        if self._preloaded:
            return

        self._start_rect = self._create_start_area()
        exit_area = self._create_exit_area()

        self._start_point = ttrk.movement.StartPoint(self._start_rect, exit_area=exit_area)
        self._start_point.log_level = self.log_level

        self._preloaded = True


    #-------------------------------------------------
    def _create_start_area(self):
        start_area = xpy.stimuli.Rectangle(size=self._size, position=self._position, colour=self._colour)
        start_area.rotate(self._rotation)
        return start_area


    # -------------------------------------------------
    def _create_exit_area(self):

        # -- Find position of the exit area, considering the rotation
        r = (EXIT_AREA_HEIGHT + self._size[1]) / 2
        rotation_rad = self._rotation / 360 * np.pi * 2
        x = self._position[0] + -np.sin(-rotation_rad) * r
        y = self._position[1] + np.cos(-rotation_rad) * r

        exit_area_width = max(self._size[0] * 2, EXIT_AREA_HEIGHT)

        exit_area = nvshapes.Rectangle(size=(exit_area_width, EXIT_AREA_HEIGHT), position=(x, y),
                                       rotation=self._rotation)

        return exit_area


    #-------------------------------------------------
    @property
    def start_rect(self):
        """
        Access the visual rectangle stimulus (an expyriment.stimuli.Rectangle object) - 
        allows modifying its properties.
        
        **Note: changing the size/position of this rectangle may result in unexpected behavior** 
        """
        self.preload()
        return self._start_rect


    #================================================================================
    #   Runtime API
    #================================================================================

    #-----------------------------------------------------------------
    def reset(self):
        """
        See :func:`StartPoint.reset() <trajtracker.movement.StartPoint.reset>`
        """
        self.preload()
        self._start_point.reset()


    #-----------------------------------------------------------------
    def check_xy(self, x_coord, y_coord):
        """
        See :func:`StartPoint.check_xy() <trajtracker.movement.StartPoint.check_xy>`
        """
        self.preload()
        return self._start_point.check_xy(x_coord, y_coord)


    #-----------------------------------------------------------------
    def wait_until_startpoint_touched(self, exp, on_loop_callback=None, on_loop_present=None,
                                      event_manager=None, trial_start_time=None, session_start_time=None,
                                      max_wait_time=None):
        """ See :func:`StartPoint.wait_until_startpoint_touched() <trajtracker.movement.StartPoint.wait_until_startpoint_touched>` """
        self.preload()
        return self._start_point.wait_until_startpoint_touched(
            exp, on_loop_callback=on_loop_callback, on_loop_present=on_loop_present,
            event_manager=event_manager, trial_start_time=trial_start_time, session_start_time=session_start_time,
            max_wait_time=max_wait_time)

    #-----------------------------------------------------------------
    def wait_until_exit(self, exp, on_loop_callback=None, on_loop_present=None,
                        event_manager=None, trial_start_time=None, session_start_time=None,
                        max_wait_time=None):
        """ See :func:`StartPoint.wait_until_exit() <trajtracker.movement.StartPoint.wait_until_exit>` """
        self.preload()
        return self._start_point.wait_until_exit(
            exp, on_loop_callback=on_loop_callback, on_loop_present=on_loop_present,
            event_manager=event_manager, trial_start_time=trial_start_time, session_start_time=session_start_time,
            max_wait_time=max_wait_time)

    #================================================================================
    #   Configuration
    #================================================================================

    #-------------------------------------------------
    @property
    def size(self):
        """
        The size of the "start" rectangle.
        
        *This property cannot be updated after the start point was preloaded*
         
        :type: (x,y) tuple 
        """
        return self._size

    @size.setter
    def size(self, value):
        if self._preloaded:
            raise ttrk.InvalidStateError("{:}.size cannot be set after the object was preloaded".format(_u.get_type_name(self)))

        if value is None:
            self._size = None

        else:
            _u.validate_attr_is_collection(self, "size", value, 2, 2)
            _u.validate_attr_numeric(self, "size[0]", value[0])
            _u.validate_attr_positive(self, "size[0]", value[0])
            _u.validate_attr_numeric(self, "size[1]", value[1])
            _u.validate_attr_positive(self, "size[1]", value[1])

            self._size = (int(value[0]), int(value[1]))

        self._log_property_changed("size")

    #-------------------------------------------------
    @property
    def position(self):
        """
        The position of the "start" rectangle on screen

        *This property cannot be updated after the start point was preloaded*

        :type: (x,y) tuple 
        """
        return self._position

    @position.setter
    def position(self, value):
        if self._preloaded:
            raise ttrk.InvalidStateError("{:}.position cannot be set after the object was preloaded".format(_u.get_type_name(self)))

        if value is None:
            self._position = None

        else:
            _u.validate_attr_is_collection(self, "size", value, 2, 2)
            _u.validate_attr_numeric(self, "size[0]", value[0])
            _u.validate_attr_numeric(self, "size[1]", value[1])

            self._position = (int(value[0]), int(value[1]))

        self._log_property_changed("position")


    #-------------------------------------------------
    @property
    def rotation(self):
        """
        The tilt of the start rectangle, in degrees (positive number = clockwise)

        *This property cannot be updated after the start point was preloaded*
        """
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if self._preloaded:
            raise ttrk.InvalidStateError("{:}.rotation cannot be set after the object was preloaded".format(_u.get_type_name(self)))

        _u.validate_attr_numeric(self, "rotation", value)
        value = value % 360
        self._rotation = value

        self._log_property_changed("rotation")

    #-------------------------------------------------
    @property
    def colour(self):
        return self._colour

    @colour.setter
    def colour(self, value):
        if self._preloaded:
            raise ttrk.InvalidStateError("{:}.colour cannot be set after the object was preloaded".format(_u.get_type_name(self)))

        _u.validate_attr_rgb(self, "colour", value)
        self._colour = value

        self._log_property_changed("colour")


    #--------------------------------------------------------------------------
    def _set_log_level(self, level):
        self._log_level = level
        if "_start_point" in dir(self):
            self._start_point.log_level = level
