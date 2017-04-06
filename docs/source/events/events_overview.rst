
Working with events
===================

Overview
--------

If your experiment needs to make things appear on screen or disappear from screen during the trial, there are
two ways to go. One way is to take care of it yourself, in the program's event loop. Another way is to use
TrajTracker's event mechanism.

TrajTracker's event mechanism involves the following concepts:

1. **Events**: An event marks a reference time point during a trial. Some events would probably appear in most
trajectory tracking experiments - e.g., "trial started", "trial succeeded", and "finger started moving".
Other events may be very particular to a specific experiment, e.g., "the subject touched the screen the third time".

An event is defined by the :class:`~trajtracker.events.Event` class.

2. **Operations** are things that the experiment program should do in particular times during the experiment -
e.g., show or hide a stimulus, start/stop tracking the finger trajectory, and so on. Operations are defined with
respect to an event - e.g., you can define that a stimulus should appear 200 ms after the "finger started moving"
event.

3. **Event-sensitive objects**: These are TrajTracker objects that can be paired with events - e.g.,
:class:`~trajtracker.stimuli.NumberLine`, :class:`~trajtracker.movement.TrajectoryTracker`, etc.

For event-sensitive objects, you can define the events for which a certain operation should occur. For example,
you can control when a :class:`~trajtracker.movement.TrajectoryTracker` starts and stops tracking
the trajectory by defining :attr:`~trajtracker.movement.TrajectoryTracker.activate_event` and
:attr:`~trajtracker.movement.TrajectoryTracker.deactivate_event`.

4. :class:`~trajtracker.events.EventManager`: This is the object that coordinates between events, operations,
and your program. It is mandatory when using TrajTracker's event mechanism. Typically, your program should have
only one instance of this object. The program notifies the event manager when an event occurs,
and the event manager dispatches this event to the relevant event-sensitive objects
and makes sure that they run the appropriate operations.


Practical information: How to use the event mechanism
-----------------------------------------------------

1. Create an :class:`~trajtracker.events.EventManager`
2. Create event-sensitive objects. Each should be registered using :class:`~trajtracker.events.EventManager`. :meth:`~trajtracker.events.EventManager.register`.
3. Configure the relevant events on each event-sensitive object.
4. Your program should notify the event manager about any event that occurs using the
   :class:`~trajtracker.events.EventManager`. :meth:`~trajtracker.events.EventManager.dispatch_event` method. You should also call
   :class:`~trajtracker.events.EventManager`. :meth:`~trajtracker.events.EventManager.on_frame` very frequently - e.g., in a loop that runs once per frame.

For example:
 .. code-block:: python

  event_manager = EventManager()
  stimulus_container = StimulusContainer()

  traj_tracker = TrajectoryTracker()
  traj_tracker.activate_event = trajtracker.events.EVENT_TRIAL_STARTED
  traj_tracker.deactivate_event = trajtracker.events.EVENT_TRIAL_ENDED

  event_manager.register(traj_tracker)

  # Start the experiment
  for trial in trials:

      event_manager.reset()

      trial_start_time = get_time()
      init_trial()

      present_target()
      event_manager.dispatch_event(trajtracker.events.TRIAL_STARTS, get_time() - trial_start_time)

      while True:  # Loop on each frame

          event_manager.on_frame(get_time() - trial_start_time)

          if trial_should_end():
              break

          stimulus_container.present() # update display and wait one frame


For a more comprehensive example, check out the "Events" samples provided with TrajTracker.


**Notes:**:

- when using event manager to show/hide visual objects, you must put these objects in a
  :class:`~trajtracker.stimuli.StimulusContainer` and use
  :meth:`~trajtracker.stimuli.StimulusContainer.present` to update the display.
- Operation can be timed to the precise moment when an event occurred (as in the example above), or to some
  time later. For example, to start tracking the trajectory 100 ms after the trial started:

  .. code-block:: python

   traj_tracker.activate_event = trajtracker.events.EVENT_TRIAL_STARTED + 0.1

- When several operations are invoked together (following a single call to EventManager.
  :meth:`~trajtracker.events.EventManager.dispatch_event` or :meth:`~trajtracker.events.EventManager.on_frame`),
  the order of invoking them is not guaranteed.


Pre-defined Events
------------------

TrajTracker has several pre-defined events. When using the event mechanism, some of trajtracker's objects
rely on these events, so you should dispatch them on each trial:

TBD

TRIAL_INITIALIZED
TRIAL_STARTED
TRIAL_SUCCEEDED
TRIAL_ERROR

TRIAL_ENDED
