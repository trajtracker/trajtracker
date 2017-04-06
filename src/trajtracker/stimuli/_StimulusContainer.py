"""

Stimulus container: holds several stimuli, and can present them all

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from operator import itemgetter

import expyriment as xpy

import trajtracker
# noinspection PyProtectedMember
import trajtracker._utils as _u


class StimulusContainer(trajtracker._TTrkObject, trajtracker.events.OnsetOffsetObj):


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

        visible_stims = [stim for stim in self._stimuli.values() if stim['stimulus'].visible]
        visible_stims.sort(key=itemgetter('order'))

        if self._should_log(self.log_trace):
            self._log_write("Present,stimuli={:}".format(";".join([str(s['id']) for s in visible_stims])))

        for i in range(len(visible_stims)):
            c = clear if i == 0 else False
            u = update if i == len(visible_stims)-1 else False
            visible_stims[i]['stimulus'].present(clear=c, update=u)


    #----------------------------------------------------------
    def add(self, stimulus, stimulus_id=None, visible=True):
        """
        Add a stimulus to the container.

        :param stimulus: An Expyriment stimulus, or any other object that has a similar present() method
        :param stimulus_id: Stimulus name. Use it later to set the stimulus as visible/invisible.
                            If not provided or None, an arbitrary ID will be generated.
        :param visible: See The stimulus ID (as defined in :func:`~trajtracker.stimuli.StimulusContainer.set_visible`)
        :return:
        """

        _u.validate_func_arg_type(self, "add", "visible", visible, bool)
        if "present" not in dir(stimulus):
            raise TypeError("trajtracker error: invalid stimulus ({:}) in {:}.add() - expecting an expyriment stimulus".format(
                stimulus, type(self).__name__))

        stimulus.visible = visible

        if stimulus_id is None:
            n = len(self._stimuli)+1
            while True:
                stimulus_id = "stimulus#{:}".format(n)
                if stimulus_id in self._stimuli:
                    n += 1
                else:
                    break


        order = len(self._stimuli)
        if stimulus_id not in self._stimuli:
            order += 1

        self._stimuli[stimulus_id] = dict(id=stimulus_id, stimulus=stimulus, order=order)


    #----------------------------------------------------------
    def __getitem__(self, item):
        return self._stimuli[item]['stimulus']
