"""

Stimulus container: holds several stimuli, and can present them all

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy

import trajtracker
import trajtracker._utils as _u


class StimulusContainer(trajtracker._TTrkObject):
    """
    Maintain several stimuli, and can present them all in one command.

    You can also define some of the stimuli as temporarily invisible.
    """


    def __init__(self):
        super(StimulusContainer, self).__init__()

        self._stimuli = {}


    #==============================================================================
    #     Presentation
    #==============================================================================

    #----------------------------------------------------------
    def present(self, clear=True, update=True):
        """
        Present all visible stimuli in the container
        Stimuli marked as invisible will not be shown

        :param clear: See in `Expyriment <http://docs.expyriment.org/expyriment.stimuli.Rectangle.html#expyriment.stimuli.Rectangle.present>`
        :param update: See in `Expyriment <http://docs.expyriment.org/expyriment.stimuli.Rectangle.html#expyriment.stimuli.Rectangle.present>`
        """

        visible_stims = [stim for stim in self._stimuli.values() if stim.visible]

        for i in range(len(visible_stims)):
            c = clear if i == 0 else False
            u = update if i == len(visible_stims)-1 else False
            visible_stims[i].present(clear=c, update=u)


    #----------------------------------------------------------
    def add(self, stimulus_id, stimulus, visible=True):
        """
        Add a stimulus to the container.

        :param stimulus_id: Stimulus name. Use it later to set the stimulus as visible/invisible.
        :param stimulus: An Expyriment stimulus, or any other object that has a similar present() method
        :param visible: See The stimulus ID (as defined in :func:`~trajtracker.stimuli.StimulusContainer.set_visible`)
        :return:
        """

        _u.validate_func_arg_type(self, "add", "visible", visible, bool)
        if not "present" in dir(stimulus):
            raise TypeError("trajtracker error: invalid stimulus ({:}) in {:}.add() - expecting an expyriment stimulus".format(
                stimulus, type(self).__name__))

        stimulus.visible = visible

        self._stimuli[stimulus_id] = stimulus


    #----------------------------------------------------------
    def __getitem__(self, item):
        return self._stimuli[item]
