"""

Number line: The NumberLine class presents a number line, detect when finger/mouse crosses it, and where

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

from enum import Enum
import numbers
import numpy as np

# noinspection PyProtectedMember
from trajtracker.utils import get_time
import expyriment as xpy

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u


# noinspection PyAttributeOutsideInit,PyProtectedMember
class NumberLine(trajtracker._TTrkObject, trajtracker.events.OnsetOffsetObj):

    Orientation = Enum('Orientation', 'Horizontal Vertical')

    #TODO: even after preloaded, allow chaning properties. We just need to know what should be changed.

    #===================================================================================
    #      Constructor + easy setters
    #===================================================================================

    def __init__(self, position, line_length, max_value, min_value=0,
                 orientation=Orientation.Horizontal,
                 line_width=1, line_colour=None, end_tick_height=None,
                 visible=True):
        """
        Constructor - invoked when you create a new object by writing NumberLine()

        :param position: the (x,y) coordinates of the middle of the line
        :param orientation: NumberLine.Orientation.Horizontal or NumberLine.Orientation.Vertical
        :param line_length: the length of the line, in pixels
        :param line_width: the width (thickness) of the line, in pixels (default = 1)
        :param line_colour: the color of the line (default = None)
        :param end_tick_height: the height of the ticks at the end of the line (default = None; see property for details)

        :param min_value: the logical value at the beginning of the line (default = 0)
        :param max_value: the logical value at the end of the line

        :param visible: set the line as visible/invisible in the next plotting

        :type position: tuple
        :type line_length: int
        :type line_colour: tuple
        :type line_width: number
        :type min_value: number
        :type max_value: number
        :type end_tick_height: number

        """

        super(NumberLine, self).__init__()

        #-- When preloaded, visual properties cannot be changed any longer
        self._preloaded = False

        self._canvas = None

        self.orientation = orientation

        #-- Visual properties of the line itself
        self.position = position
        self.line_length = line_length
        self.line_width = line_width
        self.line_colour = line_colour
        self.end_tick_height = end_tick_height

        #-- Visual properties of the text labels at the ends of the line
        self.show_labels(visible=False)

        #-- Mid-of-line ticks

        #-- Logical length of the number line
        self.min_value = min_value
        self.max_value = max_value

        #-- Touch parameters
        self._touch_directioned = True  # True: finger must be dragged to the NL from its initial direction
                                        # False: whenever the finger is close enough to the line, it's a touch
        self._touch_distance = 0        # Issue a "touch" decision when the finger is closer than this to the line
                                        # _touch_directioned=True and distance<0 means that finger must cross the line and get this far on the other side

        self.visible = visible

        self._visual_objects = {}

        self.reset()


    #-----------------------------------------------------------------------------------
    def show_labels(self, visible=True, box_size=None, font_name=None, font_size=None, font_colour=None, offset=(0, 0),
                    text_min=None, text_max=None):
        """
        Determine appearance of the two text labels at the ends of the line

        :param visible: Whether the labels are visible or not (boolean)
        :type visible: bool
        :param box_size: Size of the text box in pixels (width, height)
        :type box_size: tuple
        :param font_name: Name of font
        :type font_name: str
        :param font_size: Size of font
        :type font_size: int
        :param font_colour: Color of font
        :type font_colour: Expyriment colour spec
        :param offset: (x,y) offset of a label (in pixels) relatively to the corresponding end of the number line
        :type offset: tuple
        :param text_min: Text for the label at the MIN end of the number line (default: min value)
        :type text_min: str
        :param text_max: Text for the label at the MAX end of the number line (default: max value)
        :type text_max: str
        """

        self.labels_visible = visible
        self.labels_box_size = box_size
        self.labels_font_colour = font_colour
        self.labels_font_name = font_name
        self.labels_font_size = font_size
        self.labels_offset = offset
        self.label_min_text = text_min
        self.label_max_text = text_max


    #===================================================================================
    #      Plotting
    #===================================================================================

    def preload(self):
        """
        Pre-load the number line - prepare for plotting

        :return: The time it took this function to run. (seconds)
        """

        start_time = get_time()

        if self._preloaded:
            # Already pre-loaded
            return get_time() - start_time

        self.validate()
        self._preloaded = True

        if self._line_colour is not None:
            self._prepare_main_line()
            if self._end_tick_height != 0 and self._end_tick_height is not None:
                self._prepare_end_of_line_ticks()

        if self._labels_visible:
            self._prepare_labels()

        self._canvas = xpy.stimuli.Canvas(self.size)
        self.plot(self._canvas)
        self._canvas.position = self.position

        return get_time() - start_time


    #-------------------------------------------------------
    def present(self, clear=False, update=False):
        """
        Present the stimulus

        :param clear: Whether to clear the screen buffer prior to presenting. Default=False
        :type clear: bool
        :param update: Whether to flip buffer after plotting. Default=False
        :type update: bool
        :return: The time it took this function to run. (seconds)
        """
        start_time = get_time()

        self.preload()

        self._canvas.present(clear, update)

        return get_time() - start_time

    #-------------------------------------------------------
    @property
    def size(self):
        """
        Get the size of the rectangle surrounding the number line, with all its elements.
        The number line center will be at the center of the rectangle

        :return: tuple (width, height)
        """

        self._canvas_to_nl_coord_shift = (0, 0)

        #-- First, get the minimal/maximal coordinates of elements on the canvas

        # Start and end of the number line
        xmin, ymin = self._main_line_start()
        xmax, ymax = self._main_line_end()

        # Apply tick marks
        if self._orientation == NumberLine.Orientation.Horizontal:
            ymax += self.end_tick_height
        else:
            xmax += self.end_tick_height

        # Apply text labels
        if self._labels_visible:

            text_x_offset_min = self._labels_offset_x - self._labels_box_size[0]/2
            text_x_offset_max = self._labels_offset_x + self._labels_box_size[0]/2

            text_y_offset_min = self._labels_offset_y - self._labels_box_size[1]/2
            text_y_offset_max = self._labels_offset_y + self._labels_box_size[1]/2

            xmin = min(xmin, xmin + text_x_offset_min)
            xmax = max(xmax, xmax + text_x_offset_max)
            ymin = min(ymin, ymin + text_y_offset_min)
            ymax = max(ymax, ymax + text_y_offset_max)

        #-- In order to keep the number line's center in coordinates (0,0), i.e., in the center of the
        #-- canvas, make sure the canvas is symmetric
        #-- Get canvas size
        width = 2 * max(xmax, -xmin)
        height = 2 * max(ymax, -ymin)

        #-- Create the canvas
        return width, height


    #-------------------------------------------------------
    def _prepare_main_line(self):
        main_line = xpy.stimuli.Line(self._main_line_start(), self._main_line_end(),
                                     self._line_width, self._line_colour)
        main_line.preload()

        # print "preparing line from {0} to {1} width={2} color={3}".format(self._main_line_start(), self._main_line_end(), self._line_width, self._line_colour)

        self._visual_objects['main_line'] = main_line

    #-------------------------------------------------------
    def _prepare_end_of_line_ticks(self):
        tick_dx = 0 if self._orientation == NumberLine.Orientation.Horizontal else self._end_tick_height
        tick_dy = self._end_tick_height if self._orientation == NumberLine.Orientation.Horizontal else 0

        pt1 = self._main_line_start()
        pt2 = self._main_line_end()
        tick1 = xpy.stimuli.Line(pt1, (pt1[0] + tick_dx, pt1[1] + tick_dy),
                                 self._line_width, self._line_colour)
        tick2 = xpy.stimuli.Line(pt2, (pt2[0] + tick_dx, pt2[1] + tick_dy),
                                 self._line_width, self._line_colour)

        tick1.preload()
        tick2.preload()

        self._visual_objects['endtick1'] = tick1
        self._visual_objects['endtick2'] = tick2


    #-------------------------------------------------------
    # Text labels - one at each end of the line
    #
    def _prepare_labels(self):
        dx = self._labels_offset_x
        dy = self._labels_offset_y

        min_text = str(self._min_value) if self._label_min_text is None else self._label_min_text
        min_pos = self._main_line_start()
        min_pos = (min_pos[0] + dx, min_pos[1] + dy)
        min_box = xpy.stimuli.TextBox(text=min_text, size=self._labels_box_size, position=min_pos,
                                      text_font=self._labels_font_name, text_colour=self._labels_font_colour,
                                      text_size=self._labels_font_size, text_justification=1)  # 1=center
        min_box.preload()

        max_text = str(self._max_value) if self._label_max_text is None else self._label_max_text
        max_pos = self._main_line_end()
        max_pos = (max_pos[0] + dx, max_pos[1] + dy)
        max_box = xpy.stimuli.TextBox(text=max_text, size=self._labels_box_size, position=max_pos,
                                      text_font=self._labels_font_name, text_colour=self._labels_font_colour,
                                      text_size=self._labels_font_size, text_justification=1)  # 1=center
        max_box.preload()

        self._visual_objects['label_min'] = min_box
        self._visual_objects['label_max'] = max_box

        return

    #-------------------------------------------------------
    # Get start/end points of the main line relatively to the canvas
    #
    def _main_line_start(self):
        if self._orientation == NumberLine.Orientation.Horizontal:
            return -self._line_length/2, 0
        else:
            return 0, -self._line_length/2


    def _main_line_end(self):
        if self._orientation == NumberLine.Orientation.Horizontal:
            return self._line_length/2, 0
        else:
            return 0, self._line_length/2


    #-------------------------------------------------------
    def plot(self, stim):
        """
        Plot the number line on another stimulus

        :param stim: Any Expyriment visual object
        :return: The time it took this function to run (seconds)
        """

        start_time = get_time()

        self.preload()

        #-- Plot all visual elements on the canvas
        if self._visible:
            for k in self._visual_objects:
                self._visual_objects[k].plot(stim)

        return get_time() - start_time


    #===================================================================================
    #      Track movement
    #===================================================================================

    _errmsg_mouseat_non_numeric_coord = "trajtracker error in NumberLine.mouseAt(): a non-numeric {0} coordinate was provided ({1})"

    #---------------------------------------------------------
    # noinspection PyUnusedLocal
    def reset(self, time0=None):
        """
        Reset the last-known mouse position, so that update_xy() will forget any previous movement
        This function is typically called in the beginning of a trial.

        :param time0: ignored.
        """

        self._last_mouse_coord = None    # Last coordinate where mouse was observed (x or y, depending on the number line orientation)
        self._last_touched_coord = None  # Last coordinate where the number line was touched (x or y, depending on the number line orientation)
        self._initial_mouse_dir = None   # +1 or -1: indicates the first click position relatively to the number line


    #---------------------------------------------------------
    # noinspection PyUnusedLocal
    def update_xyt(self, x_coord, y_coord, time=None):
        """
        This function is called when mouse/touch has moved. It checks whether the movement implies touching the number line.

        :param x_coord:
        :type x_coord: int

        :param y_coord:
        :type y_coord: int

        :param time: ignored.
        """

        _u.validate_func_arg_type(self, "update_xy", "x_coord", x_coord, int)
        _u.validate_func_arg_type(self, "update_xy", "y_coord", y_coord, int)
        self._log_func_enters("update_xy", [x_coord, y_coord])

        if self._last_touched_coord is not None:
            self._log_func_returns()
            return

        #-- Get the relevant coordinates (x or y)
        if self._orientation == NumberLine.Orientation.Horizontal:
            mouse_coord = y_coord
            line_coord = self._main_line_start()[1] + self._mid_y
            touch_coord = x_coord - self._mid_x
        else:
            mouse_coord = x_coord
            line_coord = self._main_line_start()[0] + self._mid_x
            touch_coord = y_coord - self._mid_y

        distance = line_coord - mouse_coord  # positive value: mouse coord < line coord

        if not self._touch_directioned:
            #-- Direction doesn't matter. Just check the distance from the number line.
            touched = np.abs(distance) <= self._touch_distance

        elif self._initial_mouse_dir is None:
            #-- Finger must approach the line from its initial direction, which was not set: set it now
            self._initial_mouse_dir = np.sign(distance)
            touched = False

        else:
            # Fix sign of distance, such that distance>0 means that the finger is still approaching the number line
            distance *= self._initial_mouse_dir

            touched = distance < self._touch_distance

        if touched:
            self._last_touched_coord = touch_coord

        self._log_func_returns()

        return None


    #---------------------------------------------------------
    @property
    def touched(self):
        """
        Indicates whether the number line was touched or not

        :type: bool
        """
        return self._last_touched_coord is not None


    #---------------------------------------------------------
    @property
    def last_touched_coord(self):
        """
        Get the coordinate where the mouse/finger last touched the number line.
        This is either the x or y coordinate, depending on the number line orientation
        If the finger didn't touch the line since the last call to reset_mouse_pos(), the function returns None.

        :type: int
        """
        return self._last_touched_coord


    #---------------------------------------------------------
    @property
    def last_touched_value(self):
        """
        The position where the mouse/finger last touched the number line.
        The value returned is in the number line's scale.
        If the finger didn't touch the line since the last call to reset_mouse_pos(), the function returns None.

        :type: float
        """
        if self._last_touched_coord is None:
            return None

        #-- Convert the coordinate into a position using a 0-1 scale
        pos01 = self._last_touched_coord / self.line_length + 0.5

        # noinspection PyUnresolvedReferences
        return pos01 * (self._max_value - self._min_value) + self._min_value


    #===================================================================================
    #      Property setters / getters
    #===================================================================================

    _errmsg_set_to_non_numeric = "trajtracker error: invalid attempt to set NumberLine.{0} to a non-numeric value ({1})"
    _errmsg_set_to_non_positive = "trajtracker error: invalid attempt to set NumberLine.{0} to a non-positive value ({1})"
    _errmsg_set_to_non_boolean = "trajtracker error: invalid attempt to set NumberLine.{0} to a non-boolean value ({1})"
    _errmsg_set_to_non_string = "trajtracker error: invalid attempt to set NumberLine.{0} to a non-string value ({1})"

    _errmsg_value_not_collection = "trajtracker error: invalid value for NumberLine.{0} ({1}) - expecting a tuple or list"
    _errmsg_value_bad_length = "trajtracker error: invalid value for NumberLine.{0} ({1}) - expecting a 2-element tuple"
    _errmsg_set_to_non_numeric_entry = "trajtracker error: invalid value for NumberLine.{0} - {2} is not a number ({1})"
    _errmsg_set_to_non_positive_entry = "trajtracker error: invalid value for NumberLine.{0} - {2} is a non-positive number({1})"

    #-----------------------------------------------------------
    def validate(self):
        """
        Validate that the number line configuration is ok.

        :raise: ValueError - if the configuration is invalid
        """

        if self._min_value >= self._max_value:
            raise ValueError("trajtracker error: NumberLine.min_value({0}) >= NumberLine.max_value({1})".format(self._min_value, self._max_value))

        if self._labels_visible:
            if self._labels_box_size is None:
                raise ValueError("trajtracker error: NumberLine - labels textbox size was not specified")
            if self._labels_font_name is None or self._labels_font_name == "":
                raise ValueError("trajtracker error: NumberLine - labels font name was not specified")
            if self._labels_font_size is None:
                raise ValueError("trajtracker error: NumberLine - labels font size was not specified")
            if self._labels_font_colour is None:
                raise ValueError("trajtracker error: NumberLine - labels font color was not specified")



    #-----------------------------------------------------------
    def _validate_unlocked(self):
        if self._preloaded:
            raise trajtracker.InvalidStateError('An attempt was made to change the visual properties of a NumberLine after it was already plotted')


    ###################################
    #  Line properties
    ###################################


    #-----------------------------------------------------------
    @property
    def orientation(self):
        """ The number line's orientation (NumberLine.Orientation.Horizontal or NumberLine.Orientation.Vertical) """
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._validate_unlocked()

        if not isinstance(value, trajtracker.stimuli.NumberLine.Orientation):
            raise ValueError("trajtracker error: invalid value for NumberLine.orientation ({0}) - expecting NumberLine.Orientation.Horizontal or NumberLine.Orientation.Vertical".format(value))

        self._orientation = value
        self._log_setter("orientation")

    #-----------------------------------------------------------
    @property
    def position(self):
        """
        The number line's position: the (x,y) coordinates of the line mid point (tuple/list are accepted)
        """
        return self._mid_x, self._mid_y

    @position.setter
    def position(self, value):
        self._validate_unlocked()

        value = _u.validate_attr_is_coord(self, "position", value)
        self._mid_x = value[0]
        self._mid_y = value[1]
        self._log_setter("position")

        if self._canvas is not None:
            self._canvas.position = self.position


    #-----------------------------------------------------------
    @property
    def line_length(self):
        """The number line length (in pixels). Only positive values are valid."""
        return self._line_length

    @line_length.setter
    def line_length(self, value):
        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("line_length", value))
        if value <= 0:
            raise ValueError(NumberLine._errmsg_set_to_non_positive.format("line_length", value))

        self._line_length = value
        self._log_setter("line_length")

    #-----------------------------------------------------------
    @property
    def end_tick_height(self):
        """
        The height of the ticks at the ends of the number line (in pixels)
        Positive values = ticks above the line or to its right; negative values = below/left.
        """
        return self._end_tick_height

    @end_tick_height.setter
    def end_tick_height(self, value):
        self._validate_unlocked()

        if value is not None and not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("end_tick_height", value))

        self._end_tick_height = value
        self._log_setter("end_tick_height")

    #-----------------------------------------------------------
    @property
    def line_width(self):
        """The number line width (in pixels). Only positive values are valid."""
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("line_width", value))
        if value <= 0:
            raise ValueError(NumberLine._errmsg_set_to_non_positive.format("line_width", value))

        self._line_width = value
        self._log_setter("line_width")

    #-----------------------------------------------------------
    @property
    def line_colour(self):
        """The color of the number line. None = the line will not be plotted."""
        return self._line_colour

    @line_colour.setter
    def line_colour(self, value):
        self._validate_unlocked()
        self._line_colour = value
        self._log_setter("line_colour")


    ###################################
    #  Labels properties
    ###################################

    #-----------------------------------------------------------
    @property
    def labels_visible(self):
        """Whether the end-of-line labels are visible or not (boolean)"""
        return self._labels_visible

    @labels_visible.setter
    def labels_visible(self, value):
        if isinstance(value, numbers.Number):
            value = value != 0
        elif not isinstance(value, bool):
                raise ValueError(NumberLine._errmsg_set_to_non_boolean, "labels_visible", value)

        self._labels_visible = value
        self._log_setter("labels_visible")

    #-----------------------------------------------------------
    @property
    def labels_font_name(self):
        """The font name of the end-of-line labels"""
        return self._labels_font_name

    @labels_font_name.setter
    def labels_font_name(self, value):
        self._validate_unlocked()

        if value is not None and type(value) != str:
            raise ValueError(NumberLine._errmsg_set_to_non_string.format("labels_font_name", value))

        self._labels_font_name = value
        self._log_setter("labels_font_name")

    #-----------------------------------------------------------
    @property
    def labels_font_colour(self):
        """
        The font color of the end-of-line labels.
        The value is an expyriment color - tuple of 3 values, each 0-255
        """
        return self._labels_font_colour

    @labels_font_colour.setter
    def labels_font_colour(self, value):
        self._validate_unlocked()
        self._labels_font_colour = value
        self._log_setter("labels_font_colour")


    #-----------------------------------------------------------
    @property
    def labels_font_size(self):
        """The font size of the end-of-line labels"""
        return self._labels_font_size

    @labels_font_size.setter
    def labels_font_size(self, value):
        self._validate_unlocked()

        if value is not None:
            if not isinstance(value, numbers.Number):
                raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("labels_font_size", value))
            if value <= 0:
                raise ValueError(NumberLine._errmsg_set_to_non_positive.format("labels_font_size", value))

        self._labels_font_size = value
        self._log_setter("labels_font_size")


    #-----------------------------------------------------------
    @property
    def labels_box_size(self):
        """The textbox size of the end-of-line labels (height, width)"""
        return self._labels_box_size

    @labels_box_size.setter
    def labels_box_size(self, value):
        self._validate_unlocked()

        if value is not None:
            if not hasattr(value, '__iter__'):
                raise ValueError(NumberLine._errmsg_value_not_collection.format("labels_box_size", value))
            if len(value) != 2:
                raise ValueError(NumberLine._errmsg_value_bad_length.format("labels_box_size", value))
            if not isinstance(value[0], numbers.Number):
                raise ValueError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_box_size", value, "height"))
            if not isinstance(value[1], numbers.Number):
                raise ValueError(NumberLine._errmsg_set_to_non_numeric_entry.format("labels_box_size", value, "width"))
            if value[0] <= 0:
                raise ValueError(NumberLine._errmsg_set_to_non_positive_entry.format("labels_box_size", value, "height"))
            if value[1] <= 0:
                raise ValueError(NumberLine._errmsg_set_to_non_positive_entry.format("labels_box_size", value, "width"))

        self._labels_box_size = value
        self._log_setter("labels_box_size")

    #-----------------------------------------------------------
    @property
    def labels_offset(self):
        """
        The number line's position: the (x,y) coordinates of the line mid point (tuple/list are accepted)
        """
        return self._labels_offset_x, self._labels_offset_y

    @labels_offset.setter
    def labels_offset(self, value):
        self._validate_unlocked()

        value = _u.validate_attr_is_coord(self, "labels_offset", value, True)
        self._labels_offset_x = value[0]
        self._labels_offset_y = value[1]
        self._log_setter("labels_offset")

    #-----------------------------------------------------------
    @property
    def label_min_text(self):
        """The text for the label at the MIN end of the number line"""
        return self._label_min_text

    @label_min_text.setter
    def label_min_text(self, value):
        self._validate_unlocked()

        if isinstance(value, numbers.Number):
            value = str(value)
        elif value is not None and type(value) != str:
            raise ValueError(NumberLine._errmsg_set_to_non_string.format("label_min_text", value))

        self._label_min_text = value
        self._log_setter("label_min_text")

    #-----------------------------------------------------------
    @property
    def label_max_text(self):
        """The text for the label at the MAX end of the number line"""
        return self._label_max_text

    @label_max_text.setter
    def label_max_text(self, value):
        self._validate_unlocked()

        if isinstance(value, numbers.Number):
            value = str(value)
        elif value is not None and type(value) != str:
            raise ValueError(NumberLine._errmsg_set_to_non_string.format("label_max_text", value))

        self._label_max_text = value
        self._log_setter("label_max_text")




    ###################################
    #  Line values
    ###################################

    #-----------------------------------------------------------
    @property
    def min_value(self):
        """The minimal logical value on the number line"""
        return self._min_value

    @min_value.setter
    def min_value(self, value):
        self._validate_unlocked()
        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("min_value", value))
        self._min_value = value
        self._log_setter("min_value")

    #-----------------------------------------------------------
    @property
    def max_value(self):
        """The maximal logical value on the number line"""
        return self._max_value

    @max_value.setter
    def max_value(self, value):
        self._validate_unlocked()
        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("max_value", value))
        self._max_value = value
        self._log_setter("max_value")


    #-----------------------------------------------------------
    @property
    def visible(self):
        """Whether the number line is visible (boolean)"""
        return self._visible

    @visible.setter
    def visible(self, value):
        if isinstance(value, numbers.Number):
            value = value != 0
        elif not isinstance(value, bool):
                raise ValueError(NumberLine._errmsg_set_to_non_boolean, "visible", value)

        self._visible = value
        self._log_setter("visible")


    ###################################
    #  Touch properties
    ###################################

    #-----------------------------------------------------------
    @property
    def touch_distance(self):
        """Minimal distance from line that counts as touch (negative value: finger must cross to the other side)"""
        return self._touch_distance

    @touch_distance.setter
    def touch_distance(self, value):
        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_numeric.format("touch_distance", value))

        self._touch_distance = value
        self._log_setter("touch_distance")


    #-----------------------------------------------------------
    @property
    def touch_directioned(self):
        """Whether the number line can be touched only from the finger's movement direction (True) or from any direction (False)"""
        return self._touch_directioned

    @touch_directioned.setter
    def touch_directioned(self, value):

        self._validate_unlocked()

        if not isinstance(value, numbers.Number):
            raise ValueError(NumberLine._errmsg_set_to_non_boolean.format("touch_directioned", value))

        self._touch_directioned = value
        self._log_setter("touch_directioned")


