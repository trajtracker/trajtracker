"""

Stimulus selector: show one of several stimuli

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment

import trajtracker
import trajtracker._utils as _u


class StimulusSelector(trajtracker._TTrkObject):
    """
    This object keeps several expyriment stimuli, and can define one of them as active.

    You can then handle the active stimulus: present it, modify its position.

    This class is useful when you have a stimulus that can change during a trial, and you want to change the
    stimulus independently of presenting and moving it. For example, support you want to move a rectangle around the
    screen, and make its color flicker between red and green. You can:

    - Define two rectangles with the same size, one red and one green (this is better than repeatedly
      changing the color of a single rectangle, because you don't want to redraw the stimulus on every frame)
    - Wrap the two rectangles as a StimulusSelector object
    - Use a :class:`~trajtracker.movement.StimulusAnimator` to move the stimulus around screen. The animator
      will not control the rectangles directly, but the StimulusSelector
    - Repeatedly call :func:`~trajtracker.movement.StimulusAnimator.update` to move the rectangle, and
      :func:`~trajtracker.stimuli.StimulusSelector.activate` to change its color.
    """

    def __init__(self, stimuli=()):
        """
        Constructor

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
