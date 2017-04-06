"""

Stimulus selector: show one of several stimuli

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u


# noinspection PyProtectedMember
class StimulusSelector(trajtracker._TTrkObject, trajtracker.events.OnsetOffsetObj):

    def __init__(self, stimuli=()):
        """
        Constructor - invoked when you create a new object by writing StimulusSelector()

        :param stimuli: A list of stimuli to add. Each entry in the list is a (key, stimulus) pair -
                        see :func:`~trajtracker.stimuli.StimulusSelector.add_stimulus`
        """

        super(StimulusSelector, self).__init__()

        self._active_key = None
        self._stimuli = {}

        for key, stim in stimuli:
            self.add_stimulus(key, stim)


    #--------------------------------------------------
    def add_stimulus(self, key, stim):
        """
        Add a stimulus

        :param key: Identifier (logical name) for this stimulus
        :param stim: The actual expyriment stimulus
        """
        self._stimuli[key] = stim


    #--------------------------------------------------
    def _get_stimulus(self, key):
        return self._stimuli[key]


    #--------------------------------------------------
    def activate(self, key):
        """
        Set one of the stimuli as the active one.

        :param key: The key of the stimulus, as set in :func:`~trajtracker.stimuli.StimulusSelector.add_stimulus`
        """
        if key is None or key in self._stimuli:
            if self._should_log(self.log_trace):
                self._log_write("Activate,{:}".format(key), True)
            self._active_key = key
        else:
            raise ValueError("trajtracker error: {:}.select(key={:}) - this stimulus was not defined".format(type(self).__name__, key))


    #--------------------------------------------------
    @property
    def active_stimulus(self):
        """ The expyriment stimulus currently active """
        if self._active_key is None:
            return None
        else:
            return self._stimuli[self._active_key]

    @property
    def selected_key(self):
        return self._active_key

    #--------------------------------------------------
    def present(self, clear=True, update=True):
        """ present the active stimulus """

        self._log_func_enters("present", [clear, update])

        s = self.active_stimulus
        if s is None:
            # Take care of the clear and update
            if clear:
                expyriment._internals.active_exp.screen.clear()
            if update:
                expyriment._internals.active_exp.screen.update()
        else:
            s.present(clear=clear, update=update)


    #--------------------------------------------------
    @property
    def position(self):
        """ The position of the active stimulus """
        s = self.active_stimulus
        return None if s is None else s.position

    @position.setter
    def position(self, value):
        s = self.active_stimulus
        if s is not None:
            s.position = value
