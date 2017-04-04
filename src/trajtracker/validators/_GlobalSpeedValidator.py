"""

Validator for minimal/maximal global speed

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from __future__ import division

from enum import Enum
import numbers
import numpy as np

import expyriment as xpy

import trajtracker
import trajtracker._utils as _u
from trajtracker.validators import ValidationAxis, ExperimentError, _BaseValidator, _parse_validation_axis
from trajtracker.movement import StimulusAnimator
from trajtracker.data import fromXML


# -------------------------------------------------------------
def _parse_xml_milestones(xml):
    milestones = []
    for child in xml:
        if child.tag != "milestone":
            raise trajtracker.BadFormatError(
                "Invalid XML format for defining {:}'s milestones: XML block '{:}' is unknown".format(
                    type(self).__name__, child.tag))
        if 'time' not in child.attrib or 'distance' not in child.attrib:
            raise trajtracker.BadFormatError(
                "Invalid XML format for defining {:}'s milestones: either time=xxx or distance=xxx is missing from a 'milestone' XML block".format(
                    type(self).__name__))
        milestones.append(GlobalSpeedValidator.Milestone(float(child.attrib['time']), float(child.attrib['distance'])))

    return milestones


# noinspection PyAttributeOutsideInit
class GlobalSpeedValidator(_BaseValidator):
    """
    Validate minimal movement speed.
    The validation is of the *average* speed per trial. The validator can also interpolate the speed limit,
    i.e., impose the limit on the average speed from time=0 until any time point during the trial.
    """

    err_too_slow = "TooSlowGlobal"

    arg_expected_coord = "expected_coord"
    arg_actual_coord = "actual_coord"


    class Milestone(object):
        def __init__(self, time_percentage, distance_percentage):
            self.time_percentage = time_percentage
            self.distance_percentage = distance_percentage

        def __str__(self):
            return "GlobalSpeedValidator.Milestone(time={:}, distance={:})".format(self.time_percentage, self.distance_percentage)


    #-----------------------------------------------------------------------------------
    def __init__(self, enabled=True, origin_coord=None, end_coord=None, axis=ValidationAxis.y,
                 grace_period=None, max_trial_duration=None, milestones=None, show_guide=False):
        """

        :param enabled: See :attr:`~trajtracker.validators.GlobalSpeedValidator.enabled`
        :type enabled: bool

        :param origin_coord: See :attr:`~trajtracker.validators.GlobalSpeedValidator.origin_coord`
        :type origin_coord: int

        :param end_coord: See :attr:`~trajtracker.validators.GlobalSpeedValidator.end_coord`
        :type end_coord: int

        :param axis: See :attr:`~trajtracker.validators.GlobalSpeedValidator.axis`
        :type axis: trajtracker.validators.ValidationAxis

        :param grace_period: See :attr:`~trajtracker.validators.GlobalSpeedValidator.grace_period`
        :type grace_period: number

        :param max_trial_duration: See :attr:`~trajtracker.validators.GlobalSpeedValidator.max_trial_duration`
        :type max_trial_duration: number

        :param milestones: See :attr:`~trajtracker.validators.GlobalSpeedValidator.milestones`
        :type milestones: list

        :param show_guide: See :attr:`~trajtracker.validators.GlobalSpeedValidator.show_guide`
        :type show_guide: bool
        """

        super(GlobalSpeedValidator, self).__init__(enabled=enabled)

        self.axis = axis
        self.grace_period = grace_period

        if milestones is None:
            self.milestones = [self.Milestone(1, 1)]
        else:
            self.milestones = milestones

        self._max_trial_duration = None
        if max_trial_duration is not None:
            self.max_trial_duration = max_trial_duration

        self._origin_coord = None
        if origin_coord is not None:
            self.origin_coord = origin_coord

        self._end_coord = None
        if end_coord is not None:
            self.end_coord = end_coord

        self.show_guide = show_guide
        self.guide_warning_time_delta = 0
        self.guide_line_length = None
        self.do_present_guide = True


    #========================================================================
    #      Validation API
    #========================================================================

    #----------------------------------------------------------------------------------
    def reset(self, time0=0):
        """
        Called when a trial starts - reset any previous movement

        :param time0: The time when the trial started
        :type time0: number
        """

        self._log_func_enters("reset", [time0])

        if time0 is not None and not isinstance(time0, (int, float)):
            raise ValueError(_u.ErrMsg.invalid_method_arg_type(self.__class__, "reset", "numeric", "time", time0))

        self._time0 = time0


    #----------------------------------------------------------------------------------
    def check_xyt(self, x_coord, y_coord, time):
        """
        Validate movement.

        :param x_coord:
        :type x_coord: int

        :param y_coord:
        :type y_coord: int

        :param time: Time from start of trial
        :returns: None if all OK; ExperimentError object if error
        """

        self._check_xyt_validate_and_log(x_coord, y_coord, time)
        self._assert_initialized(self._origin_coord, "origin_coord")
        self._assert_initialized(self._end_coord, "end_coord")
        self._assert_initialized(self._max_trial_duration, "max_trial_duration")

        if not self._enabled:
            return None

        #-- If this is the first call in a trial: do nothing
        if self._time0 is None:
            self.reset(time)
            return None

        if time < self._time0:
            raise trajtracker.InvalidStateError("{0}.check_xyt() was called with time={1}, but the trial started at time={2}".format(self.__class__, time, self._time0))

        time -= self._time0

        #-- Get the expected and actual coordinates
        coord = x_coord if self._axis == ValidationAxis.x else y_coord
        expected_coord = int(self.get_expected_coord_at_time(time))
        d_coord = coord - expected_coord

        #-- No validation during grace period
        if time <= self._grace_period:
            if self._show_guide:
                self._guide.show(expected_coord, GlobalSpeedGuide.LineMode.Grace)
            return None

        #-- Actual coordinate must be ahead of the expected minimum
        if d_coord != 0 and np.sign(d_coord) != np.sign(self._end_coord - self._origin_coord):
            return self._create_experiment_error(self.err_too_slow, "You moved too slowly",
                                                 {self.arg_expected_coord: expected_coord, self.arg_actual_coord: coord})

        if self._show_guide:
            # Get the coordinate that the mouse/finger should reach shortly
            coord_expected_soon = self.get_expected_coord_at_time(time + self._guide_warning_time_delta)

            # check if mouse/finger already reached this coordinate
            reached_expected_soon = d_coord == 0 or np.sign(coord - coord_expected_soon) == np.sign(self._end_coord - self._origin_coord)

            # set guide color accordingly
            self._guide.show(expected_coord, GlobalSpeedGuide.LineMode.OK if reached_expected_soon else GlobalSpeedGuide.LineMode.Error)

        return None

    def _assert_initialized(self, value, attr_name):
        if value is None:
            raise trajtracker.InvalidStateError("{:}.check_xyt() was called before {:} was initalized".format(type(self).__name__, attr_name))

    #----------------------------------------------------------------------------------
    # Get the coordinate expected
    #
    def get_expected_coord_at_time(self, time):
        """
        Return the minimnal coordinate (x or y, depending on axis) that should be obtained in a given time
        """

        total_distance = self._end_coord - self._origin_coord

        remaining_time = time
        result = self._origin_coord
        for milestone in self._milestones:
            ms_duration = milestone.time_percentage * self._max_trial_duration
            ms_distance = milestone.distance_percentage * total_distance
            if remaining_time > ms_duration:
                remaining_time -= ms_duration
                result += ms_distance
            else:
                result += ms_distance * (remaining_time / ms_duration)
                break

        return result

    #========================================================================
    #      Configure
    #========================================================================

    #----------------------------------------------------------
    @property
    def axis(self):
        """
        The ValidationAxis on which speed is validated

        - ValidationAxis.x or ValidationAxis.y: limit the speed in the relevant axis.
        - ValidationAxis.xy: limit the diagonal speed
        """
        return self._axis

    @axis.setter
    @fromXML(_parse_validation_axis)
    def axis(self, value):
        _u.validate_attr_type(self, "axis", value, ValidationAxis)
        if value == ValidationAxis.xy:
            raise ValueError(_u.ErrMsg.attr_invalid_value(self.__class__, "axis", value))

        self._axis = value
        self._log_setter("axis")

    #-----------------------------------------------------------------------------------
    @property
    def origin_coord(self):
        """
        The coordinate (x or y) in which the speed validation starts
        The value of this attribute is a single number
        """
        return self._origin_coord

    @origin_coord.setter
    @fromXML(int)
    def origin_coord(self, value):
        _u.validate_attr_numeric(self, "origin_coord", value, _u.NoneValues.Invalid)
        self._origin_coord = value
        self._log_setter("origin_coord")

    #-----------------------------------------------------------------------------------
    @property
    def end_coord(self):
        """
        The coordinate (x or y) in which the speed validation end (i.e., end-of-trial coordinate)
        The value of this attribute is a single number
        """
        return self._end_coord

    @end_coord.setter
    @fromXML(int)
    def end_coord(self, value):
        _u.validate_attr_numeric(self, "end_coord", value, _u.NoneValues.Invalid)
        self._end_coord = value
        self._log_setter("end_coord")


    #-----------------------------------------------------------------------------------
    @property
    def grace_period(self):
        """The grace period in the beginning of each trial, during which speed is not validated (in seconds)."""
        return self._grace_period

    @grace_period.setter
    @fromXML(float)
    def grace_period(self, value):
        value = _u.validate_attr_numeric(self, "grace_period", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_not_negative(self, "grace_period", value)
        self._grace_period = value
        self._log_setter("grace_period")

    #-----------------------------------------------------------------------------------
    @property
    def max_trial_duration(self):
        """The maximal duration of a trial (in seconds)."""
        return self._max_trial_duration

    @max_trial_duration.setter
    @fromXML(int)
    def max_trial_duration(self, value):
        value = _u.validate_attr_numeric(self, "max_trial_duration", value, _u.NoneValues.ChangeTo0)
        _u.validate_attr_positive(self, "max_trial_duration", value)
        self._max_trial_duration = value
        self._log_setter("max_trial_duration")

    #-----------------------------------------------------------------------------------

    _errmsg_milestones_not_percentage = "trajtracker error: invalid {0} for {1}.milestones[{2}]: expecting a number between 0 and 1"

    @property
    def milestones(self):
        """
        This attribute indicates how the overall speed limit (:attr:`~trajtracker.validators.GlobalSpeedValidator.max_trial_duration`)
        should be interpolated.

        By default, the interpolation is linear. But you can define several milestones - e.g., "mouse/finger must complete X%
        of the way within Y% of the trial's total duration". The milestones split the trials into sections and define the
        speed goal per section. Within each section, the interpolation is linear.

        Each milestone is defined by the duration and distance of the relevant section, specified as the percentage
        out of the total trial duration / total movement distance. The durations and distances of all milestones must
        sum to 1.0 (= 100%).

        This property is an array of milestones. Each of them is a GlobalSpeedValidator.Milestone object (but when setting the
        property value, you can use a (time, distance) tuple/list instead).
        """
        return list(self._milestones)

    @milestones.setter
    @fromXML(_parse_xml_milestones, raw_xml=True)
    def milestones(self, value):
        if value is None:
            value = []

        _u.validate_attr_anylist(self, "milestones", value)

        total_time = 0
        total_distance = 0

        milestones = []
        for i in range(len(value)):
            milestone = value[i]

            _u.validate_attr_type(self, "milestones[{:}]".format(i), milestone, (GlobalSpeedValidator.Milestone, tuple, list))

            if not isinstance(milestone, GlobalSpeedValidator.Milestone):
                #-- convert tuple/list to milestone
                if len(milestone) != 2:
                    raise ValueError("trajtracker error: {:}.milestones[{:}] should be either a Milestone object or a (time,distance) tuple/list. Invalid value: {:}".format(type(self).__name__, i, milestone))
                milestone = GlobalSpeedValidator.Milestone(milestone[0], milestone[1])

            if not isinstance(milestone.distance_percentage, numbers.Number):
                raise ValueError(GlobalSpeedValidator._errmsg_milestones_not_percentage.format("distance_percentage", type(self).__name__, i))
            if not (0 < milestone.distance_percentage <= 1):
                raise ValueError(GlobalSpeedValidator._errmsg_milestones_not_percentage.format("distance_percentage", type(self).__name__, i))

            if not isinstance(milestone.time_percentage, numbers.Number):
                raise ValueError(GlobalSpeedValidator._errmsg_milestones_not_percentage.format("time_percentage", type(self).__name__, i))
            if not (0 < milestone.time_percentage <= 1):
                raise ValueError(GlobalSpeedValidator._errmsg_milestones_not_percentage.format("time_percentage", type(self).__name__, i))
            if milestone.distance_percentage <= total_distance:
                raise ValueError("trajtracker error: {:}.milestones[{:}] is invalid - the distance specified ({:}) must be later than in the previous milestone".format("distance_percentage", type(self).__name__, i, milestone.time_percentage))

            total_time += milestone.time_percentage
            total_distance += milestone.distance_percentage

            if total_time > 1:
                raise ValueError("trajtracker error: {:}.milestones is invalid - the total time of all milestones exceeds 1.0".format(type(self).__name__))
            if total_distance > 1:
                raise ValueError("trajtracker error: {:}.milestones is invalid - the total distance of all milestones exceeds 1.0".format(type(self).__name__))

            milestones.append(GlobalSpeedValidator.Milestone(milestone.time_percentage, milestone.distance_percentage))

        if total_time < 1:
            raise ValueError(
                "trajtracker error: {:}.milestones is invalid - the total time of all milestones sums to {:} rather than to 1.0".format(
                    type(self).__name__, total_time))
        if total_distance < 1:
            raise ValueError(
                "trajtracker error: {:}.milestones is invalid - the total distance of all milestones sums to {:} rather than to 1.0".format(
                    type(self).__name__, total_distance))

        self._milestones = np.array(milestones)


    #-------------------------------------------------------------
    @property
    def show_guide(self):
        """
        Whether to visualize the speed limit as a moving line (bool).
        If you show the guide, please note the way it's being presented -
        See :attr:`~trajtracker.validators.GlobalSpeedValidator.do_present_guide`
        """
        return self._show_guide

    @show_guide.setter
    @fromXML(bool)
    def show_guide(self, show):
        _u.validate_attr_type(self, "show_guide", show, bool)
        self._show_guide = show

    #-------------------------------------------------------------
    @property
    def guide_warning_time_delta(self):
        """
        If the time difference between the mouse/finger current coordinate and the required coordinate is
        less than this value, the visual line guide will change its color.
        """
        return self._guide_warning_time_delta

    @guide_warning_time_delta.setter
    @fromXML(float)
    def guide_warning_time_delta(self, value):
        _u.validate_attr_type(self, "guide_warning_time_delta", value, numbers.Number)
        _u.validate_attr_not_negative(self, "guide_warning_time_delta", value)
        self._guide_warning_time_delta = value

    #-------------------------------------------------------------
    @property
    def guide_line_length(self):
        """
        The length of the speed guide line (int)
        """
        return self._guide_line_length

    @guide_line_length.setter
    @fromXML(int)
    def guide_line_length(self, value):
        _u.validate_attr_type(self, "guide_line_length", value, numbers.Number, none_allowed=True)
        if value is not None:
            _u.validate_attr_positive(self, "guide_line_length", value)
        self._guide_line_length = value
        self._guide = GlobalSpeedGuide(self)


    #-------------------------------------------------------
    @property
    def do_present_guide(self):
        """
        If the guide line is shown, this determines the mechanism used to present it:

        - True: the validator itself will call present() for the stimulus
        - False: the validator will update the stimulus position and color, but the main program
           should take care of present()ing validator.guide.stimulus
        """
        return None if self._guide is None else self._guide.do_present

    @do_present_guide.setter
    @fromXML(bool)
    def do_present_guide(self, value):
        if self._guide is not None:
            self._guide.do_present = value


    #-------------------------------------------------------------
    @property
    def guide(self):
        """
        An object (trajtracker.validators.GlobalSpeedGuide) that takes care of showing a visual guide for the speed limit (read-only property)
        """
        return self._guide



#==========================================================================================
# Show a moving line to visualize the validator's speed
#==========================================================================================

class GlobalSpeedGuide(trajtracker._TTrkObject):
    """
    This class displays a moving line that visualizes the global speed limit.

    """

    LineMode = Enum("LineMode", "Grace OK Error")


    def __init__(self, validator):
        """
        Constructor

        :param validator: See :class:`~trajtracker.validators.GlobalSpeedValidator`
        """

        super(GlobalSpeedGuide, self).__init__()
        self._validator = validator

        self._initialized = False
        self._guide_line = None

        self.line_width = 1
        self.colour_grace = (255, 255, 255)
        self.colour_ok = (0, 255, 0)
        self.colour_err = (255, 0, 0)
        self.visible = False

        self._initialized = True
        self._create_guide_line()


    #--------------------------------------------------
    def _create_guide_line(self):

        if not self._initialized:
            return

        line_length = self._get_line_length()
        if line_length is None:
            return

        if self._validator.axis == ValidationAxis.x:
            start_pt = (0, -line_length/2)
            end_pt = (0, line_length/2)
        else:
            start_pt = (-line_length/2, 0)
            end_pt = (line_length/2, 0)

        self._guide_line = trajtracker.stimuli.StimulusSelector()
        self._guide_line.add_stimulus(self.LineMode.Grace, self._create_line(start_pt, end_pt, self._colour_grace))
        self._guide_line.add_stimulus(self.LineMode.Error, self._create_line(start_pt, end_pt, self._colour_err))
        self._guide_line.add_stimulus(self.LineMode.OK, self._create_line(start_pt, end_pt, self._colour_ok))

    #--------------------------------------------------
    def _get_line_length(self):
        if self._validator.guide_line_length is not None:
            return self._validator.guide_line_length
        elif xpy._internals.active_exp.screen is None:
            return None
        elif self._validator.axis == ValidationAxis.x:
            return xpy._internals.active_exp.screen.size[1]
        else:
            return xpy._internals.active_exp.screen.size[0]

    #--------------------------------------------------
    def _create_line(self, start_pt, end_pt, color):
        line = xpy.stimuli.Line(start_point=start_pt, end_point=end_pt, line_width=self._line_width, colour=color)
        line.position = (0,0)
        line.preload()

        if self._validator.axis == ValidationAxis.x:
            line_canvas_size = (self._line_width, self._get_line_length())
        else:
            line_canvas_size = (self._get_line_length(), self._line_width)
        canvas = xpy.stimuli.Canvas(size=line_canvas_size)
        line.plot(canvas)
        canvas.preload()

        return canvas


    #=====================================================================================
    #    Runtime API
    #=====================================================================================


    #------------------------------------------------------------------------
    def show(self, coord, line_mode):

        if self._guide_line is None:
            self._create_guide_line()  # try creating again. Maybe the experiment was inactive
            if self._guide_line is None:
                raise trajtracker.InvalidStateError("The visual guide for {:} cannot be created because the experiment is inactive".format(GlobalSpeedValidator.__name__))

        _u.validate_func_arg_type(self, "show", "coord", coord, int)
        _u.validate_func_arg_type(self, "show", "line_mode", line_mode, self.LineMode)

        self._guide_line.activate(line_mode)

        pos = (coord, 0) if self._validator.axis == ValidationAxis.x else (0, coord)
        self._guide_line.position = pos
        self._guide_line.present(clear=False, update=False)


    #--------------------------------------------------------------------------
    @property
    def stimulus(self):
        return self._guide_line


    #=====================================================================================
    #    Configure
    #=====================================================================================

    #-------------------------------------------------------
    @property
    def visible(self):
        """ Whether the speed guide is currently visible or not """
        return self._visible

    @visible.setter
    def visible(self, value):
        _u.validate_attr_type(self, "visible", value, bool)
        self._visible = value


    #-------------------------------------------------------
    @property
    def do_present(self):
        """
        Whether the line will be present()ed by the validator.
        If False: the line's positon will be updated, but you need to take care yourself to continuously
        present() the object returned by self.stimulus
         """
        return self._do_present

    @do_present.setter
    def do_present(self, value):
        _u.validate_attr_type(self, "do_present", value, bool)
        self._do_present = value


    #-------------------------------------------------------
    @property
    def colour_grace(self):
        """ The guiding line's color during the validator's grace period """
        return self._colour_grace

    @colour_grace.setter
    def colour_grace(self, value):
        _u.validate_attr_rgb(self, "colour_grace", value)
        self._colour_grace = value
        self._create_guide_line()

    #--------------------------
    @property
    def colour_ok(self):
        """ The guiding line's color when the mouse/finger is moving properly """
        return self._colour_ok

    @colour_ok.setter
    def colour_ok(self, value):
        _u.validate_attr_rgb(self, "colour_ok", value)
        self._colour_ok = value
        self._create_guide_line()

    #--------------------------
    @property
    def colour_err(self):
        """ The guiding line's color when the mouse/finger is moving an invalid speed """
        return self._colour_err

    @colour_err.setter
    def colour_err(self, value):
        _u.validate_attr_rgb(self, "colour_err", value)
        self._colour_err = value
        self._create_guide_line()

    #-------------------------------------------------------
    @property
    def line_width(self):
        """ The guiding line's width """
        return self._line_width

    @line_width.setter
    def line_width(self, value):
        _u.validate_attr_type(self, "line_width", value, int)
        self._line_width = value
        self._create_guide_line()
