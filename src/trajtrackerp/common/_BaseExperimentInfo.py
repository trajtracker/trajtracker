"""
Static elements common to several experiment types

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

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u


class BaseExperimentInfo(object):
    """
    All objects relevant to this experiment
    """

    def __init__(self, config, xpy_exp, subject_id, subject_name):

        # -- Static elements - remain throughout the experiment

        self._config = config

        #: Expyriment's "Experiment" object
        self.xpy_exp = xpy_exp

        #: Subject ID (As entered in Expyriment's welcome screen)
        self.subject_id = subject_id

        #: Subject name (as entered in the number-to-position app's welcome screen)
        self.subject_name = subject_name

        self._text_target = None
        self._generic_target = None
        self._start_point = None
        self._errmsg_box = None
        self._trajtracker = None
        self._trajectory_sensitive_objects = []
        self._event_sensitive_objects = []

        #: A :class:`~trajtracker.stimuli.StimulusContainer` object, containing all stimuli.
        self.stimuli = ttrk.stimuli.StimulusContainer("main")

        #: An :class:`~trajtracker.events.EventManager` object (responsible for handling the app's events)
        self.event_manager = ttrk.events.EventManager()

        #: Sound to play on trial failure
        #: (`expyriment.stimuli.Audio <http://docs.expyriment.org/expyriment.stimuli.Audio.html>`_)
        self.sound_err = None

        #: Sound/s to play when the trial succeeded
        #: (`expyriment.stimuli.Audio <http://docs.expyriment.org/expyriment.stimuli.Audio.html>`_)
        #:
        #: This has more than one entry in case you used several sounds (configured by Config.sound_by_accuracy)
        self.sounds_ok = None

        self.fixation = None

        # -- Runtime elements: change during the experiment

        #: The list of trials (loaded from the CSV file)
        self.trials = None
        self.exported_trial_csv_columns = []

        #: Time when the session started.
        self.session_start_time = None

        #: Time when the session started, as string
        self.session_start_localtime = None

        # -- Results: per experiment, per trial

        #: A dict with the experiment-level results
        self.exp_data = {}

        #: Name of session.xml results file
        self.session_out_filename = None

        #: Name of trials.csv results file
        self.trials_out_filename = None

        #: Name of trajectory.csv results file
        self.traj_out_filename = None

        #: a DictWriter for the trials.csv file
        self.trials_file_writer = None

        #: A :class:`~trajtracker.stimuli.Slider` for measuing subjective confidence rating
        self.confidence_slider = None


    #---------------------------------------------------------------
    @property
    def trajectory_sensitive_objects(self):
        """
        A list of all objects that need to know about the finger movement 
        (e.g. :class:`~trajtracker.movement.TrajectoryTracker` and the validators).
        For each of these objects, obj.update_xyt() will be called on each frame.
        """
        return self._trajectory_sensitive_objects


    def add_trajectory_sensitive_object(self, obj):
        """
        Add an object to :attr:`~trajtrackerp.num2pos.trajectory_sensitive_objects`
        """
        self._trajectory_sensitive_objects.append(obj)


    #---------------------------------------------------------------
    @property
    def event_sensitive_objects(self):
        """
        A list of objects that need to be registered to the :class:`~trajtracker.events.EventManager`
        """
        return self._event_sensitive_objects

    def add_event_sensitive_object(self, obj):
        """
        Add an object to :attr:`~trajtrackerp.num2pos.event_sensitive_objects`
        """
        self._event_sensitive_objects.append(obj)

    # ---------------------------------------------------------------
    @property
    def screen_size(self):
        """
        The screen size (width, height)
        :type: tuple 
        """
        return self.xpy_exp.screen.size

    # ---------------------------------------------------------------
    def add_validator(self, validator, name):
        """
        Add a validator to the experiment's set of validators.
        The validator will also be registered in :attr:`~trajtrackerp.num2pos.trajectory_sensitive_objects` 

        :param validator: The validator object
        :param name: The validator will also be saved as "exp_info.validator_<name>"
        """

        self._trajectory_sensitive_objects.append(validator)
        self.add_event_sensitive_object(validator)

        setattr(self, "validator_" + name, validator)
        validator.log_level = ttrk.log_info

    # ---------------------------------------------------------------
    @property
    def text_target(self):
        """
        The target text stimuli

        :type: trajtracker.stimuli.MultiTextBox 
        """
        return self._text_target

    @text_target.setter
    def text_target(self, target):
        if self._text_target is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.text_target cannot be set twice")

        self._text_target = target
        self.stimuli.add(target.stimulus, "text_target")

    # ---------------------------------------------------------------
    @property
    def generic_target(self):
        """
        The target non-text stimuli

        :type: trajtracker.stimuli.MultiStimulis 
        """
        return self._generic_target

    @generic_target.setter
    def generic_target(self, target):
        if self._generic_target is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.generic_target cannot be set twice")

        self._generic_target = target
        self.stimuli.add(target.stimulus, "generic_target")

    #---------------------------------------------------------------
    @property
    def start_point(self):
        """
        The start point
        (a :class:`~trajtracker.movement.StartPoint` or :class:`~trajtracker.movement.RectStartPoint` )   
        """
        return self._start_point

    @start_point.setter
    def start_point(self, spoint):
        self._start_point = spoint

    # ---------------------------------------------------------------
    @property
    def errmsg_textbox(self):
        """
        A text box for showing error messages
        (`expyriment.stimuli.TextBox <http://docs.expyriment.org/expyriment.stimuli.TextBox.html>`_
        or an equivalent stimulus)  
        """
        return self._errmsg_textbox

    @errmsg_textbox.setter
    def errmsg_textbox(self, value):
        self._errmsg_textbox = value
        self.stimuli.add(value, "errmsg", visible=False)

    # ---------------------------------------------------------------
    @property
    def trajtracker(self):
        """
        A :class:`~trajtracker.movement.TrajectoryTracker` object for tracking the finger trajectory
        """
        return self._trajtracker

    @trajtracker.setter
    def trajtracker(self, tracker):
        if self._trajtracker is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.trajtracker cannot be set twice")

        self._trajectory_sensitive_objects.append(tracker)
        self._event_sensitive_objects.append(tracker)
        self._trajtracker = tracker

    # ---------------------------------------------------------------
    @property
    def fixation(self):
        """
        The fixation (a cross / symbol / etc) 
        """
        return self._fixation

    @fixation.setter
    def fixation(self, value):
        self._fixation = value
        if isinstance(value, ttrk.stimuli.FixationZoom):
            self.stimuli.add(value.stimulus, "fixation", visible=True)
        elif value is not None:
            self.stimuli.add(value, "fixation", visible=False)
