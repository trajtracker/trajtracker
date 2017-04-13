"""
Static elements in the number-to-position experiment

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy

import trajtracker as ttrk
import trajtracker._utils as _u


class ExperimentInfo(object):
    """
    All objects relevant to this experiment
    """


    def __init__(self, xpy_exp, config):

        #-- Static elements - remain throughout the experiment

        self.xpy_exp = xpy_exp  # Expyriment's "Experiment" object
        self._config = config

        self._numberline = None
        self._target = None
        self._start_point = None
        self._errmsg_box = None
        self._trajtracker = None
        self._trajectory_sensitive_objects = []

        self.stimuli = ttrk.stimuli.StimulusContainer()
        self.event_manager = ttrk.events.EventManager()

        self.sound_err = None
        self.sounds_ok = None
        self.sounds_ok_max_ep_err = None

        #-- Runtime elements: change during the experiment

        self.trials = None
        self.session_start_time = None

        #-- Results: per experiment, per trial

        self.exp_data = {}

        self.trials_out_filename = None
        self.traj_out_filename = None

        self.trials_file_writer = None


    #---------------------------------------------------------------
    @property
    def config(self):
        """
        :type: trajtracker.paradigms.num2pos.Config  
        """
        return self._config


    #---------------------------------------------------------------
    @property
    def screen_size(self):
        return self.xpy_exp.screen.size


    #---------------------------------------------------------------
    def add_validator(self, validator, name):
        self._trajectory_sensitive_objects.append(validator)
        setattr(self, "validator_" + name, validator)

    #---------------------------------------------------------------
    @property
    def numberline(self):
        return self._numberline

    @numberline.setter
    def numberline(self, nl):
        if self._numberline is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.numberline cannot be set twice")
        self._numberline = nl
        self.stimuli.add(nl, "numberline")

    #---------------------------------------------------------------
    @property
    def target(self):
        """
        The target object
        """
        return self._target

    def set_target(self, target, target_stim):
        """
        Set the target.
        :param target: The object representing the target placeholder on screen (this is not necessarity a visual object)
        :param target_stim: The stimulus to display as a target
        """
        if self._target is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.target cannot be set twice")

        self._target = target
        self.stimuli.add(target_stim, "target", visible=False)


    #---------------------------------------------------------------
    @property
    def start_point(self):
        return self._start_point

    @start_point.setter
    def start_point(self, spoint):
        self._start_point = spoint


    #---------------------------------------------------------------
    @property
    def errmsg_textbox(self):
        return self._errmsg_textbox

    @errmsg_textbox.setter
    def errmsg_textbox(self, value):
        self._errmsg_textbox = value
        self.stimuli.add(value, "errmsg", visible=False)


    #---------------------------------------------------------------
    @property
    def trajtracker(self):
        return self._trajtracker

    @trajtracker.setter
    def trajtracker(self, tracker):
        if self._trajtracker is not None:
            raise ttrk.InvalidStateError("ExperimentInfo.trajtracker cannot be set twice")

        self._trajectory_sensitive_objects.append(tracker)
        self._trajtracker = tracker


    #---------------------------------------------------------------
    @property
    def trajectory_sensitive_objects(self):
        return self._trajectory_sensitive_objects

