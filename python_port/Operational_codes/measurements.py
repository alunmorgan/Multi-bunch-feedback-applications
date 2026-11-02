import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy

from Common import (
    get_variable,
    hannwin,
    machine_environment,
    mbf_fll_setup,
    mbf_system_config,
    save_to_archive,
    set_variable,
)


def mbf_growdamp_capture(input_settings: dict, pv_names: dict):
    # Gathers data on the machine environment.
    # Runs a growdamp experiment on an already setup system.
    # Saves the resultant data.
    #
    #   Args:
    #       input_settings(struct): contains all the setup information.
    #       pv_names(struct): contains the locations of all the machine parameters.
    #
    # example data = mbf_growdamp_capture(input_settings, pv_names)
    growdamp: dict = {}
    mbf_axis = input_settings["mbf_axis"]
    capture_full_bunch_motion = input_settings["capture_full_bunch_motion"]
    pv_head = pv_names["hardware_names"][mbf_axis]
    pv_head_mem = pv_names["hardware_names"]["mem"][mbf_axis]
    triggers = pv_names["tails"]["triggers"]
    Sequencer = pv_names["tails"]["Sequencer"]
    FIR = pv_names["tails"]["FIR"]
    # Getting feedback gain
    growdamp["FIR_gain"] = f"{pv_head}{FIR['gain']}"
    start_state = get_variable(f"{pv_head}{Sequencer['start_state']}")
    # getting the state of the sequencer.
    exp_state_names: list = []
    for n in range(start_state):
        entries = Sequencer[f"seq1{n}"].keys()
        for en in range(len(entries)):
            growdamp[f"seq1{n}_{entries[en]}"] = get_variable(
                f"{pv_head}{Sequencer[f'seq1{n}'][entries[en]]}"
            )

    growdamp["exp_state_names"] = exp_state_names
    ## Preparing system for data capture
    set_variable(f"{pv_head_mem}{triggers['MEM']['disarm']}", 1)
    time.sleep(0.5)  # Letting the hardware sort itself out.
    # Arm the memory so that it cycles[''] This means that all the status PV are
    # updated. Otherwise the code will say the memory is not ready as the status is
    # stale.
    set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
    time.sleep(2)  # Letting the hardware sort itself out.
    temp1 = get_variable(f"{pv_head_mem}{pv_names['tails']['TRG']['memory_status']}")
    if temp1 != "Idle":
        set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
    else:
        print("Memory is not ready trying again")
        time.sleep(5)  # Letting the hardware sort itself out.
        temp1 = get_variable(
            f"{pv_head_mem}{pv_names['tails']['TRG']['memory_status']}"
        )
        if temp1 != "Idle":
            set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
        else:
            raise ValueError("growdamp:memoryNotReady Memory is not ready please rerun")

    # Disarm, so that the current settings will be picked up upon arming.
    set_variable(f"{pv_head}{triggers['SEQ']['disarm']}", 1)
    ## Trigger the measurement
    if mbf_axis.lower() == "x" or mbf_axis.lower() == "s":
        chan = 0
    elif mbf_axis.lower() == "y":
        chan = 1

    if mbf_axis.lower() == "s":
        mem_lock = 180
    else:
        mem_lock = 30

    # Arm
    set_variable(f"{pv_head}{triggers['SEQ']['arm']}", 1)
    # Trigger
    set_variable(f"{pv_head_mem}{triggers['soft']}", 1)
    # download the data
    [growdamp["data"], growdamp["data_freq"], _1] = mbf_read_det(
        pv_head_mem, "axis", chan, "lock", mem_lock
    )
    ## Capturing full bunch motion data
    if capture_full_bunch_motion.lower() == "yes":
        turn_count = 1250 * 400
        turn_offset = 0
        growdamp["bunch_motion"] = mbf_read_mem(
            pv_head_mem, turn_count, "offset", turn_offset, "channel", 0, "lock", 60
        )
    return growdamp


def mbf_growdamp_setup(input_settings: dict, pv_names: dict):
    # Sets up the MBF system to be ready for a growdamp measurement['']
    #
    #   Args:
    #       input_settings(struct): contains all the setup information['']
    #       pv_names(struct): contains the locations of all the machine parameters['']
    #
    # example: mbf_growdamp_setup(input_settings, pv_names, trigger_inputs)
    mbf_tools()
    pll_setup: dict = {}
    mbf_axis = input_settings["mbf_axis"]
    harmonic_number = input_settings["harmonic_number"]
    states = input_settings["states"]
    excitation_tune = input_settings["excitation_tune"]
    bunch_monitor = input_settings["bunches_monitored"]
    pll_setup["pll_tracking"] = input_settings["pll_tracking"]
    pll_setup["pll_bunches"] = input_settings["pll_bunches"]
    pll_setup["pll_guard_bunches"] = input_settings["pll_guard_bunches"]
    pv_head = pv_names["hardware_names"][mbf_axis]
    pv_head_mem = pv_names["hardware_names"]["mem"][mbf_axis]
    trigger_inputs = pv_names["trigger_inputs"]
    triggers = pv_names["tails"]["triggers"]
    memory = pv_names["tails"]["MEM"]
    Sequencer = pv_names["tails"]["Sequencer"]
    Detector = pv_names["tails"]["Detector"]
    Bunch_bank = pv_names["tails"]["Bunch_bank"]
    NCO2 = pv_names["tails"]["NCO2"]
    ## Set up triggering
    # set up the appropriate triggering
    # Stop triggering first, otherwise there's a good chance the first thing
    # we'll do is loose the beam as we change things['']
    for trigger_ind in range(len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(f"{pv_head}{triggers[trigger]['enable_status']}", "Ignore")

    for trigger_ind in range(len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(f"{pv_head}{triggers['MEM'][trigger]['enable_status']}", "Ignore")
        set_variable(f"{pv_head}{triggers['MEM'][trigger]['blanking_status']}", "All")

    # Set the trigger to one shot
    set_variable(f"{pv_head}{triggers['SEQ']['mode']}", "One Shot")
    set_variable(f"{pv_head_mem}{triggers['MEM']['mode']}", "One Shot")
    # Set the triggering to Soft only
    set_variable(f"{pv_head}{triggers['SOFT']['enable_status']}", "Enable")
    set_variable(f"{pv_head_mem}{triggers['MEM']['SOFT']['enable_status']}", "Enable")
    #  set up the memory buffer to capture ADC data.
    set_variable(f"{pv_head_mem}{memory['channel_select']}", "ADC0/ADC1")
    # Delay to make sure the currently set up sweeps have finished.
    time.sleep(1)  # TODO look for system to be in bank 0.
    ## Set up banks
    # bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #               7=sweep+NCO+FIR)
    # bunch bank 2 (the feedback)
    mbf_set_bank(mbf_axis, 2, 1)  # FIR
    # bunch bank 1 (the excitation)
    mbf_set_bank(mbf_axis, 1, 4)  # Sweep
    # bunch bank 0 (the resting condition)
    mbf_set_bank(mbf_axis, 0, 1)  # FIR
    ## Set up states
    # (ax, state, tune, bank, gain, enable, duration, dwell, capture)
    for st in range(len(states)):
        mbf_set_state(mbf_axis, st, excitation_tune, states[st])

    # start state
    set_variable(f"{pv_head}{Sequencer['start_state']}", len(states))
    # steady state bank
    set_variable(f"{pv_head}{Sequencer['steady_state_bank']}", "Bank 0")
    ## set the super sequencer to scan all modes.
    set_variable(
        f"{pv_head}{pv_names['tails']['Super_sequencer_count']}", harmonic_number
    )
    ## set up PLL
    if pll_setup["pll_tracking"] == "yes":
        mbf_fll_setup("x", pll_setup["pll_bunches"], pll_setup["pll_guard_bunches"])
        set_variable(f"{pv_head}{NCO2['PLL_follow']}", "Follow")
        set_variable(f"{pv_head}{NCO2['gaindb']}", -30)
        fillx = get_variable(f"{pv_head}{Bunch_bank['bank1']['SEQ_enablewf']}")
        set_variable(f"{pv_head}{Bunch_bank['bank0']['NCO2_enablewf']}", fillx)
        set_variable(f"{pv_head}{Bunch_bank['bank1']['NCO2_enablewf']}", fillx)
        set_variable(f"{pv_head}{NCO2['enable']}", "On")

    ## Set up the detector.
    # Set the detector input to FIR
    set_variable(f"{pv_head}{Detector['source']}", "FIR")
    # Enable only detector 0
    for n_det in range(3):
        l_det = f"det{n_det}"
        set_variable(f"{pv_head}{Detector[l_det]['enable']}", "Disabled")

    set_variable(f"{pv_head}{Detector['det0']['enable']}", "Enabled")
    # Set which bunches detector 0 records.
    set_variable(f"{pv_head}{Detector['det0']['bunch_selection']}", bunch_monitor)


def mbf_set_bank(ax: str, bank: int, out_type: int):
    # Setup an individual bank in an individual MBF system.
    #
    #
    # Args:
    #       ax (str)          : 'x', 'y', or 's' axis
    #       bank (int)        : The bunch bank number.
    #       out_type (int)    : Determines which combination of filters and
    #                           excitation is required (0=off 1=FIR 2=NCO
    #                           3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #                           7=sweep+NCO+FIR)
    #
    # Example:  mbf_set_bank(ax, bank, out_type)
    [_1, harmonic_number, pv_names] = mbf_system_config()
    BB = pv_names["tails"]["Bunch_bank"][f"bank{bank}"]
    pv_head = [pv_names["hardware_names"][ax]]
    # bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #               7=sweep+NCO+FIR)
    if out_type == 0:
        # all off
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 1:
        # FIR only
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 2:
        # NCO only
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 3:
        # NCO + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 4:
        # sweep only
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 5:
        # sweep + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 6:
        # sweep + NCO
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 7:
        # sweep + NCO + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)

    # select which FIR filter to use
    set_variable(f"{pv_head}{BB['FIR']['selectwf']}", np.ones(1, harmonic_number) * 0)


def mbf_set_state(ax: str, state: int, tune: float, setup_data: dict):
    # Setup an individual state in the super sequencer.
    #
    # Args:
    #       ax (str)      : 'x', 'y', or 's' axis
    #       state (int)   : state number in the sequencer.
    #       tune (float)  : Tune of the machine.
    #       setup_data (struct): containing
    #           bank (int)    : The bunch bank used for this state.
    #           gain (str)    : the excitation level.
    #           duration (int): the number of turns the state is active.
    #           dwell (int)   : Dwell time (turns).
    #           capture (str) : 'Capture' or 'Discard' depending onn if you want to
    #                            keep the data or not
    #
    # Example: mbf_set_state(ax, state, tune, setup_data)
    [_2, _1, pv_names] = mbf_system_config()
    system_axis = pv_names["hardware_names"][ax]
    seq1 = pv_names["tails"]["Sequencer"][f"seq1{state}"]
    set_variable(f"{system_axis}{seq1['start_frequency']}", tune)
    set_variable(f"{system_axis}{['step_frequency']}", 0)
    set_variable(f"{system_axis}{['turns']}", setup_data["duration"])
    set_variable(f"{system_axis}{['holdoff']}", 0)
    set_variable(f"{system_axis}{['dwell']}", setup_data["dwell"])
    set_variable(f"{system_axis}{['bank_select']}", ["Bank ", (setup_data["bank"])])
    set_variable(f"{system_axis}{['capture_state']}", setup_data["capture"])
    set_variable(f"{system_axis}{['windowing_state']}", "Disabled")
    set_variable(f"{system_axis}{['gain']}", setup_data["excitation_level"])
    set_variable(f"{system_axis}{['blanking_state']}", "Off")
    set_variable(f"{system_axis}{['enable']}", setup_data["excitation"])


def reestablish_tune_measurement(mbf_axis: str):
    # sets up the tune measurement by setting bank1 and sequencer state one as
    # required.
    #   Args:
    #       mbf_axis(str): 'x','y', or 's'
    # Example: reestablish_tune_measurement('x')
    [_1, harmonic_number, pv_names] = mbf_system_config()
    if mbf_axis.lower() == "x":
        sweep_start = 80.139
        sweep_end = 80.239
        tune_gain = -54
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["x"]
    elif mbf_axis.lower() == "y":
        sweep_start = 80.227
        sweep_end = 80.327
        tune_gain = -54
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["y"]
    elif mbf_axis.lower() == "s":
        sweep_start = 80.00320
        sweep_end = 80.00520
        tune_gain = -18
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["s"]
    else:
        raise ValueError("MBF:InputError Please set required axis to x, y, or s")

    # setting up sequencer state 1 to be the tune sweep['']
    set_variable(f"{base}{pv_names['tails']['Super_sequencer']['count']}", 1)
    set_variable(f"{base}{pv_names['tails']['Sequencer']['start_state']}", 1)
    tune_sequencer = pv_names["tails"]["Sequencer"]["seq1"]
    set_variable(f"{base}{tune_sequencer['start_frequency']}", sweep_start)
    set_variable(f"{base}{tune_sequencer['end_frequency']}", sweep_end)
    set_variable(f"{base}{tune_sequencer['gaindb']}", tune_gain)
    set_variable(f"{base}{tune_sequencer['turns']}", tune_count)
    set_variable(f"{base}{tune_sequencer['dwell']}", tune_dwell)
    set_variable(f"{base}{tune_sequencer['bank_select']}", {"Bank 1"})
    set_variable(f"{base}{tune_sequencer['tune_pll_following']}", {"Ignore"})
    set_variable(f"{base}{tune_sequencer['enable']}", "On")
    set_variable(f"{base}{tune_sequencer['holdoff_state']}", 0)
    set_variable(f"{base}{tune_sequencer['holdoff']}", 0)
    set_variable(f"{base}{tune_sequencer['blanking_state']}", {"Blanking"})
    set_variable(f"{base}{tune_sequencer['windowing_state']}", {"Windowed"})
    set_variable(f"{base}{tune_sequencer['capture_state']}", {"Capture"})
    tune_bank = pv_names["tails"]["Bunch_bank"]["bank1"]
    # Setting bank 1 to use both the FIR and the sequencer but nothing else['']
    set_variable(f"{base}{tune_bank['FIR']['enablewf']}", np.ones(1, harmonic_number))
    set_variable(f"{base}{tune_bank['NCO1']['enablewf']}", np.zeros(1, harmonic_number))
    set_variable(f"{base}{tune_bank['NCO2']['enablewf']}", np.zeros(1, harmonic_number))
    set_variable(f"{base}{tune_bank['SEQ']['enablewf']}", np.ones(1, harmonic_number))
    set_variable(
        f"{base}{pv_names['tails']['Bunch_bank']['bank1']['PLL']['enablewf']}",
        np.zeros(1, harmonic_number),
    )
    # triggering
    set_variable(f"{base}{pv_names['tails']['triggers']['mode']}", "Rearm")
    set_variable(
        f"{base}{pv_names['tails']['triggers']['EXT']['enable_status']}", "Enable"
    )
    set_variable(f"{base}{pv_names['tails']['triggers']['SEQ']['arm']}", 1)


def get_stage_details(exp_data: dict):
    if "seq1_capture_state" in exp_data:
        stage_names: list = []
        for n in range(len(exp_data["states"])):
            if "Discard" in exp_data[f"seq1{n}_capture_state"]:
                stage_names[n] = "spacer"
            else:
                if "On" in exp_data[f"seq1{n}_enable"]:
                    stage_names[n] = "growth"
                else:
                    if "Bank 2" in exp_data[f"seq1{n}_bank_select"]:
                        stage_names[n] = "active"
                    else:
                        stage_names[n] = "passive"
        ck: int = 1
        # change the ordering so that the first stage in time is at index 1['']
        # works out which samples in the time series correspond to each stage['']
        end_of_stage: list = []
        recorded_stage_names: list = []
        samples_of_stage: list = []
        turns_of_stage: list = []

        for jjse in range(len(stage_names)):
            if "spacer" not in stage_names[jjse]:
                recorded_stage_names[ck] = stage_names[jjse]
                length_of_stage = exp_data["states"][jjse]["duration"]
                dwell_of_stage = exp_data["states"][jjse]["dwell"]
                if ck == 1:
                    end_of_stage[ck] = length_of_stage
                    samples_of_stage[ck] = range(end_of_stage[ck])
                    turns_of_stage[ck] = len(samples_of_stage[ck]) / dwell_of_stage
                else:
                    end_of_stage[ck] = end_of_stage[ck - 1] + length_of_stage
                    samples_of_stage[ck] = range(
                        (end_of_stage[ck - 1] + 1), end_of_stage[ck]
                    )
                    turns_of_stage[ck] = len(samples_of_stage[ck]) / dwell_of_stage

                ck = ck + 1
    else:
        # Old dataset use implict order in structure to order stages.
        test = exp_data.keys()
        names = test["_turns" in test]
        names = names["spacer" not in names]
        turns_of_stage = np.zeros(len(names)).tolist()
        samples_of_stage: list = []
        recorded_stage_names: list = []
        for nrs in range(len(names)):
            turns_of_stage[nrs] = exp_data[names[nrs]]

        turns_of_stage = turns_of_stage.reverse()
        for nrs in range(len(names)):
            samples_of_stage[nrs] = range(
                np.sum(turns_of_stage[1 : nrs - 1]) + 1, np.sum(turns_of_stage[1:nrs])
            )

        for hs in range(len(names)):
            recorded_stage_names[hs] = names[hs].replace("_turns", "")

        recorded_stage_names = recorded_stage_names.reverse()
    return recorded_stage_names, samples_of_stage, turns_of_stage


def mbf_modescan_capture(input_settings: dict, pv_names: dict):
    # wrapper def to call modescan, gather data on the environment:
    # and to save the resultant data.
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
    #       n_repeats (int): The number of repeat datapoints to capture
    #   Returns:
    #       modescan (struct): data structure containing the experimental
    #                          results and the machine conditions['']
    #                          [optional output]
    #
    # example data = mbf_modescan_capture('x', 100)
    modescan: dict = {}
    pv_head = pv_names["hardware_names"][input_settings["mbf_axis"]]
    for hs in range(input_settings["n_repeats"]):
        modescan["magnitude"][hs] = get_variable(f"{pv_head}:TUNE:DMAGNITUDE")
        modescan["phase"][hs] = get_variable(f"{pv_head}:TUNE:DPHASE")

    return modescan


def mbf_modescan_config(mbf_axis: str):
    # Contains the axis specific settings desired for the modescan experiment.
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
    #                       requesting
    #
    # Example: settings = mbf_modescan_config('x')
    settings: dict = {}
    if mbf_axis == "x":
        settings["axis_label"] = "x"
        settings["axis_number"] = 1
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.
    elif mbf_axis == "y":
        settings["axis_label"] = "y"
        settings["axis_number"] = 2
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.
    elif mbf_axis == "s":
        settings["axis_label"] = "s"
        settings["axis_number"] = 3
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.


def mbf_modescan_setup(input_settings: dict, pv_names: dict):
    # Sets up the MBF system to be ready for a modescan measurement.
    #
    #   Args:
    #       input_settings(struct): contains all the setup information.
    #       pv_names(struct): contains the locations of all the machine parameters.
    #
    # example: mbf_modescan_setup(input_settings, pv_names)
    mbf_tools()
    # Generate the base PV name.
    system_axis = pv_names["hardware_names"][input_settings["mbf_axis"]]
    # state 1 of sequencer
    seq1 = pv_names["tails"]["Sequencer"]["seq1"]
    set_variable(
        f"{system_axis}{seq1['start_frequency']}", input_settings["excitation_tune"]
    )
    set_variable(f"{system_axis}{seq1['step_frequency']}", 1)
    set_variable(f"{system_axis}{seq1['turns']}", input_settings["harmonic_number"] - 1)
    set_variable(f"{system_axis}{seq1['holdoff']}", 0)
    set_variable(f"{system_axis}{seq1['dwell']}", input_settings["dwell"])
    set_variable(f"{system_axis}{seq1['bank_select']}", "Bank 1")
    set_variable(f"{system_axis}{seq1['capture_state']}", "Capture")
    set_variable(f"{system_axis}{seq1['windowing_state']}", "Disabled")
    set_variable(f"{system_axis}{seq1['gaindb']}", input_settings["excitation_gain"])
    set_variable(f"{system_axis}{seq1['blanking_state']}", "Off")


def mbf_spectrum(mbf_axis: str, n_turns: int, fold: int = 1, repeat: int = 1):
    # generates a spectragram of all bunches.
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
    #                       requesting
    #       n_turns (int): The number of turns to capture.
    #       fold (int): The number of times to fold the data along the
    #                   frequency axis. This enhances power resolution
    #                   at the cost of frequency resolution.
    #       repeat (int): Repeat the capture this many times in order to
    #                     improve the power resolution.
    #
    # Example: mbf_spectrum('x',10000)
    ## Getting the desired system setup parameters.
    [root_string, harmonic_number, pv_names, trigger_inputs] = mbf_system_config()

    # Generate the base PV name.
    pv_head = pv_names["hardware_names"][mbf_axis]
    if mbf_axis == "s":
        system_name = pv_names["hardware_names"]["L"]
    else:
        system_name = pv_names["hardware_names"]["T"]

    PVt = pv_names["tails"]
    # getting general environment data.
    mbf_spec = machine_environment()
    mbf_spec["axis_label"] = mbf_axis
    # Disarm the sequencer and memory triggers
    set_variable(
        f"{pv_names['hardware_names'][mbf_axis]}"
        f"{pv_names['tails']['triggers']['SEQ']['disarm']}",
        1,
    )
    set_variable(f"{system_name}{pv_names['tails']['triggers']['MEM']['disarm']}", 1)
    for trigger_ind in range(len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(
            f"{pv_head}{pv_names['tails']['triggers']['MEM'][trigger]['enable_status']}",
            "Ignore",
        )
        set_variable(
            f"{pv_head}{pv_names['tails']['triggers']['MEM'][trigger]['blanking_status']}",
            "All",
        )

    # Set the trigger to one shot
    set_variable(f"{pv_head}{PVt['triggers']['MEM']['mode']}", "One Shot")
    # Set the triggering to External only
    set_variable(
        f"{pv_head}{pv_names['triggers']['MEM']['EXT']['enable_status']}", "Enable"
    )
    #  set up the memory buffer to capture ADC data['']
    set_variable(f"{pv_head}{pv_names['MEM']['channel_select']}", "ADC0/ADC1")
    mode_data = np.zeros(n_turns / fold, harmonic_number)
    bunch_data = np.zeros(n_turns / 2, harmonic_number)
    if mbf_axis == "x" or mbf_axis == "s":
        chan = 0
    elif mbf_axis == "y":
        chan = 1

    for k in range(1, repeat):
        set_variable(f"{ax2dev(mbf_axis)}{pv_names['tails']['MEM_arm']}", 1)
        if mbf_axis == "s":
            set_variable(
                f"{pv_names['hardware_names']['L']}{pv_names['tails']['triggers']['soft']}",
                1,
            )
            raw_data = mbf_read_mem(
                pv_names["hardware_names"]["L"], n_turns, "channel", chan, "lock", 60
            )
        else:
            set_variable(
                f"{pv_names['hardware_names']['T']}{pv_names['tails']['triggers']['soft']}",
                1,
            )
            raw_data = mbf_read_mem(
                pv_names["hardware_names"]["T"], n_turns, "channel", chan, "lock", 60
            )

        data_length = len(raw_data)
        # remove everything that is constant each revolotion
        xx = np.reshape(
            raw_data, harmonic_number, []
        )  # turn into matrix bunches x turns
        xx = xx - np.repmat(
            np.mean(xx, 2), 1, n_turns
        )  # subtract the average position per bunch
        motion_only = np.reshape(xx, 1, [])  # stretch out again
        # This enhances power resolution at the cost of frequency resolution['']
        folded_motion = np.reshape(motion_only, data_length / fold, fold)
        # calculate spectrum over all bunches
        s = 2 * np.sqrt(
            np.mean(abs(np.fft(hannwin(folded_motion)) / (data_length / fold)) ^ 2, 2)
        )
        ss1 = np.reshape(s, n_turns / fold, harmonic_number)  # fold into tune x modes
        mode_data = mode_data ^ 2 + ss1 ^ 2  # accumulating['']
        xf1 = abs(np.fft(hannwin(xx), [], 2)) / n_turns
        # only taking the lower half of the FFT
        bunch_data = (
            bunch_data ^ 2 + (xf1[:, 1 : np.floor(len(xf1) / 2)]) ^ 2
        )  # accumulating
    data = {}
    data["bunch_data"] = bunch_data
    data["bunch_bunches"] = np.sum(bunch_data[""] ^ 2, 1)
    data["bunch_tune"] = np.sum(bunch_data[""] ^ 2, 2)
    data["tune_data"] = np.fft.fftshift(mode_data, 2)
    data["mode_modes"] = np.sum(bunch_data[""] ^ 2, 1)
    data["mode_tune"] = np.sum(mode_data[1 : np.floor(len(mode_data)) / 2, :] ^ 2, 2)
    data["tune_axis"] = np.linspace(0, 0.5, len(data["bunch_tune"]))
    data["bunch_axis"] = range(harmonic_number)
    data["mode_axis"] = range(-harmonic_number / 2, (harmonic_number / 2))

    graph_handles = plt.figure
    ax1 = plt.subplot("position", [0.02, 0.35, 0.7, 0.6])
    plt.imagesc(
        data["bunch_axis"],
        data["tune_axis"],
        np.log10(data["bunch_data"]),
        [-3, 0] + np.log10(max(max(data["bunch_data"]))),
    )
    set(ax1, "YAxisLocation", "right")
    set(ax1, "YDir", "normal")
    set(ax1, "XTick", [])
    set(ax1, "YTick", [])
    plt.title(data["axis_label"])
    # Frequencies graph
    ax2 = plt.subplot("position", [0.72, 0.35, 0.18, 0.6])
    plt.plot(data["bunch_tune"], data["tune_axis"])
    set(ax2, "YAxisLocation", "right")
    set(ax2, "XAxisLocation", "top")
    set(ax2, "XTick", [])
    plt.ylabel("Fractional tune")
    # bunches graph
    [_1, bpi] = max(data["mode_tune"])
    ax3 = plt.subplot("position", [0.02, 0.11, 0.7, 0.24])
    plt.plot(data["bunch_data"][bpi, :])
    plt.xlabel(f"Bunches at peak tune {data['tune_axis'][bpi]}")
    set(ax3, "YTick", [])

    graph_handles = plt.figure
    ax4 = plt.subplot("position", [0.02, 0.35, 0.7, 0.6])
    plt.imagesc(
        data["mode_axis"],
        data["tune_axis"],
        np.log10(data["tune_data"][1 : -1 / 2, :]),
        [-3, 0] + np.log10(max(max(data["tune_data"][1 : -1 / 2, :]))),
    )
    set(ax4, "YAxisLocation", "right")
    set(ax4, "YDir", "normal")
    set(ax4, "XTick", [])
    set(ax4, "YTick", [])
    ax5 = plt.subplot("position", [0.72, 0.35, 0.18, 0.6])
    plt.plot(data["mode_tune"], data["tune_axis"])
    set(ax5, "YAxisLocation", "right")
    set(ax5, "XAxisLocation", "top")
    set(ax5, "XTick", [])
    plt.ylabel("Fractional tune")
    ax6 = plt.subplot("position", [0.02, 0.11, 0.7, 0.24])
    plt.plot(data["mode_axis"][data["tune_data"][bpi, :]])
    plt.xlabel(f"Modes at peak tune {data['tune_axis'][bpi]}")
    set(ax6, "YTick", [])

    data["time"] = datetime.datetime.now()
    data["base_name"] = ["Spectrum_", mbf_axis, "_axis"]
    ## saving the data to a file
    save_to_archive(root_string, data, graph_handles)
    mbf_restore_all()

    return data


def mbf_spectrum_capture(input_settings: dict, pv_names: dict):
    # captures a set of data from the mbf system runs the analysis.
    #
    # Args:
    #       input_settings(struct): contains all the setup information.
    #       pv_names(struct): contains the locations of all the machine parameters.
    #
    # Example: data = mbf_spectrum_capture(input_settings, pv_names)
    mbf_axis = input_settings["mbf_axis"]
    n_turns = input_settings["n_turns"]
    repeat = input_settings["repeat"]
    captured_data: list = []
    for k in range(repeat):
        # Arm, trigger, read
        if mbf_axis == "s":
            # LMBF hardware
            set_variable(
                f"{pv_names['hardware_names']['L']}{pv_names['tails']['triggers']['MEM']['arm']}",
                1,
            )
            set_variable(
                f"{pv_names['hardware_names']['L']}{pv_names['tails']['triggers']['soft']}",
                1,
            )
            captured_data[k] = mbf_read_mem(
                pv_names["hardware_names"]["L"], n_turns, "channel", 0, "lock", 60
            )
        else:
            # TMBF hardware
            set_variable(
                f"{pv_names['hardware_names']['T']}{pv_names['tails']['triggers']['MEM']['arm']}",
                1,
            )
            set_variable(
                f"{pv_names['hardware_names']['T']}{pv_names['tails']['triggers']['soft']}",
                1,
            )
            if mbf_axis == "x":
                captured_data[k] = mbf_read_mem(
                    pv_names["hardware_names"]["T"], n_turns, "channel", 0, "lock", 60
                )
            else:
                captured_data[k] = mbf_read_mem(
                    pv_names["hardware_names"]["T"], n_turns, "channel", 1, "lock", 60
                )


def mbf_spectrum_setup(input_settings: dict, pv_names: dict):
    # sets up the hardware ready to capture data for a spectrum['']
    # Args:
    #       input_settings(struct): contains all the setup information['']
    #       pv_names(struct): contains the locations of all the machine parameters['']
    #
    # Example mbf_spectrum_setup(input_settings, pv_names, trigger_inputs)
    mbf_tools()
    mbf_axis = input_settings["mbf_axis"]
    trigger_inputs = pv_names["trigger_inputs"]
    # Disarm the sequencer (tune measurement) and memory triggers
    set_variable(
        f"{pv_names['hardware_names'][mbf_axis]}{pv_names['tails']['triggers']['SEQ']['disarm']}",
        1,
    )
    set_variable(
        f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['triggers']['MEM']['disarm']}",
        1,
    )
    for trigger_ind in range(len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(
            f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['triggers']['MEM'][trigger]['enable_status']}",
            "Ignore",
        )
        set_variable(
            f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['triggers']['MEM'][trigger]['blanking_status']}",
            "All",
        )

    # Set the trigger to one shot
    set_variable(
        f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['triggers']['MEM']['mode']}",
        "One Shot",
    )
    # Set the triggering to External only
    set_variable(
        f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['triggers']['MEM']['EXT']['enable_status']}",
        "Enable",
    )
    #  set up the memory buffer to capture ADC data['']
    set_variable(
        f"{pv_names['hardware_names']['mem'][mbf_axis]}{pv_names['tails']['MEM']['channel_select']}",
        "ADC0/ADC1",
    )


def mbf_bunch_motion_capture(pv_names: dict):
    # simultaineously captures bunch by bunch centroid data for all three axes.
    # When armed by the code each system will start aquisition
    # on the next hardware trigger.
    #
    # Example: bunch_motion = mbf_bunch_motion_capture(pv_names)
    [turn_count, turn_offset] = mbf_bunch_motion_config()
    # Generate the base PV names['']
    pv_head_T = pv_names["hardware_names"]["T"]
    pv_head_L = pv_names["hardware_names"]["L"]
    # Disarm, so that the current settings will be picked up upon arming.
    set_variable(f"{pv_head_T}{pv_names['tails']['triggers']['MEM']['disarm']}", 1)
    set_variable(f"{pv_head_L}{pv_names['tails']['triggers']['MEM']['disarm']}", 1)
    ## Trigger the measurement on all three axes
    # Turn off the External triggering from the Event receiver.
    set_variable(pv_names["Hardware_trigger"], 0)
    time.sleep(0.5)
    # Check memory is ready
    mem_t = get_variable(f"{pv_head_T}{pv_names['tails']['TRG']['memory_status']}")
    mem_s = get_variable(f"{pv_head_L}{pv_names['tails']['TRG']['memory_status']}")
    if (mem_t[1] == "Idle") != 1 or (mem_s[1] == "Idle") != 1:
        raise ValueError(
            "BunchMotionCapture:MemoryErrorMemory is not ready please try again"
        )

    # Arming the systems
    set_variable(
        [
            f"{pv_head_T}{pv_names['tails']['triggers']['MEM']['arm']}",
            f"{pv_head_L}{pv_names['tails']['triggers']['MEM']['arm']}",
        ],
        1,
    )
    # Triggering the measurement[''] #### SHOULD TRIGGER ON THE NEXT EXTERNAL
    set_variable(pv_names["Hardware_trigger"], 1)
    # Triggering memory under a lock['']
    bunch_motion_temp = mbf_read_mem(
        pv_names["hardware_names"]["T"], turn_count, "offset", turn_offset, "lock", 60
    )
    bunch_motion = {}
    bunch_motion["x"] = bunch_motion_temp[:, 1]
    bunch_motion["y"] = bunch_motion_temp[:, 2]
    bunch_motion["z"] = mbf_read_mem(
        pv_names["hardware_names"]["L"],
        turn_count,
        "offset",
        turn_offset,
        "channel",
        0,
        "lock",
        60,
    )
    return bunch_motion


def mbf_bunch_motion_config():
    # Contains the specific settings desired for the bunch motion experiment.
    # # Example: [turn_count, turn_offset] = mbf_bunch_motion_config
    # Number of turns to capture.
    turn_count = 8962
    # Trigger is zero.
    turn_offset = 48000


def mbf_bunch_motion_setup(pv_names: dict):
    # Sets up all three axis so that they will take a single set of data each
    # when armed and triggered
    #
    # Example: mbf_bunch_motion_setup
    memory_triggers = pv_names["tails"]["triggers"]["MEM"]
    memory_buffers = pv_names["tails"]["MEM"]
    mbf_setup_wait_for_hw_trigger(pv_names)
    PVt = pv_names["tails"]
    mbf_systems: list = ["T", "L"]
    for hse in range(2):
        # Generate the base PV name['']
        pv_head = pv_names["hardware_names"][mbf_systems[hse]]
        set_variable(
            f"{pv_head}{memory_triggers['ADC0']['blanking_status']}", "Blanking"
        )
        set_variable(
            f"{pv_head}{memory_triggers['ADC1']['blanking_status']}", "Blanking"
        )
        #  set up the memory buffer to capture ADC data['']
        set_variable(f"{pv_head}{memory_buffers['channel_select']}", "ADC0/ADC1")


def BBBFE_detector_restore(mbf_axis: str, detector_setup: dict):
    mbf_axis = mbf_axis.lower()
    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    detector = pv_names["tails"]["Detector"]
    # set up the individual tune detectors to run on 1,2,3
    for ms in range(3):
        det_name = f"det{ms}"
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['enable']}",
            detector_setup[det_name]["enable"],
        )
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['scale']}",
            detector_setup[det_name]["scale"],
        )
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['bunch_select']}", "0:935"
        )
        set_variable(f"{mbf_names[mbf_axis]}{detector[det_name]['reset_selection']}", 1)
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['bunch_select']}",
            detector_setup[det_name]["bunch_select"][1],
        )
        set_variable(f"{mbf_names[mbf_axis]}{detector[det_name]['set_selection']}", 1)


def BBBFE_detector_setup(mbf_axis: str, single_bunch_location: int):
    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    detector = pv_names["tails"]["Detector"]
    if single_bunch_location == 0:
        prior_bunch = 935
    else:
        prior_bunch = single_bunch_location - 1

    # read the existing detector states
    detector_setup: dict = {}
    for ms in range(3):
        detector_setup[f"det{ms}"]["enable"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["enable"]]
        )
        detector_setup[f"det{ms}"]["scale"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["scale"]]
        )
        detector_setup[f"det{ms}"]["bunch_select"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["bunch_select"]]
        )

    # set up the individual tune detectors to run on 1,2,3
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det1']['bunch_select']}", prior_bunch
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['set_selection']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det2']['bunch_select']}",
        (single_bunch_location),
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['set_selection']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det3']['bunch_select']}",
        (single_bunch_location + 1),
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['set_selection']}", 1)
    # set sweep gain to -18
    set_variable(
        [mbf_names[mbf_axis], pv_names["tails"]["Sequencer"]["seq1"]["gaindb"]], "-18"
    )
    # set detector fixed gain
    return detector_setup


def mbf_pll_bank_setup(mbf_axis: str, pllbunches: int = 400, guardbunches: int = 2):
    # Sets up the banks for FLL operation['']
    #
    #   mbf_axis(str): x, y, or s
    #   pllbunches (float or list of floats): bunches numbers to use for PLL (0-935)
    #                                         (defaults to 400)
    #   guardbunches (int): number of bunches around PLL to also take out
    #                       of sweeper (defaults to 2)
    #
    # example: mbf_fll_bank_setup(name,pllbunches,guardbunches)

    [_1, harmonic_number, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    pllbunches = np.mod(pllbunches, harmonic_number - 1)
    # initialise pll pattern
    pllpattern = False(range(harmonic_number))
    pllpattern[pllbunches] = True
    # now we want to create a pattern with a little more room around the
    # pll bunches[''] It's a little tricky with a general pattern, and the cirular
    # nature the pattern, so I use circshift in a loop
    guardpattern = True(range(harmonic_number))
    for n in range(-guardbunches, guardbunches):
        guardpattern[np.fft.circshift(pllpattern, n)] = False

    # Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps),
    # and in PLL detector.
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank0']['PLL']['enablewf']}",
        pllpattern,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['PLL']['enablewf']}",
        pllpattern,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['target_bunches']}",
        pllpattern,
    )
    # Set sweep (SEQ) and its detector (#1) to NOT operate on these and
    # guard bunches around, ie only on guardpattern.
    # check or add to any previous config and uses logical AND to insert the
    # guardpattern into the existing setup.
    sequencer = get_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['SEQ']['enablewf']}"
    )
    detector = get_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Detector']['det0']['bunch_selection']}"
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['SEQ']['enablewf']}",
        guardpattern and sequencer,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Detector']['det0']['bunch_selection']}",
        guardpattern and detector,
    )


def mbf_pll_detector_setup(
    mbf_axis: str,
    pll_detector_select: str = "ADC no fill",
    adc_reject_count: str = "128 turns",
    pll_detector_scaling: str = "48dB",
    pll_detector_blanking: str = "Blanking",
    pll_detector_dwell: int = 128,
):
    # Sets up the detector for FLL operation['']
    #
    #   mbf_axis (str): x, y, or s. Selects which MBF system to operate on.
    #
    # example: mbf_pll_detector_setup(mbf_axis, varargin)

    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    # Set up the PLL detector
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['mode']}",
        pll_detector_select,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['adc']['reject_count']}", adc_reject_count
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['scaling']}",
        pll_detector_scaling,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['blanking']}",
        pll_detector_blanking,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}",
        pll_detector_dwell,
    )


def mbf_pll_start(
    mbf_axis: str,
    pllbunches: int = 400,
    guardbunches: int = 2,
    pll_nco_gain: int = -30,
    target_phase: int = 180,
):
    # sets up the frequency locked loop of the MBF system['']
    # and starts['']
    #
    #       mbf_axis (str): x, y, or s[''] Selects which MBF system to operate on['']
    #       pllbunches (float or list of floats): Selects which bunches to have the
    #                                             FLL operational on['']
    #       guardbunches (int): number of bunches around the FLL bunches which have
    #                           feddback and capture disabled['']
    #
    # example: mbf_fll_setup(mbf_axis, pllbunches, guardbunches)

    mbf_pll_bank_setup(mbf_axis, pllbunches=pllbunches, guardbunches=guardbunches)
    mbf_pll_detector_setup(mbf_axis)
    pll_initialisation(
        mbf_axis, pll_target_phase=target_phase, pll_nco_gain=pll_nco_gain
    )


def pll_initial_setup_values(mbf_axis: str):
    # Some setup with 'working values'[''] These ought to be read from a
    # config file or be additional arguments in the future['']
    # mbf_axis(str): xys
    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['mode']}", "ADC no fill"
    )
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['adc']['reject_count']}", "128 turns")
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['scaling']}", "48dB"
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['blanking']}", "Blanking"
    )
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['minumum_magnitude']}", 0)
    if "TMBF" in mbf_names[mbf_axis]:
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", 1000
        )  # safe also for for low charge, sharp resonance
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", 0)
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}", 128
        )
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}", 0.02)
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", -180)
    elif "LMBF" in mbf_names[mbf_axis]:
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", 100
        )  # safe also for for low charge, sharp resonance
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", 0)
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}", 128
        )
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}", 0.001)
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", -5)


def pll_initialisation(
    mbf_axis: str,
    pll_ki: int = 1000,
    pll_kp: int = 0,
    pll_min_magnitude: float = 0,
    pll_locking_max_offset: float = 0.003,
    pll_tracking_max_offset: float = 0.02,
    pll_nco_gain: int = -30,
    pll_target_phase: int = 160,
    tune_override: float | None = None,
):
    # This is to start the phase locked loop (pll) [also called pll] from
    # scratch. Once the initial lock is found then the settings are changed to
    # improve tracking. if signal is lost this process can be run again.
    # mbf_axis(str): x, y, or s
    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    ## Checking tune
    # starting frequency is taken from swept tune measurement. Can also
    # be overridden from command line input (but then it will only work if tune
    # feedback has brought the tune to the desired value.)
    if not tune_override:
        # Perform a TUNE sweep, record phase at tune peak and the tune value
        tune_frequency_from_sweep = get_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['tune']['centre']}"
        )
        if not tune_frequency_from_sweep:
            raise ValueError(
                "pllInitialisation:invalidTuneFitTune fit invalid, cannot start PLL."
            )

    else:
        tune_frequency_from_sweep = tune_override
        print(f"Using tune override of {tune_override}")

    # Disable PLL and turn off the NCO
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['stop']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['enable']}", "Off")
    # Set up the FLL feedback loop
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", pll_ki)
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", pll_kp)
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['minumum_magnitude']}",
        pll_min_magnitude,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", pll_target_phase
    )
    # Set up the NCO
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['gain']}", pll_nco_gain)
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['set_frequency']}",
        tune_frequency_from_sweep,
    )
    # Limit tune range of the NCO for initial peak finding['']
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}",
        pll_locking_max_offset,
    )
    # Enable the NCO and PLL
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['enable']}", "On")
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['start']}", 1)
    # Wait until PLL has locked (set lower bound to phase error?)
    t1 = datetime.datetime.now()
    while (
        abs(
            abs(
                get_variable(
                    f"{mbf_names[mbf_axis]}{mbf_vars['pll']['readback']['phase']}"
                )
            )
            - abs(pll_target_phase)
        )
        > 1
    ):  # within one degree of target['']
        lock_time = datetime.datetime.now()
        if lock_time > t1 + 10:  # FIXME
            print("Unable to lock within 10 seconds")
            return

    # Once locked widen the NCO limits to max required for tracking
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}",
        pll_tracking_max_offset,
    )


def setup_feedback_for_bunch_train(
    mbf_axis: str, train_length: int, clear_previous: str = "yes"
):
    # This allows the setup of the MBF to be adjusted to be suitable for the
    # different bunch train lengths[''] The feedback will ignore anything not in the
    # bunch train
    # Inputs:
    #        mbf_axis (str): axis to apply the settings to[''] ('x' or 'y')
    #        train_length (int): length of train to apply tune measurement and
    #                            feedback to[''] Starts from first bunch as per the
    #                            master timing generator['']
    #        clear_previous(str): if yes removes existing enable patterns['']
    #                            Defaults to yes['']
    #
    # Example: setup_for_bunch_train('x', 686)

    [_1, harmonic_number, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][mbf_axis]
    # feedback during quiecent mode
    feedback0 = pv_names["tails"]["Bunch_bank"]["bank0"]["FIR"]["enablewf"]
    # feedback during tune measurement
    feedback1 = pv_names["tails"]["Bunch_bank"]["bank1"]["FIR"]["enablewf"]

    if clear_previous.lower() == "yes":
        enable_feedback0 = np.zeros(harmonic_number)
        enable_feedback1 = np.zeros(harmonic_number)
    else:
        enable_feedback0 = get_variable(f"{pv_head}{feedback0}")
        enable_feedback1 = get_variable(f"{pv_head}{feedback1}")

    for js in range(train_length):
        enable_feedback0[js] = 1
        enable_feedback1[js] = 1

    # Apply changes
    set_variable(f"{pv_head}{feedback0}", enable_feedback0)
    set_variable(f"{pv_head}{feedback1}", enable_feedback1)


def setup_tune_bunch_selection(
    mbf_axis: str,
    start_bunch: int = 1,
    step_bunch: int = 1,
    n_bunch: str | int = "all",
    clear_previous: str = "yes",
):
    # This allows the setup of the tune to be adjusted from using all bunches to
    # using a subset. This is useful if the tune measurement is struggling due to
    # distortion of the IQ plot. Defaults to all bunches.
    # Inputs:
    #       mbf_axis (str): axis to apply the settings to. ('x' or 'y')
    #       start_bunch(int): The first position to take the tune measurement.
    #       step_bunch(int): The spacing of measurement positions.
    #       n_bunch(int): How many positions are used.
    #       clear_previous(str): if yes removes existing enable patterns.
    #                            Defaults to yes.
    #
    # Example: setup_tune_bunch_selection('x', 40, 90, 10)
    [_1, harmonic_number, pv_names] = mbf_system_config()
    if n_bunch == "all":
        n_bunch = harmonic_number

    pv_head = pv_names["hardware_names"][mbf_axis]
    # tune measurement
    detector0 = pv_names["tails"]["Detector"]["det0"]["bunch_selection"]
    # tune excitation
    sequencer1 = pv_names["tails"]["Bunch_bank"]["bank1"]["SEQ"]["enablewf"]

    if clear_previous == "yes":
        det_enable_wfm = np.zeros(harmonic_number)
        seq_enable_wfm = np.zeros(harmonic_number)
    else:
        det_enable_wfm = get_variable([pv_head, detector0])
        seq_enable_wfm = get_variable([pv_head, sequencer1])

    for js in range(n_bunch):
        det_enable_wfm[start_bunch + (js - 1) * step_bunch] = 1
        seq_enable_wfm[start_bunch + (js - 1) * step_bunch] = 1

    # Apply changes
    set_variable(f"{pv_head}{detector0}", det_enable_wfm)
    set_variable(f"{pv_head}{sequencer1}", seq_enable_wfm)


def configure_tune_sweep(
    mbf_axis: str,
    drive_bunch: list[int],
    fb_on_off: int,
    d0flag: int,
    d1flag: int,
    d2flag: int,
    d3flag: int,
):
    # drive_bunch = 0:2:935;    # starts at 0
    # drive_bunch = 123
    # fb_on_off = 1;      # 0 => off, 1 => on
    [_1, harmonic_number, pv_names] = mbf_system_config()
    head = pv_names["hardware_names"][mbf_axis]
    bank1 = pv_names["tails"]["Bunch_bank"][""]("bank1")
    detectors = pv_names["tails"]["Detector"]
    detect_bunch = drive_bunch
    # Only sweep selected bunch
    drive_wf = np.zeros(harmonic_number)
    drive_wf[drive_bunch + 1] = 1
    # chose which bunches to monitor the response
    detect_wf_1 = np.zeros(1, harmonic_number)
    detect_wf_1[np.sort(np.mod(detect_bunch + 0, harmonic_number) + 1)] = 1
    detect_wf_2 = np.zeros(1, harmonic_number)
    detect_wf_2[np.sort(np.mod(detect_bunch + 1, harmonic_number) + 1)] = 1
    detect_wf_3 = np.zeros(1, harmonic_number)
    detect_wf_3[np.sort(np.mod(detect_bunch + 2, harmonic_number) + 1)] = 1
    # write to the TMBF on which bunches to perform the sweep
    set_variable(f"{head}{bank1['SEQ']['enablewf']}", drive_wf)
    # Configure FIR enable (whether feedback is on or off)
    set_variable(
        f"{head}{bank1['FIR']['enablewf']}", fb_on_off * np.ones(1, harmonic_number)
    )
    # Detector 0 grabs everything
    if d0flag:
        set_variable(
            f"{head}{detectors['det0']['bunch_selection']}", np.ones(1, harmonic_number)
        )
        set_variable(f"{head}{detectors['det0']['enable']}", "Enabled")
    else:
        set_variable(f"{head}{detectors['det0']['enable']}", "Disabled")

    # Detector 1 only observes active bunches
    if d1flag:
        set_variable(f"{head}{detectors['det1']['bunch_selection']}", detect_wf_1)
        set_variable(f"{head}{detectors['det1']['enable']}", "Enabled")
    else:
        set_variable(f"{head}{detectors['det1']['enable']}", "Disabled")

    # Detector 2 only observes 1 bunch behind driven bunches
    if d2flag:
        set_variable(f"{head}{detectors['det2']['bunch_selection']}", detect_wf_2)
        set_variable(f"{head}{detectors['det2']['enable']}", "Enabled")
    else:
        set_variable(f"{head}{detectors['det2']['enable']}", "Disabled")

    # Detector 3 only observes 2 bunches behind driven bunches
    if d3flag:
        set_variable(f"{head}{detectors['det3']['bunch_selection']}", detect_wf_3)
        set_variable(f"{head}{detectors['det3']['enable']}", "Enabled")
    else:
        set_variable(f"{head}{detectors['det3']['enable']}", "Disabled")

    return


def mbf_tunescan_over_modes_capture(mbf_axis: str, pv_names: dict):
    # wrapper def to call tunescan, gather data on the environment:
    # and to save the resultant data.
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
    #
    # example data = mbf_tunescan_over_modes_capture('x', pv_names)
    pv_head = pv_names["hardware_names"][mbf_axis]
    pv_head_mem = pv_names["hardware_names"]["mem"][mbf_axis]
    triggers = pv_names["tails"]["triggers"]
    # Disarm, so that the current settings will be picked up upon arming.
    set_variable(f"{pv_head}{triggers['SEQ']['disarm']}", 1)
    ## Trigger the measurement
    if mbf_axis == "x" or mbf_axis == "s":
        chan = 0
    elif mbf_axis == "y":
        chan = 1

    if mbf_axis == "s":
        mem_lock = 180
    else:
        mem_lock = 30
    tunescan = {}
    # Arm
    set_variable(f"{pv_head}{triggers['SEQ']['arm']}", 1)
    # Trigger
    set_variable(f"{pv_head_mem}{triggers['soft']}", 1)
    # download the data
    measurement_time = (
        np.ceil(get_variable["SR23C-DI-TMBF-01:Y:SEQ:TOTAL:DURATION:S"]) + 5
    )
    time.sleep(measurement_time)
    tunescan["data"], tunescan["scale"] = mbf_read_det(
        pv_head_mem, "axis", chan, "lock", mem_lock
    )
    return tunescan


def mbf_tunescan_over_modes_config(mbf_axis: str):
    # Contains the axis specific settings desired for the tunescan experiment['']
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are
    #                       requesting
    #
    # Example: settings = mbf_tunescan_config('x')
    settings: dict = {}
    if mbf_axis.lower() == "x":
        settings["axis_label"] = "x"
        settings["axis_number"] = 1
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.
    elif mbf_axis.lower() == "y":
        settings["axis_label"] = "y"
        settings["axis_number"] = 2
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.
    elif mbf_axis.lower() == "s":
        settings["axis_label"] = "s"
        settings["axis_number"] = 3
        settings["ex_level"] = -18  # excitation level in dB.
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB.
        settings["seq_gain"] = -42  # sequencer gain in dB.


def mbf_tunescan_over_modes_setup(tunescan: dict):
    # Sets up the MBF system to be ready for a tunescan measurement.
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
    #       tunescan (struct): Contains all the setup parameters.
    #
    # example: mbf_tunescan_over_modes_setup(tunescan)
    mbf_tools()
    if tunescan["feedback_state"] == "on":
        fb_on_off = 1
    else:
        fb_on_off = 0

    [_1, harmonic_number, pv_names] = mbf_system_config()
    Detector = pv_names["tails"]["Detector"]
    Sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    Bunch_bank1 = pv_names["tails"]["Bunch_bank"]["bank1"]
    # Generate the base PV name['']
    system_axis = pv_names["hardware_names"][""](tunescan["mbf_axis"])
    detect_bunch = tunescan["drive_bunches"]
    # Only sweep selected bunch
    drive_wf = np.zeros(1, harmonic_number)
    drive_wf[tunescan["drive_bunches"] + 1] = 1
    # chose which bunches to monitor the response
    detect_wf_1 = np.zeros(1, harmonic_number)
    detect_wf_1[np.sort(np.mod(detect_bunch + 0, harmonic_number) + 1)] = 1
    detect_wf_2 = np.zeros(1, harmonic_number)
    detect_wf_2[np.sort(np.mod(detect_bunch + 1, harmonic_number) + 1)] = 1
    detect_wf_3 = np.zeros(1, harmonic_number)
    detect_wf_3[np.sort(np.mod(detect_bunch + 2, harmonic_number) + 1)] = 1
    # write to the TMBF on which bunches to perform the sweep
    set_variable(f"{system_axis}{Bunch_bank1['SEQ']['enablewf']}", drive_wf)
    # Configure FIR enable (whether feedback is on or off)
    set_variable(
        f"{system_axis}{Bunch_bank1['FIR']['enablewf']}",
        fb_on_off * np.ones(1, harmonic_number),
    )
    # Detector 0 grabs everything
    set_variable(
        f"{system_axis}{Detector['det0']['bunch_selection']}",
        np.ones(1, harmonic_number),
    )
    set_variable(f"{system_axis}{Detector['det0']['enable']}", "Enabled")
    # Detector 1 only observes active bunches
    set_variable(f"{system_axis}{Detector['det1']['bunch_selection']}", detect_wf_1)
    set_variable(f"{system_axis}{Detector['det1']['enable']}", "Enabled")
    # Detector 2 only observes 1 bunch behind driven bunches
    set_variable(f"{system_axis}{Detector['det2']['bunch_selection']}", detect_wf_2)
    set_variable(f"{system_axis}{Detector['det2']['enable']}", "Enabled")
    # Detector 3 only observes 2 bunches behind driven bunches
    set_variable(f"{system_axis}{Detector['det3']['bunch_selection']}", detect_wf_3)
    set_variable(f"{system_axis}{Detector['det3']['enable']}", "Enabled")
    # arm the TMBF as one-shot rather than continuous
    set_variable(f"{system_axis}{pv_names['tails']['triggers']['mode']}", "One Shot")
    set_variable(f"{system_axis}{pv_names['tails']['Sequencer']['reset']}", 1)
    # set the super-sequencer to have the correct number of modes
    set_variable(f"{system_axis}{pv_names['tails']['Super_sequencer_reset']}", 1)
    set_variable(
        f"{system_axis}{pv_names['tails']['Super_sequencer_count']}", harmonic_number
    )
    # change the number of captures to speed things up (normally 4096)
    set_variable(f"{system_axis}{Sequencer1['turns']}", tunescan["n_captures"])
    # select the tune sweep frequency / mode
    set_variable(
        f"{system_axis}{Sequencer1['start_frequency']}",
        tunescan["start_mode"] + tunescan["start_frequency"],
    )
    set_variable(
        f"{system_axis}{Sequencer1['end_frequency']}",
        tunescan["start_mode"] + tunescan["end_frequency"],
    )


def tune_sweep_expt(mbf_axis: str):
    # add the matlab paths for MBF tools
    mbf_tools()
    [_2, harmonic_number, pv_names, _1] = mbf_system_config()
    mbf_vars = pv_names["tails"]
    system_axis = pv_names["hardware_names"][mbf_axis]
    seq1 = pv_names["tails"]["Sequencer"]["seq1"]
    # experiment parameters
    savefile = appendtimestamp("tmbf_expt")
    ncap = 1001  # 4096; # 1001 takes ~ 3 minutes
    startmode = 0
    drive_bunch = range(harmonic_number)
    # drive_bunch = 100
    fb_on_off = 1
    if mbf_axis == "x":
        start_freq = 0.139
        end_freq = 0.239
    else:
        start_freq = 0.227
        end_freq = 0.327

    ### configure the sweep
    configure_tune_sweep(mbf_axis, drive_bunch, fb_on_off, 1, 1, 1, 1)
    # arm the TMBF as one-shot rather than continuous
    set_variable(f"{system_axis}{mbf_vars['triggers']['mode']}", "One Shot")
    set_variable(f"{system_axis}{pv_names['tails']['Sequencer']['reset']}", 1)
    # set the super-sequencer to have the correct number of modes
    set_variable(f"{system_axis}{mbf_vars['Super_sequencer_reset']}", 1)
    set_variable(f"{system_axis}{mbf_vars['Super_sequencer_count']}", harmonic_number)
    # change the number of captures to speed things up (normally 4096)
    set_variable(f"{system_axis}{seq1['count']}", ncap)
    # select the tune sweep frequency / mode
    set_variable(f"{system_axis}{seq1['start_frequency']}", startmode + start_freq)
    set_variable(f"{system_axis}{seq1['end_frequency']}", startmode + end_freq)
    # start the multi-mode sweep
    set_variable(f"{system_axis}{mbf_vars['triggers']['SEQ']['arm']}", 1)
    # download the data
    # (Eww['']  Convert axis string into 0 or 1[''])
    det_axis = np.find("xy" == mbf_axis) - 1
    [data, scale] = mbf_read_det(system_axis, "axis", det_axis, "lock", 1800)
    # reset the sweep
    configure_tune_sweep[mbf_axis, range(harmonic_number), 1, 1, 0, 0, 0]
    set_variable(f"{system_axis}{mbf_vars['triggers']['SEQ']['mode']}", "Rearm")
    set_variable(f"{system_axis}{pv_names['tails']['Sequencer']['reset']}", 1)
    # reshape the results
    fracttune = scale[1:ncap]
    for n in range(data.shape[1]):
        result = np.reshape(abs(data[:, n]), ncap, harmonic_number)
        # plot the results
        plt.figure[n]
        plt.imagesc(range(harmonic_number), fracttune, result)
        plt.xlabel("mode number")
        plt.ylabel("fractional tune")
        plt.ylabel("magnitude of response")

    # get the stored beam conditions
    fill_pattern = get_variable(pv_names["bunch_pattern"])
    current = get_variable(pv_names["current"])
    # save the data
    scipy.savemat(
        savefile,
        "data",
        "scale",
        "mbf_axis",
        "ncap",
        "startmode",
        "drive_bunch",
        "fb_on_off",
        "start_freq",
        "end_freq",
        "fill_pattern",
        "current",
    )
