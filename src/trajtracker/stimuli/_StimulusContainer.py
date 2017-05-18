"""

Stimulus container: holds several stimuli, and can present them all

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

from operator import itemgetter

import expyriment as xpy

import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u


class StimulusContainer(ttrk.TTrkObject, ttrk.events.OnsetOffsetObj):


    #----------------------------------------------------------
    def __init__(self, name=None):
        """
        Constructor
        
        :param name: A name that identifies this container (this is used only to print in log messages)   
        """
        super(StimulusContainer, self).__init__()
        self._name = name
        self._stimuli = {}
        self._non_recurring_callbacks = []
        self._recurring_callbacks = {}


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

        if self._should_log(ttrk.log_trace):
            self._log_write("Present,stimuli={:}".format(";".join([str(s['id']) for s in visible_stims])))

        if len(visible_stims) == 0:
            #-- If no stimuli to present: just clear/update
            if self._should_log(ttrk.log_debug):
                self._log_write("{:}.present(clear={:}, update={:}): no visible stimuli".format(self._myname(), clear, update))

            if clear:
                _u.display_clear()
            if update:
                _u.display_update()

        else:
            #-- Present all stimuli
            for i in range(len(visible_stims)):
                c = clear and i == 0
                u = update and i == len(visible_stims) - 1
                visible_stims[i]['stimulus'].present(clear=c, update=u)

                if self._should_log(ttrk.log_debug):
                    self._log_write("{:}.present(clear={:}, update={:}) stimulus #{:}".format(self._myname(), visible_stims[i]['order'], c, u), True)

        self._invoke_callbacks(visible_stims)


    #-------------------------------------------------------
    def _invoke_callbacks(self, visible_stims):
        if len(self._recurring_callbacks) == 0 and len(self._non_recurring_callbacks) == 0:
            return

        present_time = ttrk.utils.get_time()
        visible_stim_ids = tuple(s['id'] for s in visible_stims)
        all_listeners = list(self._recurring_callbacks.values()) + self._non_recurring_callbacks
        for listener in all_listeners:
            listener(self, visible_stim_ids, present_time)
        self._non_recurring_callbacks = []


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
    def remove(self, stimulus_id):
        """
        Remove a stimulus from the container
        
        :param stimulus_id: The ID to remove 
        :return: True if removed, False if not found
        """

        if stimulus_id not in self._stimuli:
            return False

        del self._stimuli[stimulus_id]
        return True


    #----------------------------------------------------------
    def register_callback(self, callback_func, recurring=False, func_id=None):
        """
        Register a "present callback" - a function that should be called when the StimulusContainer is present()ed
        
        :param callback_func: A function or another callable object, which will be called. 
                         This function takes these arguments -
                         
                         1. The StimulusContainer object
                         2. a tuple with the IDs of the stimuli that were actually presented (i.e., stimuli 
                            that had stim.visible == True)
                         3. The time when present() returned
                            
        :param recurring: True = invoke the function on each present() call. False = Invoke the function only 
                          on the next present(), and then forget this function.
                          
        :param func_id: A logical ID for a recurring function (it can be used to unregister the function later) 
        """

        _u.validate_func_arg_type(self, "register_callback", "callback_func", callback_func, ttrk.TYPE_CALLABLE)
        _u.validate_func_arg_type(self, "register_callback", "recurring", recurring, bool)

        if recurring:
            if func_id == "":
                func_id = None
            _u.validate_func_arg_type(self, "register_callback", "func_id", func_id, str)
            self._recurring_callbacks[func_id] = callback_func

        else:
            self._non_recurring_callbacks.append(callback_func)


    #----------------------------------------------------------
    def unregister_recurring_callback(self, func_id):
        """
        Unregister a recurring listener function that was previously registered via 
        :func:`~trajtracker.stimuli.StimulusContainer.register_callback`
        
        :param func_id: The function ID that was provided to :func:`~trajtracker.stimuli.StimulusContainer.register_callback` 
        :return: *True* if unregistered, *False* if there is no registered recurring function with the given func_id 
        """
        _u.validate_func_arg_type(self, "unregister_recurring_callback", "func_id", func_id, str)

        if func_id in self._recurring_callbacks:
            del self._recurring_callbacks[func_id]
            return True
        else:
            return False


    #----------------------------------------------------------
    def unregister_non_recurring_callbacks(self):
        """
        Clear all non-recurring listeners that were previously registered
        """
        self._non_recurring_callbacks = []


    #----------------------------------------------------------
    @property
    def position(self):
        raise ttrk.TrajTrackerError("This object has no 'position' method")

    @position.setter
    def position(self, value):
        raise ttrk.TrajTrackerError("This object has no 'position' method")


    #----------------------------------------------------------
    def __getitem__(self, item):
        return self._stimuli[item]['stimulus']

    def __str__(self):
        return "{:}[{:}]".format(_u.get_type_name(self), ",".join([str(k) for k in self._stimuli.keys()]))

    #----------------------------------------------------------
    def _myname(self):
        if self._name is None:
            return _u.get_type_name(self)
        else:
            return "{:}({:})".format(_u.get_type_name(self), self._name)
