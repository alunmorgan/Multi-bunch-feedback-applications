from time import sleep

from Common import machineEnvironment, mbfGetThenPut, mbfSystemConfig, saveToArchive
from cothread.catools import caGet, caPut
from scipy.io import savemat


def mbfGrowdampCapture(mbf_axis, additional_save_location=None):
    """Gathers data on the machine environment.
    Runs a growdamp experiment on an already setup system.
    Saves the resultant data.
     Args:
        mbf_axis (str): Selects which MBF axis to work on (x, y, s).
        additional_save_location (str): Full path to additional save location.
     Returns:
        growdamp (dict): data structure containing the experimental
                           results and the machine conditions.
                           [optional output]
     Example: growdamp = mbf_growdamp_capture('x')"""

    if (
        not mbf_axis == "x"
        and not mbf_axis == "y"
        and not mbf_axis == "s"
        and not mbf_axis == "tx"
        and not mbf_axis == "ty"
        and not mbf_axis == "X"
        and not mbf_axis == "Y"
        and not mbf_axis == "S"
        and not mbf_axis == "TX"
        and not mbf_axis == "TY"
    ):
        raise ValueError(
            "".join(
                (
                    "mbf_growdamp_capture: ",
                    "Incorrect value axis given ",
                    "(should be x, y or s. ",
                    "OR tx, ty if testing)",
                )
            )
        )

    [root_string, _1, pv_names, _2] = mbfSystemConfig
    root_string = root_string[0]

    # Generate the base PV name.
    pv_head = pv_names["hardware_names"][mbf_axis]
    if mbf_axis == "x" or mbf_axis == "y" or mbf_axis == "X" or mbf_axis == "Y":
        pv_head_mem = pv_names["hardware_names"]["T"]
    elif mbf_axis == "s":
        pv_head_mem = pv_names["hardware_names"]["L"]
    elif mbf_axis == "tx" or mbf_axis == "ty" or mbf_axis == "TX" or mbf_axis == "TY":
        pv_head_mem = pv_names["hardware_names"]["lab"]

    caPut("".join((pv_head_mem, pv_names["tails"]["triggers"]["MEM"]["disarm"])), 1)
    # Arm the memory so that it cycles. This means that all the status PV are
    # updated.
    # Otherwise the code will say the memory is not ready as the status is
    # stale.
    caPut("".join((pv_head_mem, pv_names["tails"]["triggers"]["MEM"]["arm"])), 1)
    sleep(2)  # Letting the hardware sort itself out.
    temp1 = caGet("".join((pv_head_mem, pv_names["tails"]["TRG"]["memory_status"])))
    if temp1 == "Idle":
        mbfGetThenPut(
            "".join((pv_head_mem, pv_names["tails"]["triggers"]["MEM"]["arm"])), 1
        )
    else:
        raise ValueError("Memory is not ready please try again")

    # getting general environment data.
    growdamp = machineEnvironment()
    # Add the axis label to the data structure.
    growdamp["ax_label"] = mbf_axis
    # construct name and add it to the structure
    growdamp["base_name"] = "".join(("Growdamp_", growdamp["ax_label"], "_axis"))

    # Disarm, so that the current settings will be picked up upon arming.
    caPut("".join((pv_head, pv_names["tails"]["triggers"]["SEQ"]["disarm"])), 1)

    # Getting settings for growth, natural damping, and active damping.
    exp_state_names = ["spacer", "act", "nat", "growth"]
    for n in range(4):
        # Getting the number of turns
        growdamp["".join((exp_state_names[n], "_turns"))] = caGet(
            [
                pv_head,
                pv_names["tails"]["Sequencer"]["Base"],
                n,
                pv_names["tails"]["Sequencer"]["count"],
            ]
        )
        # Getting the number of turns each point dwells at
        growdamp["".join((exp_state_names[n], "_dwell"))] = caGet(
            [
                pv_head,
                pv_names["tails"]["Sequencer"]["Base"],
                n,
                pv_names["tails"]["Sequencer"]["dwell"],
            ]
        )
        # Getting the gain
        growdamp["".join((exp_state_names[n], "_gain"))] = caGet(
            [
                pv_head,
                pv_names["tails"]["Sequencer"]["Base"],
                n,
                pv_names["tails"]["Sequencer"]["gain"],
            ]
        )

    # Trigger the measurement
    if (
        mbf_axis == "x"
        or mbf_axis == "s"
        or mbf_axis == "tx"
        or mbf_axis == "X"
        or mbf_axis == "S"
        or mbf_axis == "TX"
    ):
        chan = 0
    elif mbf_axis == "y" or mbf_axis == "ty":
        chan = 1

    if mbf_axis == "s" or mbf_axis == "S":
        mem_lock = 180
    else:
        mem_lock = 10

    # Arm
    caPut("".join((pv_head, pv_names["tails"]["triggers"]["SEQ"]["arm"])), 1)
    # Trigger
    caPut("".join((pv_head_mem, pv_names["tails"]["triggers"]["soft"])), 1)
    growdamp["data"], growdamp["data_freq"], _3 = mbf_read_det(
        pv_head_mem, "axis", chan, "lock", mem_lock
    )

    turn_count = 1250 * 400
    turn_offset = 0
    growdamp["bunch_motion"] = mbf_read_mem(
        pv_head_mem, turn_count, "offset", turn_offset, "channel", 0, "lock", 60
    )
    # saving the data to a file
    if (
        mbf_axis == "x"
        or mbf_axis == "y"
        or mbf_axis == "s"
        or mbf_axis == "X"
        or mbf_axis == "Y"
        or mbf_axis == "S"
    ):
        #     only save if not on test system
        saveToArchive(root_string, growdamp)
        if additional_save_location is not None:
            savemat(additional_save_location, growdamp)

    return growdamp
