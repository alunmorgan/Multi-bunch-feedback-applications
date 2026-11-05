import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy
from hardware_setup import configure_tune_sweep, reestablish_tune_measurement

from Common import (
    get_operational_mode,
    get_variable,
    hannwin,
    machine_environment,
    mbf_system_config,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def run_single_axis_measurement(
    setup_info: dict,
    hardware_setup_function,
    capture_function,
    restore_function,
    retrival_function,
):
    [root_string, harmonic_number, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]

    frontend = pv_names["frontend"]["base"]
    clock_phases = pv_names["frontend"]["clock_phase"]
    fe_gain = pv_names["frontend"]["gain"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    fe_system_phase = pv_names["frontend"]["system_phase"]
    if setup_info["mbf_axis"].lower() == "x" or setup_info["mbf_axis"].lower() == "y":
        fe_phase_pv = f"{frontend}{fe_system_phase[setup_info['mbf_axis']]}"
    else:
        fe_phase_pv = f"{frontend}{fe_system_phase['sI']}"
        fe_phase_pvQ = f"{frontend}{fe_system_phase['sQ']}"

    setup_info["harmonic_number"] = harmonic_number
    setup_info["fir_gain"] = get_variable(f"{pv_head}:FIR:GAIN_S")
    setup_info["orig_seq1_gain"] = get_variable(f"{pv_head}{sequencer1['gaindb']}")
    setup_info["original_frontend_clock_phase"] = get_variable(
        f"{frontend}{clock_phases[setup_info['mbf_ax']]}"
    )
    setup_info["original_frontend_gain"] = get_variable(
        f"{frontend}{fe_gain[setup_info['mbf_ax']]}"
    )
    setup_info["original_system_phase"] = get_variable(fe_phase_pv)
    if setup_info["mbf_ax"].lower() == "s":
        setup_info["original_system_phaseQ"] = get_variable(fe_phase_pvQ)
    if setup_info["bunches_monitored"] == "all":
        setup_info["bunches_monitored"] = np.ones(harmonic_number).tolist()

    if setup_info["auto_setup"] == "yes":
        # putting the system into a known state.
        setup_operational_mode(setup_info["mbf_axis"], setup_info["start_state"])
        # Setting the FIR gain to its original value.
        set_variable(f"{pv_head}:FIR:GAIN_S", setup_info["fir_gain"])

    setup_info["mbf_state"] = get_operational_mode(setup_info["mbf_axis"])
    # Setup the MBF ready for the measurement.
    if hardware_setup_function:
        restore_state = hardware_setup_function(setup_info, pv_names)
        time.sleep(2)
    # Capturing data.
    captured_data = capture_function(setup_info, pv_names)
    # adding to output data structure.
    data_fields = captured_data.keys()
    data = setup_info
    for je in range(len(data_fields)):
        data[data_fields[je]] = captured_data[data_fields[je]]

    if restore_function:
        restore_function(setup_info, pv_names, restore_state)

    if setup_info["auto_setup"] == "yes":
        setup_operational_mode(setup_info["mbf_axis"], setup_info["end_state"])
        # Setting the FIR gain to its original value.
        set_variable(f"{pv_head}:FIR:GAIN_S", setup_info["fir_gain"])
    else:
        reestablish_tune_measurement(setup_info["mbf_axis"])

    ## saving the data to a file
    save_to_archive(root_string, data)
    if setup_info["additional_save_location"]:
        scipy.savemat(setup_info["additional_save_location"], data)

    ## Plotting data
    if setup_info["plotting"] == "yes":
        # for archival investigations this allows filtering by machine state.
        # but for capture this is not needed so it set to empty.
        filter_conditions: list = []
        retrival_function(
            setup_info["mbf_axis"],
            [setup_info["time"], setup_info["time"]],
            filter_conditions,
        )


def run_multi_axis_measurement(
    setup_info: dict,
    hardware_setup_function,
    capture_function,
    restore_function,
    retrival_function,
):
    [root_string, harmonic_number, pv_names] = mbf_system_config()
    mbf_pv_x = pv_names["hardware_names"]["x"]
    mbf_pv_y = pv_names["hardware_names"]["y"]
    mbf_pv_s = pv_names["hardware_names"]["s"]
    frontend = pv_names["frontend"]["base"]
    clock_phases = pv_names["frontend"]["clock_phase"]
    fe_gain = pv_names["frontend"]["gain"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    fe_system_phase = pv_names["frontend"]["system_phase"]
    if setup_info["mbf_axis"].lower() == "x" or setup_info["mbf_axis"].lower() == "y":
        fe_phase_pv = f"{frontend}{fe_system_phase[setup_info['mbf_axis']]}"
    else:
        fe_phase_pv = f"{frontend}{fe_system_phase['sI']}"
        fe_phase_pvQ = f"{frontend}{fe_system_phase['sQ']}"

    setup_info["orig_seq1_gain_x"] = get_variable(f"{mbf_pv_x}{sequencer1['gaindb']}")
    setup_info["orig_seq1_gain_y"] = get_variable(f"{mbf_pv_y}{sequencer1['gaindb']}")
    setup_info["orig_seq1_gain_s"] = get_variable(f"{mbf_pv_s}{sequencer1['gaindb']}")
    setup_info["harmonic_number"] = harmonic_number
    setup_info["fir_gain_x"] = get_variable(f"{mbf_pv_x}:FIR:GAIN_S")
    setup_info["fir_gain_y"] = get_variable(f"{mbf_pv_y}:FIR:GAIN_S")
    setup_info["fir_gain_s"] = get_variable(f"{mbf_pv_s}:FIR:GAIN_S")
    setup_info["original_frontend_clock_phase"] = get_variable(
        f"{frontend}{clock_phases[setup_info['mbf_ax']]}"
    )
    setup_info["original_frontend_gain"] = get_variable(
        f"{frontend}{fe_gain[setup_info['mbf_ax']]}"
    )
    setup_info["original_system_phase"] = get_variable(fe_phase_pv)
    if setup_info["mbf_ax"].lower() == "s":
        setup_info["original_system_phaseQ"] = get_variable(fe_phase_pvQ)
    if setup_info["bunches_monitored"] == "all":
        setup_info["bunches_monitored"] = np.ones(harmonic_number).tolist()

    # Setup the MBF ready for the measurement.
    if hardware_setup_function:
        restore_state = hardware_setup_function(setup_info, pv_names)
        time.sleep(2)

    setup_info["mbf_state"] = get_operational_mode(setup_info["mbf_axis"])

    # Capturing data.
    captured_data = capture_function(setup_info, pv_names)
    # adding to output data structure.
    data_fields = captured_data.keys()
    data = setup_info
    for je in range(len(data_fields)):
        data[data_fields[je]] = captured_data[data_fields[je]]

    if restore_function:
        restore_function(setup_info, pv_names, restore_state)

    ## saving the data to a file
    save_to_archive(root_string, data)
    if setup_info["additional_save_location"]:
        scipy.savemat(setup_info["additional_save_location"], data)

    ## Plotting data
    if setup_info["plotting"] == "yes":
        # for archival investigations this allows filtering by machine state.
        # but for capture this is not needed so it set to empty.
        filter_conditions: list = []
        retrival_function(
            setup_info["mbf_axis"],
            [setup_info["time"], setup_info["time"]],
            filter_conditions,
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

    captured_data: dict[list] = {}
    for k in range(input_settings["repeat"]):
        # Arm, trigger, read
        if input_settings["mbf_axis"] == "s":
            # LMBF hardware
            set_variable(
                f"{pv_names['hardware_names']['L']}{pv_names['tails']['triggers']['MEM']['arm']}",
                1,
            )
            set_variable(
                f"{pv_names['hardware_names']['L']}{pv_names['tails']['triggers']['soft']}",
                1,
            )
            captured_data["raw_data"][k] = mbf_read_mem(
                pv_names["hardware_names"]["L"],
                input_settings["n_turns"],
                "channel",
                0,
                "lock",
                60,
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
            if input_settings["mbf_axis"] == "x":
                captured_data["raw_data"][k] = mbf_read_mem(
                    pv_names["hardware_names"]["T"],
                    input_settings["n_turns"],
                    "channel",
                    0,
                    "lock",
                    60,
                )
            else:
                captured_data["raw_data"][k] = mbf_read_mem(
                    pv_names["hardware_names"]["T"],
                    input_settings["n_turns"],
                    "channel",
                    1,
                    "lock",
                    60,
                )
    return captured_data


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
    configure_tune_sweep(mbf_axis, range(harmonic_number), 1, 1, 0, 0, 0)
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


def clock_phase_scan_capture(setup_info, pv_names):

    detector = pv_names["tails"]["Detector"]
    adc = pv_names["tails"]["adc"]
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
    frontend = pv_names["frontend"]["base"]
    clock_phase = pv_names["frontend"]["clock_phase"][setup_info["mbf_axis"]]
    fe_phase_pv = f"{frontend}{clock_phase}"
    data = setup_info
    # set up the sweep
    data["phase"] = range(
        setup_info["sweep_start"], setup_info["sweep_end"], setup_info["sweep_step"]
    )
    data["phase"].extend(
        range(
            setup_info["sweep_end"] - setup_info["sweep_step"],
            setup_info["sweep_start"],
            -setup_info["sweep_step"],
        )
    )
    # moving to starting point in scan
    for pp in range(
        setup_info["original_frontend_clock_phase"],
        setup_info["sweep_start"],
        -setup_info["sweep_step"],
    ):
        set_variable(fe_phase_pv, pp)
        time.sleep(0.5)

    data["side1"] = []
    data["main"] = []
    data["side2"] = []
    data["adc_phase"] = []
    for x in range(len(data["phase"])):
        set_variable(fe_phase_pv, data["phase"][x])
        time.sleep(0.5)
        data["side1"][x] = max(get_variable(f"{pv_head}{detector['det1']['power']}"))
        data["main"][x] = max(get_variable(f"{pv_head}{detector['det2']['power']}"))
        data["side2"][x] = max(get_variable(f"{pv_head}{detector['det3']['power']}"))
        if data["mbf_axis"].lower() == "s":
            data["adc_phase"][x] = max(get_variable(f"{pv_head}{adc['phase']['mean']}"))
            data["adc_mean"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['min']}"))
            data["adc_meanQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['mean']}"))
            data["adc_maxQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['max']}"))
            data["adc_minQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['min']}"))
        else:
            data["adc_mean"][x] = max(get_variable(f"{pv_head}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{pv_head}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{pv_head}{adc['min']}"))

    # move back to the original setting
    for pp in range(
        data["sweep_start"], data["original_frontend_clock_phase"], data["sweep_step"]
    ):
        set_variable(fe_phase_pv, pp)
        time.sleep(0.5)
    return data


def bbbfe_gain_scan_capture(setup_info, pv_names):
    adc = pv_names["tails"]["adc"]
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
    frontend = pv_names["frontend"]["base"]
    fe_gain = pv_names["frontend"]["gain"]
    fe_gain_pv = f"{frontend}{fe_gain[setup_info['mbf_axis']]}"

    data = setup_info
    # set up the sweep
    setup_info["gain"] = range(
        setup_info["sweep_start"], setup_info["sweep_end"], setup_info["sweep_step"]
    )
    setup_info["gain"].extend(
        range(
            setup_info["sweep_end"] - setup_info["sweep_step"],
            setup_info["sweep_start"],
            -setup_info["sweep_step"],
        )
    )
    # prealloacation
    data["adc_mean"] = []
    data["adc_max"] = []
    data["adc_min"] = []

    # moving to starting point in scan
    for pp in range(
        setup_info["original_frontend_gain"],
        setup_info["sweep_start"],
        -setup_info["sweep_step"],
    ):
        set_variable(fe_gain_pv, pp)
        time.sleep(0.5)

    # measurement
    for x in range(len(setup_info["gain"])):
        set_variable(fe_gain_pv, setup_info["gain"][x])
        time.sleep(setup_info["sweep_speed"])
        data["adc_mean"][x] = max(get_variable([pv_head, adc["mean"]]))
        data["adc_max"][x] = max(get_variable([pv_head, adc["max"]]))
        data["adc_min"][x] = max(get_variable([pv_head, adc["min"]]))

    # move back to the original setting
    for pp in range(
        setup_info["sweep_start"],
        setup_info["original_frontend_gain"],
        setup_info["sweep_step"],
    ):
        set_variable(fe_gain_pv, pp)
        time.sleep(0.5)
    return data


def bbbfe_system_phase_scan_capture(setup_info, pv_names):
    [root_string, _1, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]

    detector = pv_names["tails"]["Detector"]
    adc = pv_names["tails"]["adc"]
    frontend = pv_names["frontend"]["base"]
    fe_system_phase = pv_names["frontend"]["system_phase"]

    if setup_info["mbf_axis"].lower() == "x" or setup_info["mbf_axis"].lower() == "y":
        fe_phase_pv = f"{frontend}{fe_system_phase[setup_info['mbf_axis']]}"
    else:
        fe_phase_pv = f"{frontend}{fe_system_phase['sI']}"
        fe_phase_pvQ = f"{frontend}{fe_system_phase['sQ']}"

    # set up the sweep
    setup_info["phase"] = range(
        setup_info["sweep_start"], setup_info["sweep_end"], setup_info["sweep_step"]
    )
    setup_info["phase"].extend(
        range(
            setup_info["sweep_end"] - setup_info["sweep_step"],
            setup_info["sweep_start"] - setup_info["sweep_step"],
        )
    )
    data = setup_info
    # prealloacation
    data["side1"] = []
    data["main"] = []
    data["side2"] = []
    data["adc_phase"] = []

    # moving to starting point in scan
    for pp in range(
        data["original_system_phase"],
        setup_info["sweep_start"],
        -setup_info["sweep_step"],
    ):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if setup_info["mbf_axis"].lower() == "s":
        # I and Q must be in quadrature
        for pp in (
            range(
                data["original_system_phaseQ"],
                setup_info["sweep_start"],
                -setup_info["sweep_step"],
            )
            + 90
        ):
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    # measurement
    for x in range(len(data["phase"])):
        set_variable(fe_phase_pv, data["phase"][x])
        if setup_info["mbf_axis"].lower() == "s":
            set_variable(fe_phase_pvQ, data["phase"][x] + 90)

        time.sleep(setup_info["sweep_speed"])
        data["side1"][x] = max(get_variable(f"{pv_head}{detector['det1']['power']}"))
        data["main"][x] = max(get_variable(f"{pv_head}{detector['det2']['power']}"))
        data["side2"][x] = max(get_variable(f"{pv_head}{detector['det3']['power']}"))
        if setup_info["mbf_ax"].lower() == "s":
            data["adc_phase"][x] = max(get_variable(f"{pv_head}{adc['phase']['mean']}"))
            data["adc_mean"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{pv_head[1:-2]}{adc['min']}"))
            data["adc_meanQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['mean']}"))
            data["adc_maxQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['max']}"))
            data["adc_minQ"][x] = max(get_variable(f"{pv_head[1:-3]}Q{adc['min']}"))
        else:
            data["adc_mean"][x] = max(get_variable(f"{pv_head}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{pv_head}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{pv_head}{adc['min']}"))

    # move back to the original setting
    for pp in range(
        data["sweep_start"], data["original_system_phase"], data["sweep_step"]
    ):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if setup_info["mbf_axis"].lower() == "s":
        # move back to the original setting
        for pp in range(
            data["sweep_start"] + 90, data["original_system_phaseQ"], data["sweep_step"]
        ):
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    return data


def doris_target_phase_scan_capture(setup_info, pv_names):
    [root_string, _1, pv_names] = mbf_system_config()

    doris_pv = pv_names["doris"]["phase"]
    detector = pv_names["tails"]["Detector"]

    setup_info["original_doris_target_phase"] = get_variable(doris_pv)

    # set up the sweep
    setup_info["phase"] = range(
        setup_info["sweep_start"], setup_info["sweep_end"], setup_info["sweep_step"]
    )
    setup_info["phase"].extend(
        range(
            setup_info["sweep_end"] - setup_info["sweep_step"],
            setup_info["sweep_start"],
            -setup_info["sweep_step"],
        )
    )
    data = setup_info
    # prealloacation
    data["side1_x"] = []
    data["main_x"] = []
    data["side2_x"] = []
    data["side1_y"] = []
    data["main_y"] = []
    data["side2_y"] = []

    # moving to starting point in scan
    set_variable(doris_pv, -180)
    for dbf in range(1, len(data["phase"])):
        set_variable(doris_pv, data["phase"][dbf])
        time.sleep(2)
        data["side1_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det1']['power']}")
        )
        data["main_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det2']['power']}")
        )
        data["side2_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det3']['power']}")
        )
        data["side1_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det1']['power']}")
        )
        data["main_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det2']['power']}")
        )
        data["side2_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det3']['power']}")
        )
        print(".")

    # move back to the original setting
    set_variable(doris_pv, data["original_doris_target_phase"])
    return data


def mbf_pll_phase_scan_capture(setup_info, pv_names):
    [root_path, _1, pv_names] = mbf_system_config()
    name = pv_names["hardware_names"][setup_info["mbf_axis"]]
    pll_tails = pv_names["tails"]["pll"]
    setup_info["mbf_fll"]["target_bunches"] = get_variable(
        f"{name}{pll_tails['detector']['target_bunches']}"
    )
    setup_info["mbf_fll"]["gain"] = get_variable(f"{name}{pll_tails['nco']['gain']}")
    setup_info["mbf_fll"]["target_phase"] = get_variable(
        f"{name}{pll_tails['target_phase']}"
    )
    setup_info["mbf_fll"]["KI"] = get_variable(f"{name}{pll_tails['i']}")
    setup_info["mbf_fll"]["KP"] = get_variable(f"{name}{pll_tails['p']}")

    start = get_variable(f"{name}{pll_tails['target_phase']}")
    setup_info["phase"] = range(
        start, start + setup_info["scan_range"], setup_info["scan_step"]
    )
    setup_info["phase"].extend(
        range(
            start + setup_info["scan_range"],
            start - setup_info["scan_range"],
            -setup_info["scan_step"],
        )
    )
    setup_info["phase"].extend(
        range(
            start - setup_info["scan_range"],
            start + setup_info["scan_range"],
            setup_info["scan_step"],
        )
    )
    setup_info["phase"].extend(
        range(start + setup_info["scan_range"], start, -setup_info["scan_step"])
    )

    data = setup_info

    data["mag"] = []
    data["iq"] = []
    data["f"] = []
    for n in range(len(setup_info["phase"])):
        status = get_variable(f"{name}{pll_tails['status']}")
        if status == "Running":
            # the funny mod is required to get into the right range of -180 to +179
            set_variable(
                f"{name}{pll_tails['target_phase']}",
                np.mod(setup_info["phase"][n] + 180, 360) - 180,
            )
            # This will depend on the dwell time and PLL config,
            # but works with the default
            time.sleep(2)
            # get magnitude
            data["mag"][n] = get_variable(f"{name}{pll_tails['readback']['magnitude']}")
            # get phase readback
            data["phase"][n] = get_variable(f"{name}{pll_tails['readback']['phase']}")
            data["iq"][n] = [1, np.i] * get_variable(
                f"{name}{pll_tails['readback']['i']}{name}{pll_tails['readback']['q']}"
            )
            data["f"][n] = get_variable(f"{name}{pll_tails['nco']['frequency']}")
        else:
            set_variable(f"{name}{pll_tails['target_phase']}", start)
            raise ValueError(
                "PLL:stoppedUnexpectedly"
                "PLL stopped during phase sweep, please restart using fll_start"
            )

    return data
