import datetime
import time

import numpy as np

from Common import (
    get_variable,
    mbf_fll_setup,
    mbf_system_config,
    set_variable,
)


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


def mbf_bunch_motion_setup(setup_info, pv_names: dict):
    # Sets up all three axis so that they will take a single set of data each
    # when armed and triggered
    #
    # Example: mbf_bunch_motion_setup
    mbf_tools()
    Bunch_bank1 = pv_names["tails"]["Bunch_bank"]["bank1"]

    # Add the extra data to the data structure.
    bunch_motion["base_name"] = "Bunch_motion"
    bunch_motion["harmonic_number"] = harmonic_number
    if auto_setup == "yes":
        # Get the current FIR gains
        # FIXME which bank???
        orig_fir_gain_x = get_variable(
            f"{pv_names['hardware_names']['x']}{Bunch_bank['FIR_gains']}"
        )
        orig_fir_gain_y = get_variable(
            f"{pv_names['hardware_names']['y']}{Bunch_bank['FIR_gains']}"
        )
        orig_fir_gain_s = get_variable(
            f"{pv_names['hardware_names']['s']}{Bunch_bank['FIR_gains']}"
        )
        # Programatically press the tune only button on each system['']
        setup_operational_mode("x", "TuneOnly")
        setup_operational_mode("y", "TuneOnly")
        setup_operational_mode("s", "TuneOnly")

    bunch_motion["mbf_state_x"] = get_operational_mode("x")
    bunch_motion["mbf_state_y"] = get_operational_mode("y")
    bunch_motion["mbf_state_s"] = get_operational_mode("s")

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


def clock_phase_scan_setup(setup_info, pv_names):

    if setup_info["auto_setup"] == "yes":
        original_detector_setup = BBBFE_detector_setup(
            setup_info["mbf_ax"], setup_info["single_bunch_location"]
        )


def clock_phase_scan_restore(setup_info, pv_names, restore_state):
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]

    if setup_info["auto_setup"] == "yes":
        BBBFE_detector_restore(setup_info["mbf_axis"], original_detector_setup)
        set_variable(f"{pv_head}{sequencer1['gaindb']}", setup_info["orig_seq1_gain"])


def bbbfe_system_phase_scan_setup(setup_info, pv_names):
    original_detector_setup = BBBFE_detector_setup(
        setup_info["mbf_axis"], setup_info["single_bunch_location"]
    )
    return original_detector_setup


def bbbfe_system_phase_scan_restore(setup_info, pv_names, restore_state):
    if setup_info["auto_setup"] == "yes":
        pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
        sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
        set_variable(f"{pv_head}{sequencer1['gaindb']}", setup_info["orig_seq1_gain"])

    BBBFE_detector_restore(setup_info["mbf_ax"], restore_state)


def doris_target_phase_scan_setup(setup_info, pv_names):
    if setup_info["auto_setup"] == "yes":
        setup_operational_mode("x", "TuneOnly")
        setup_operational_mode("y", "TuneOnly")
        setup_operational_mode("s", "TuneOnly")
    original_state = {}
    original_state["detector_setup_x"] = BBBFE_detector_setup(
        "x", setup_info["single_bunch_location"]
    )
    original_state["detector_setup_y"] = BBBFE_detector_setup(
        "y", setup_info["single_bunch_location"]
    )
    original_state["detector_setup_s"] = BBBFE_detector_setup(
        "s", setup_info["single_bunch_location"]
    )


def doris_target_phase_scan_restore(setup_info, pv_names, restore_state):
    mbf_pv_x = pv_names["hardware_names"]["x"]
    mbf_pv_y = pv_names["hardware_names"]["y"]
    mbf_pv_s = pv_names["hardware_names"]["s"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]

    if setup_info["auto_setup"] == "yes":
        setup_operational_mode("x", "TuneOnly")
        set_variable(f"{mbf_pv_x}{sequencer1['gaindb']}", setup_info["orig_gain_x"])
        setup_operational_mode("y", "TuneOnly")
        set_variable(f"{mbf_pv_y}{sequencer1['gaindb']}", setup_info["orig_gain_y"])
        setup_operational_mode("s", "TuneOnly")
        set_variable(f"{mbf_pv_s}{sequencer1['gaindb']}", setup_info["orig_gain_s"])
    BBBFE_detector_restore("x", restore_state["detector_setup_x"])
    BBBFE_detector_restore("y", restore_state["detector_setup_y"])
    BBBFE_detector_restore("s", restore_state["detector_setup_s"])
    reestablish_tune_measurement("x")
    reestablish_tune_measurement("y")
    reestablish_tune_measurement("s")


def tunescan_over_modes_restore(setup_info, pv_names, restore_state):
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
    # reset the sweep
    ####Is this section needed or does the TuneOnly script take care of things?
    configure_tune_sweep(
        setup_info["mbf_axis"], range(setup_info["harmonic_number"]), 1, 1, 0, 0, 0
    )
    set_variable(f"{pv_head}{pv_names['tails']['triggers']['mode']}", "Rearm")
    set_variable(f"{pv_head}{pv_names['tails']['Sequencer']['reset']}", 1)
    #######
    if setup_info["auto_setup"] == "yes":
        # Programatically press the tune only button on each system
        setup_operational_mode(setup_info["mbf_axis"], "TuneOnly")


def bunch_motion_restore(setup_info, pv_names, restore_state):

    if setup_info["auto_setup"] == "yes":
        setup_operational_mode("x", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['x']}{Bunch_bank['FIR_gains']}",
            restore_state["orig_fir_gain_x"],
        )
        setup_operational_mode("y", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['y']}{Bunch_bank['FIR_gains']}",
            restore_state["orig_fir_gain_y"],
        )
        setup_operational_mode("s", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['s']}{Bunch_bank['FIR_gains']}",
            restore_state["orig_fir_gain_s"],
        )
