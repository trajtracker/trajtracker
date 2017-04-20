"""

TrajTracker - general stuff for all paradigms

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import expyriment as xpy


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
        default_id = "".join([e[0] for e in name_elems])

    id_input = xpy.io.TextInput("Subject ID (initials) - mandatory:", length=10,
                                message_colour=xpy.misc.constants.C_WHITE)
    while True:
        subj_id = id_input.get(default_id)
        if subj_id != "":
            break


    return subj_id, subj_name