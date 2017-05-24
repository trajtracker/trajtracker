

from __future__ import division

import time

import expyriment as xpy


import trajtracker as ttrk
# noinspection PyProtectedMember
import trajtracker._utils as _u
import trajtracker.utils as u
from trajtracker.paradigms.common import FINGER_STARTED_MOVING


#---------------------------------------------------------------------
def get_subject_name_id():
    """
    Get the name (optional) and the initials of the subject
    """

    name_input = xpy.io.TextInput("Subject name - optional:", length=40,
                                  message_colour=xpy.misc.constants.C_WHITE)
    subj_name = name_input.get()

    if subj_name == "":
        default_id = ""
    else:
        name_elems = subj_name.lower().split(" ")
        default_id = "".join([e[0] for e in name_elems if len(e) > 0])

    id_input = xpy.io.TextInput("Subject ID (initials) - mandatory:", length=10,
                                message_colour=xpy.misc.constants.C_WHITE)
    while True:
        subj_id = id_input.get(default_id)
        if subj_id != "":
            break


    return subj_id, subj_name


#----------------------------------------------------------------
def create_start_point(exp_info):
    """
    Create the "start" area, with default configuration

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    start_area_size = config.start_point_size
    start_area_position = (config.start_point_x_coord,
                           - (exp_info.screen_size[1] / 2 - start_area_size[1] / 2))

    exp_info.start_point = ttrk.movement.RectStartPoint(size=start_area_size,
                                                        position=start_area_position,
                                                        rotation=config.start_point_tilt,
                                                        colour=config.start_point_colour)

    exp_info.stimuli.add(exp_info.start_point.start_area, "start_point")

    exp_info.exp_data['TrajZeroCoordX'] = start_area_position[0]
    exp_info.exp_data['TrajZeroCoordY'] = start_area_position[1] + start_area_size[1]/2
    exp_info.exp_data['TrajPixelsPerUnit'] = 1


# ----------------------------------------------------------------
def create_traj_tracker(exp_info):
    """
    Create the object that tracks the trajectory

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    if not exp_info.config.save_results:
        return

    curr_time = time.strftime("%Y%m%d_%H%M", time.localtime())
    exp_info.trials_out_filename = "trials_{:}_{:}.csv".format(exp_info.subject_id, curr_time)
    exp_info.traj_out_filename = "trajectory_{:}_{:}.csv".format(exp_info.subject_id, curr_time)
    exp_info.session_out_filename = "session_{:}_{:}.xml".format(exp_info.subject_id, curr_time)

    traj_file_path = xpy.io.defaults.datafile_directory + "/" + exp_info.traj_out_filename
    exp_info.trajtracker = ttrk.movement.TrajectoryTracker(traj_file_path)
    exp_info.trajtracker.enable_event = FINGER_STARTED_MOVING
    exp_info.trajtracker.disable_event = ttrk.events.TRIAL_ENDED


#----------------------------------------------------------------
def create_validators(exp_info, direction_validator, global_speed_validator, inst_speed_validator, zigzag_validator):
    """
    Create movement validators, with default configuration.

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo

    :param direction_validator: Whether to include the validator that enforces upward-only movement
    :type direction_validator: bool

    :param global_speed_validator: Whether to validate that the finger reaches each y coordinate in time
    :type global_speed_validator: bool

    :param inst_speed_validator: Whether to validate the finger's instantaneous speed
    :type inst_speed_validator: bool

    :param zigzag_validator: Whether to prohibit zigzag movement
    :type zigzag_validator: bool

    :return: tuple: (list_of_validators, dict_of_validators)
    """

    _u.validate_func_arg_type(None, "create_validators", "direction_validator", direction_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "global_speed_validator", global_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "inst_speed_validator", inst_speed_validator, bool)
    _u.validate_func_arg_type(None, "create_validators", "zigzag_validator", zigzag_validator, bool)

    config = exp_info.config

    if direction_validator:
        v = ttrk.validators.MovementAngleValidator(
            min_angle=config.dir_validator_min_angle,
            max_angle=config.dir_validator_max_angle,
            calc_angle_interval=config.dir_validator_calc_angle_interval)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'direction')


    if global_speed_validator:
        v = ttrk.validators.GlobalSpeedValidator(
            origin_coord=exp_info.start_point.position[1] + exp_info.start_point.start_area.size[1] / 2,
            end_coord=exp_info.numberline.position[1],
            grace_period=config.grace_period,
            max_trial_duration=config.max_trial_duration,
            milestones=config.global_speed_validator_milestones,
            show_guide=config.speed_guide_enabled)
        v.do_present_guide = False
        v.movement_started_event = FINGER_STARTED_MOVING
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'global_speed')
        exp_info.stimuli.add(v.guide.stimulus, "speed_guide", visible=False)


    if inst_speed_validator:
        v = ttrk.validators.InstantaneousSpeedValidator(
            min_speed=config.min_inst_speed,
            grace_period=config.grace_period,
            calculation_interval=0.05)
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'inst_speed')


    if zigzag_validator:
        v = ttrk.validators.NCurvesValidator(max_curves_per_trial=config.max_zigzags)
        v.direction_monitor.min_angle_change_per_curve = config.zigzag_validator_min_angle_change_per_curve
        v.enable_event = FINGER_STARTED_MOVING
        v.disable_event = ttrk.events.TRIAL_ENDED
        exp_info.add_validator(v, 'zigzag')


#----------------------------------------------------------------
def create_textbox_target(exp_info):
    """
    Create a textbox to serve as the target. This text box supports multiple texts (so it can be used
    for RSVP, priming, etc.)

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    target = _create_textbox_target_impl(exp_info, "target")

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else FINGER_STARTED_MOVING
    target.onset_time = config.target_onset_time
    target.duration = config.target_duration
    target.last_stimulus_remains = config.text_target_last_stimulus_remains

    exp_info.text_target = target
    exp_info.add_event_sensitive_object(target)


#----------------------------------------------------------------
def create_textbox_fixation(exp_info):
    """
    Create a textbox to serve as the fixation. 

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    y, height = get_target_y(exp_info)

    text = exp_info.config.fixation_text

    fixation = xpy.stimuli.TextBox(
        text='' if text is None else text,
        size=(config.text_target_width, int(height)),
        position=(config.text_target_x_coord, y),
        text_font=config.text_target_font,
        text_colour=config.text_target_colour,
        text_justification=config.text_target_justification
    )

    hsr = u.get_font_height_to_size_ratio(fixation.text_font)
    font_size = int(height / hsr * config.text_target_height)
    fixation.text_size = font_size
    ttrk.log_write("Fixation font size = {:}, height = {:.1f} pixels".format(font_size, font_size*hsr), print_to_console=True)

    fixation.preload()

    exp_info.fixation = fixation


#----------------------------------------------------------------
def _create_textbox_target_impl(exp_info, role):

    config = exp_info.config

    target = ttrk.stimuli.MultiTextBox()

    y, height = get_target_y(exp_info)
    target.position = (config.text_target_x_coord, y)
    target.text_font = config.text_target_font
    target.size = (config.text_target_width, int(height))
    target.text_colour = config.text_target_colour
    target.text_justification = config.text_target_justification

    if not (0 < config.text_target_height <= 1):
        raise ttrk.ValueError("Invalid config.text_target_height ({:}): value must be between 0 and 1, check out the documentation".format(config.text_target_height))

    hsr = u.get_font_height_to_size_ratio(target.text_font)
    font_size = int(height / hsr * config.text_target_height)
    target.text_size = font_size
    ttrk.log_write("{:} font size = {:}, height = {:.1f} pixels".format(role, font_size, font_size*hsr), print_to_console=True)

    return target


#----------------------------------------------------------------
def create_generic_target(exp_info):
    """
    Create a handler for non-text targets (pictures, shapes, etc.). This object supports multiple targets
    (so it can be used for RSVP, priming, etc.)

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    y, height = get_target_y(exp_info)
    target = ttrk.stimuli.MultiStimulus(position=(config.generic_target_x_coord, y))

    target.onset_event = ttrk.events.TRIAL_STARTED if config.stimulus_then_move else FINGER_STARTED_MOVING
    target.onset_time = config.target_onset_time
    target.duration = config.target_duration
    target.last_stimulus_remains = config.generic_target_last_stimulus_remains

    exp_info.generic_target = target
    exp_info.add_event_sensitive_object(target)


#----------------------------------------------------------------
def create_fixation(exp_info):
    """
    Create the fixation shape

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    fixtype = exp_info.config.fixation_type.lower()

    if fixtype is None:
        pass

    if fixtype == 'cross':
        create_fixation_cross(exp_info)

    elif fixtype == 'text':
        create_textbox_fixation(exp_info)

    else:
        raise ttrk.ValueError("Invalid config.fixation_type ({:})".format(fixtype))


#----------------------------------------------------------------
def create_fixation_cross(exp_info):
    y, height = get_target_y(exp_info)
    exp_info.fixation = xpy.stimuli.FixCross(size=(30, 30), position=(0, y), line_width=2)
    exp_info.fixation.preload()


#----------------------------------------------------------------
def get_target_y(exp_info):
    """
    Create the y coordinate where the target should be presented 

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    screen_top = exp_info.screen_size[1] / 2
    height = screen_top - exp_info.numberline.position[1] - exp_info.config.stimulus_distance_from_top - 1
    y = int(screen_top - exp_info.config.stimulus_distance_from_top - height / 2)
    return y, height


#----------------------------------------------------------------
def create_errmsg_textbox(exp_info):
    """
    Create a stimulus that can show the error messages

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """

    config = exp_info.config

    exp_info.errmsg_textbox = xpy.stimuli.TextBox(
        text="",
        size=config.errmsg_textbox_size,
        position=config.errmsg_textbox_coords,
        text_font=config.errmsg_textbox_font_name,
        text_size=config.errmsg_textbox_font_size,
        text_colour=config.errmsg_textbox_font_colour)


#----------------------------------------------------------------
def register_to_event_manager(exp_info):
    """
    Register all event-sensitive objects to the event manager

    :param exp_info: The experiment-level objects
    :type exp_info: trajtracker.paradigms.num2pos.ExperimentInfo
    """
    for obj in exp_info.event_sensitive_objects:
        exp_info.event_manager.register(obj)


#------------------------------------------------
def load_sound(config, filename):
    sound = xpy.stimuli.Audio(config.sounds_dir + "/" + filename)
    sound.preload()
    return sound
