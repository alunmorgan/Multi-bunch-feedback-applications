from time import sleep

from cothread.catools import caput  # type: ignore

from mbf_applications.Common.mbf_get_then_put import mbfGetThenPut
from mbf_applications.Common.mbf_system_config import mbfSystemConfig
from mbf_applications.Growdamp.mbf_set_bank import mbfSetBank
from mbf_applications.Growdamp.mbf_set_state import mbfSetState


def mbfGrowdampSetup(
    mbf_axis,
    tune,
    durations=0,
    dwell=0,
    tune_sweep_range=0,
    tune_offset=0,
    excitation_level=[],
):
    # Sets up the MBF system to be ready for a growdamp measurement.
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
    #       tune (float): Tune of the machine.
    #       varargin: other settings (dwell, excitation, etc)
    #
    # example: mbf_growdamp_setup('x', 0.17)
    if (
        mbf_axis == "x"
        or mbf_axis == "y"
        or mbf_axis == "tx"
        or mbf_axis == "ty"
        or mbf_axis == "X"
        or mbf_axis == "Y"
        or mbf_axis == "TX"
        or mbf_axis == "TY"
    ):
        default_durations = [250, 250, 250, 500]
        default_dwell = 1
        default_tune_sweep_range = [80.00500, 80.49500]
        default_tune_offset = 0
        default_excitation_level = -18
    elif mbf_axis == "s" or mbf_axis == "S":
        default_durations = [10, 10, 50, 100]
        default_dwell = 480
        default_tune_sweep_range = [80.00220, 80.00520]
        default_tune_offset = 0
        default_excitation_level = -18
    else:
        raise ValueError("Incorrect axis selected. Should be x, y, s, tx, ty")

    if durations == 0:
        durations = default_durations
    if dwell == 0:
        dwell = default_dwell
    if tune_sweep_range == 0:
        tune_sweep_range = default_tune_sweep_range
    if tune_offset == 0:
        tune_offset = default_tune_offset
    if excitation_level == []:
        excitation_level = default_excitation_level

    _1, harmonic_number, pv_names, trigger_inputs = mbfSystemConfig()
    # Generate the base PV name.
    pv_head = pv_names["hardware_names"][mbf_axis]
    if mbf_axis == "x" or mbf_axis == "y" or mbf_axis == "X" or mbf_axis == "Y":
        pv_head_mem = pv_names["hardware_names"]["T"]
    elif mbf_axis == "s" or mbf_axis == "S":
        pv_head_mem = pv_names["hardware_names"]["L"]
    elif mbf_axis == "tx" or mbf_axis == "ty" or mbf_axis == "TX" or mbf_axis == "TY":
        pv_head_mem = pv_names["hardware_names"]["lab"]

    # Set up triggering
    # set up the appropriate triggering
    # Stop triggering first, otherwise there's a good chance the first thing
    # we'll do is loose the beam as we change things.
    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        mbfGetThenPut(
            "".join((pv_head, pv_names["tails"]["triggers"][trigger]["enable_status"])),
            "Ignore",
        )

    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        mbfGetThenPut(
            "".join(
                (
                    pv_head_mem,
                    pv_names["tails"]["triggers"]["MEM"][trigger]["enable_status"],
                )
            ),
            "Ignore",
        )
        mbfGetThenPut(
            "".join(
                (
                    pv_head_mem,
                    pv_names["tails"]["triggers"]["MEM"][trigger]["blanking_status"],
                )
            ),
            "All",
        )

    # Set the trigger to one shot
    mbfGetThenPut(
        "".join((pv_head, pv_names["tails"]["triggers"]["SEQ.mode"])), "One Shot"
    )
    mbfGetThenPut(
        "".join((pv_head_mem, pv_names["tails"]["triggers"]["MEM"]["mode"])), "One Shot"
    )
    # Set the triggering to Soft only
    caput(
        "".join((pv_head, pv_names["tails"]["triggers"]["SOFT"]["enable_status"])),
        "Enable",
    )
    caput(
        "".join(
            (pv_head_mem, pv_names["tails"]["triggers"]["MEM"]["SOFT"]["enable_status"])
        ),
        "Enable",
    )
    #  set up the memory buffer to capture ADC data.
    mbfGetThenPut(
        "".join((pv_head_mem, pv_names["tails"]["MEM"]["channel_select"])), "ADC0/ADC1"
    )
    # Delay to make sure the currently set up sweeps have finished.
    sleep(1)  # TODO look for system to be in bank 0.

    # Set up banks
    # bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR
    # 6=sweep+NCO 7=sweep+NCO+FIR)
    # bunch bank 1 (the excitation)
    mbfSetBank(mbf_axis, 1, 4)  # Sweep

    # bunch bank 2 (the feedback)
    mbfSetBank(mbf_axis, 2, 1)  # FIR

    # bunch bank 0 (the resting condition)
    mbfSetBank(mbf_axis, 0, 1)  # FIR

    # Set up states
    # state 4
    mbfSetState(
        mbf_axis,
        4,
        tune,
        1,
        "".join((excitation_level, "dB")),
        "On",
        durations[0],
        dwell,
        "Capture",
    )  # excitation
    # state 3
    mbfSetState(
        mbf_axis, 3, tune, 1, "-48dB", "Off", durations[1], dwell, "Capture"
    )  # passive damping
    # state 2
    mbfSetState(
        mbf_axis, 2, tune, 2, "-48dB", "Off", durations[2], dwell, "Capture"
    )  # active damping
    # state 1
    mbfSetState(
        mbf_axis, 1, tune, 2, "-48dB", "Off", durations[3], dwell, "Discard"
    )  # Quiecent

    # start state
    mbfGetThenPut("".join((pv_head, pv_names["tails"]["Sequencer.start_state"])), 4)
    # steady state bank
    mbfGetThenPut(
        "".join((pv_head, pv_names["tails"]["Sequencer.steady_state_bank"])), "Bank 0"
    )

    # set the super sequencer to scan all modes.
    mbfGetThenPut(
        "".join((pv_head, pv_names["tails"]["Super_sequencer_count"])), harmonic_number
    )

    # Set up data capture
    # Set the detector input to FIR
    mbfGetThenPut("".join((pv_head, pv_names["tails"]["Detector"]["source"])), "FIR")
    # Enable only detector 0
    for n_det in range(4):
        l_det = "".join(("det", n_det))
        mbfGetThenPut(
            "".join((pv_head, pv_names["tails"]["Detector"][l_det]["enable"])),
            "Disabled",
        )

    caput(
        "".join((pv_head, pv_names["tails"]["Detector"]["det0"]["enable"])), "Enabled"
    )
    # Set the bunch mode to all bunches on detector 0
    mbfGetThenPut(
        "".join((pv_head, pv_names["tails"]["Detector"]["det0"]["bunch_selection"])),
        range(1, 937),
    )
