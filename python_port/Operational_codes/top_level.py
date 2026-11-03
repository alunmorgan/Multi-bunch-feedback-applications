import datetime
import time

import numpy as np
import scipy
from measurements import (
    BBBFE_detector_restore,
    BBBFE_detector_setup,
    DORIS_phase_scan_plotting,
    fll_phase_scan_plotting,
    mbf_bunch_motion_archival_retrieval,
    mbf_bunch_motion_capture,
    mbf_bunch_motion_setup,
    mbf_frontend_gain_scan_archival_retrieval,
    mbf_frontend_system_phase_scan_archival_retrieval,
    mbf_growdamp_archival_retrieval,
    mbf_growdamp_capture,
    mbf_growdamp_setup,
    mbf_modescan_archival_retrieval,
    mbf_modescan_capture,
    mbf_modescan_setup,
    mbf_pll_start,
    mbf_spectra_archival_retrieval,
    mbf_spectrum_capture,
    mbf_spectrum_setup,
    run_single_axis_measurement,
)

from Common import (
    get_operational_mode,
    get_variable,
    machine_environment,
    mbf_system_config,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def growdamp_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    excitation_setting: str = "yes",
    excitation_location: str = "tune",
    excitation_manual: int = 0,
    pll_tracking: str = "no",
    pll_bunches: int = 400,
    pll_guard_bunches: int = 10,
    bunches_monitored: list[int] | str = "all",
    capture_full_bunch_motion: str = "no",
) -> None:
    # Top level def to run the growdamp measurements on the:
    # selected plane
    #   Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       excitation(str): sets whether the measurement uses an excitation to
    #                        drive a resonance or if the measurement just uses the
    #                        natural beam coupling.
    #                        Defaults to 'yes'
    #       excitation_location(str): The location of the excitation in tune space.
    #                                 The default value is 'tune'.
    #       excitation_manual(float): if excitation_location is set to 'manual' then
    #                                 this defines the location of the excitation
    #                                 in tune space.
    #       pll_tracking (str): Sets if the excitation frequency follows the tune
    #                           jitter. Default is no
    #       pll_bunches (float): bunches the pll is active on.
    #       pll_guard_bunches (float): the number of bunches surrounding the pll
    #                                  bunches for which feedback is switched off.
    #       bunch_monitor(list(int)) | str: This determines which bunches are monitored
    #                                 during the measurement. Defaults to 'all' which
    #                                 means all bunches.
    #       capture_full_bunch_motion(str): Captures the centroid motion for the
    #                                       duration of the measuremnt.
    #                                       Defaults to no as this is a lot of data.
    # Example: growdamp_all('x')

    ## Constructing the different states for the sequencer. These will be arranged
    # in various configurations depending on the experiment requested.
    #
    # bank = 1 is Feedback off
    # bank = 2 is Feedback on
    #       tune_offset (float): Tune fraction to offset from the peak.
    #       dwell (int): number of turns at each point.
    #       durations (struct): number of points for each stage.
    growth: dict = {}
    excitation: dict = {}
    passive: dict = {}
    active: dict = {}
    spacer: dict = {}
    if mbf_axis.lower() == "x" or mbf_axis.lower() == "y":
        # Passive Growth
        growth["duration"] = 2500
        growth["dwell"] = 1
        growth["capture"] = "Capture"
        growth["excitation"] = "Off"
        growth["excitation_level"] = "-48dB"
        growth["bank"] = 1
        # Excitation
        excitation["duration"] = 750
        excitation["dwell"] = 1
        excitation["capture"] = "Capture"
        excitation["excitation"] = "On"
        excitation["excitation_level"] = "-18dB"
        excitation["bank"] = 1
        # Passive decay (assuming no instability)
        passive["duration"] = 1500
        passive["dwell"] = 1
        passive["capture"] = "Capture"
        passive["excitation"] = "Off"
        passive["excitation_level"] = "-48dB"
        passive["bank"] = 1
        # Feedback active
        active["duration"] = 1500
        active["dwell"] = 1
        active["capture"] = "Capture"
        active["excitation"] = "Off"
        active["excitation_level"] = "-48dB"
        active["bank"] = 2
        # Feedback active but no capture
        spacer["duration"] = 4000
        spacer["dwell"] = 1
        spacer["capture"] = "Discard"
        spacer["excitation"] = "Off"
        spacer["excitation_level"] = "-48dB"
        spacer["bank"] = 2
        tune_offset = 0
    elif mbf_axis.lower() == "s":
        growth["duration"] = 10
        growth["dwell"] = 480
        growth["capture"] = "Capture"
        growth["excitation"] = "Off"
        growth["excitation_level"] = "-48dB"
        growth["bank"] = 1
        # Excitation
        excitation["duration"] = 10
        excitation["dwell"] = 480
        excitation["capture"] = "Capture"
        excitation["excitation"] = "On"
        excitation["excitation_level"] = "-18dB"
        excitation["bank"] = 1
        # Passive decay (assuming no instability)
        passive["duration"] = 10
        passive["dwell"] = 480
        passive["capture"] = "Capture"
        passive["excitation"] = "Off"
        passive["excitation_level"] = "-48dB"
        passive["bank"] = 1
        # Feedback active
        active["duration"] = 50
        active["dwell"] = 480
        active["capture"] = "Capture"
        active["excitation"] = "Off"
        active["excitation_level"] = "-48dB"
        active["bank"] = 2
        # Feedback active but no capture
        spacer["duration"] = 100
        spacer["dwell"] = 480
        spacer["capture"] = "Discard"
        spacer["excitation"] = "Off"
        spacer["excitation_level"] = "-48dB"
        spacer["bank"] = 2
        tune_offset = 0

    # getting general environment data.
    growdamp = machine_environment()
    ## Setting up the growdamp experiments.
    states: list = []
    state_names: list = []
    if excitation_setting == "no":
        states[1] = growth
        states[0] = active
        state_names[1] = "growth"
        state_names[0] = "active"
    else:
        states[5] = excitation
        states[4] = passive
        states[3] = spacer
        states[2] = excitation
        states[1] = active
        states[0] = spacer
        state_names[5] = "excitation"
        state_names[4] = "passive"
        state_names[3] = "spacer"
        state_names[2] = "excitation"
        state_names[1] = "active"
        state_names[0] = "spacer"
        if "lower_sideband" in excitation_location:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["lower_sideband"] + tune_offset
            )
        elif "upper_sideband" in excitation_location:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["upper_sideband"] + tune_offset
            )
        elif "manual" in excitation_location:
            excitation_tune = excitation_manual
        else:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["tune"] + tune_offset
            )

    # Add the extra data to the data structure.
    growdamp["ax_label"] = mbf_axis
    growdamp["base_name"] = ["Growdamp_", mbf_axis, "_axis"]
    growdamp["excitation_tune"] = excitation_tune
    growdamp["states"] = states
    growdamp["state_names"] = state_names
    growdamp["mbf_axis"] = mbf_axis
    growdamp["auto_setup"] = auto_setup
    growdamp["plotting"] = plotting
    growdamp["additional_save_location"] = additional_save_location
    growdamp["excitation_setting"] = excitation_setting
    growdamp["excitation_location"] = excitation_location
    growdamp["excitation_manual"] = excitation_manual
    growdamp["pll_tracking="] = pll_tracking
    growdamp["pll_bunches"] = pll_bunches
    growdamp["pll_guard_bunches"] = pll_guard_bunches
    growdamp["bunches_monitored"] = bunches_monitored
    growdamp["capture_full_bunch_motion"] = capture_full_bunch_motion
    growdamp["start_state"] = "Feedback"
    growdamp["end_state"] = "Feedback"

    run_single_axis_measurement(
        setup_info=growdamp,
        hardware_setup_function=mbf_growdamp_setup,
        capture_function=mbf_growdamp_capture,
        restore_function=None,
        retrival_function=mbf_growdamp_archival_retrieval,
    )


def modescan_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_repeats: int = 10,
    dwell: int = 500,
    excitation_gain: float = -30,
):
    # Top level def to run the modescan for all selected plane.:
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       n_repeats(int): How many times to repeat each measurement point.
    #       dwell (int): How many turns to stay at each measurement point.
    #       excitation_gain(float): level of the excitation.
    #
    # Example  modescan_all('x')

    # getting general environment data
    modescan = machine_environment()
    # Add the extra data to the data structure.
    modescan["ax_label"] = mbf_axis
    modescan["base_name"] = f"Modescan_{mbf_axis}_axis"
    modescan["excitation_tune"] = modescan["tunes"][f"{mbf_axis}_tune"]["tune"]
    modescan["mbf_axis"] = mbf_axis
    modescan["auto_setup"] = auto_setup
    modescan["plotting"] = plotting
    modescan["additional_save_location"] = additional_save_location
    modescan["n_repeats"] = n_repeats
    modescan["dwell"] = dwell
    modescan["excitation_gain"] = excitation_gain
    modescan["start_state"] = "TuneOnly"
    modescan["end_state"] = "Feedback"

    run_single_axis_measurement(
        setup_info=modescan,
        hardware_setup_function=mbf_modescan_setup,
        capture_function=mbf_modescan_capture,
        restore_function=None,
        retrival_function=mbf_modescan_archival_retrieval,
    )


def mbf_spectrum_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_turns: int = 1000,
    repeat: int = 1,
):
    # Top level def to run all spectral measurements on selected plane.:
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       n_turns (int): number of turns to capture. Default is 1000.
    #       repeat (int): Number of repeat points (improves the power resolution).
    #                     Default is 1.
    #
    # Example mbf_spectrum_all

    # getting general environment data.
    spectrum = machine_environment()
    # Add the extra data to the data structure.
    spectrum["ax_label"] = mbf_axis
    spectrum["base_name"] = f"Spectrum_{mbf_axis}_axis"
    spectrum["mbf_axis"] = mbf_axis
    spectrum["auto_setup"] = auto_setup
    spectrum["plotting"] = plotting
    spectrum["additional_save_location"] = additional_save_location
    spectrum["n_turns"] = n_turns
    spectrum["repeat"] = repeat
    spectrum["start_state"] = "TuneOnly"
    spectrum["end_state"] = "Feedback"

    run_single_axis_measurement(
        setup_info=spectrum,
        hardware_setup_function=mbf_spectrum_setup,
        capture_function=mbf_spectrum_capture,
        restore_function=None,
        retrival_function=mbf_spectra_archival_retrieval,
    )


def Bunch_motion_all(
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
):
    [root_string, harmonic_number, pv_names] = mbf_system_config()
    mbf_tools()
    Bunch_bank1 = pv_names["tails"]["Bunch_bank"]["bank1"]

    # getting general environment data
    bunch_motion = machine_environment()
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
    mbf_bunch_motion_setup(pv_names)
    captured_data = mbf_bunch_motion_capture(pv_names)
    # adding to output data structure['']
    data_fields = captured_data.keys()
    for je in range(len(data_fields)):
        bunch_motion[data_fields[je]] = captured_data[data_fields[je]]

    if auto_setup == "yes":
        setup_operational_mode("x", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['x']}{Bunch_bank['FIR_gains']}",
            orig_fir_gain_x,
        )
        setup_operational_mode("y", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['y']}{Bunch_bank['FIR_gains']}",
            orig_fir_gain_y,
        )
        setup_operational_mode("s", "Feedback")
        set_variable(
            f"{pv_names['hardware_names']['s']}{Bunch_bank['FIR_gains']}",
            orig_fir_gain_s,
        )

    ## saving the data to a file
    save_to_archive(root_string, bunch_motion)
    if additional_save_location:
        scipy.savemat(additional_save_location, bunch_motion)

    ## Plotting data
    if plotting == "yes":
        # for archival investigations this allows filtering by machine state.
        # but for capture this is not needed so it set to empty.
        filter_conditions: list = []
        mbf_bunch_motion_archival_retrieval(
            [bunch_motion["time"], bunch_motion["time"]], filter_conditions
        )


def BBBFE_LO_scan(phase_centre: int, sweep_extent: int):
    # Scans the LO phase shift in the bunch by bunch frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #     phase_centre (int): The phase value to center the sweep on.
    #     sweep_extent (int): The range to sweep. 45 would sweep 45 degrees
    #                         above and 45 degrees below the centre value.
    #
    # Example: BBBFE_LO_scan(90, 45)
    root_string = mbf_system_config()
    data: dict = {}
    data["phase_pv"] = "SR23C-DI-BBFE-01:PHA"
    old_val = get_variable(data["phase_pv"])
    data["n"] = range(
        phase_centre - sweep_extent,
        phase_centre + sweep_extent,
        np.ceil(sweep_extent / 20),
    )
    data["t1"] = []
    data["t2"] = []
    data["t3"] = []
    for jd in range(len(data["n"])):
        set_variable(data["phase_pv"], data["n"](jd))
        time.sleep(2)
        data["t1"][jd] = max(get_variable("SR23C-DI-TMBF-01:TUNE:POWER"))
        data["t2"][jd] = max(get_variable("SR23C-DI-TMBF-02:TUNE:POWER"))
        data["t3"][jd] = max(get_variable("SR23C-DI-TMBF-03:TUNE:POWER"))

    set_variable(data["phase_pv"], old_val)

    data["time"] = datetime.datetime.now()
    data["base_name"] = "LO_scan"
    ## saving the data to a file
    save_to_archive(root_string, data)

    # graph_handles = plt.figure
    # plt.plot(
    #     data["n"],
    #     data["t1"] / max(data["t1"]),
    #     "b",
    #     data["n"],
    #     data["t2"] / max(data["t2"]),
    #     "r",
    #     data["n"],
    #     data["t3"] / max(data["t3"]),
    #     "c",
    # )
    # plt.xlabel("LO phase (degrees)")
    # plt.ylabel("tune max value (normalised)")
    # plt.legend("X", "Y", "S")


def BBBFE_clock_phase_scan(
    mbf_ax: str,
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 10,
    sweep_end: int = 180,
):
    # Scans one of the clock phase shifts in the bunch by bunch frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #      ax (str): Specifies which axis.
    #      single_bunch_location (int): the location of the single bunch.
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): phase value in degrees to start the sweep.
    #       sweep_step(int):  phase scan step in degrees.
    #       sweep_end(int):   phase value in degreees to stop the sweep.
    #
    #
    # Machine setup: (manual for the time being.)
    # fill some charge in bunch 1 (0['2nC'])
    #
    # Example: BBBFE_clock_phase_scan('x', 400)

    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["base_name"] = f"clock_phase_scan_{mbf_ax}_axis"
    data["mbf_ax"] = mbf_ax
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=clock_phase_scan_setup,
        capture_function=clock_phase_scan_capture,
        restore_function=clock_phase_scan_restore,
        retrival_function=clock_phase_scan_retrival,
    )


def clock_phase_scan_setup(setup_info, pv_names):

    if setup_info["auto_setup"] == "yes":
        original_detector_setup = BBBFE_detector_setup(
            setup_info["mbf_ax"], setup_info["single_bunch_location"]
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


def clock_phase_scan_restore(setup_info, pv_names, restore_state):
    pv_head = pv_names["hardware_names"][setup_info["mbf_axis"]]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]

    if setup_info["auto_setup"] == "yes":
        BBBFE_detector_restore(setup_info["mbf_axis"], original_detector_setup)
        set_variable(f"{pv_head}{sequencer1['gaindb']}", setup_info["orig_seq1_gain"])

    # ## saving the data to a file
    # save_to_archive(root_string, data)
    # if additional_save_location:
    #     scipy.savemat(additional_save_location, data)

    # ## plotting
    # if plotting == "yes":
    #     # for archival investigations this allows filtering by machine state.
    #     # but for capture this is not needed so it set to empty.
    #     filter_conditions: list = []
    #     mbf_frontend_clock_phase_scan_archival_retrieval(
    #         mbf_ax, [data["time"], data["time"]], filter_conditions
    #     )


def BBBFE_full_frontend_checkout(single_bunch_location: int):
    # BBBFE_FULL_FRONTEND_CHECKOUT
    # This assumes that the machine is set up with a single bunch in the machine at
    # the single_bunch_location
    BBBFE_system_phase_scan("x", single_bunch_location)
    BBBFE_system_phase_scan("y", single_bunch_location)
    BBBFE_system_phase_scan("s", single_bunch_location)
    BBBFE_clock_phase_scan("x", single_bunch_location)
    BBBFE_clock_phase_scan("y", single_bunch_location)
    BBBFE_clock_phase_scan("s", single_bunch_location)


def BBBFE_gain_scan(
    mbf_ax: str,
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -40,
    sweep_step: int = 5,
    sweep_end: int = 10,
    sweep_speed: int = 2,
):
    # Scans one of the individual axis gains in the
    # bunch by bunch frontend and records the strength of the ADC signal.
    # Restores the original value after the scan.
    #
    # Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): level value to start the sweep.
    #       sweep_step(int):  level step.
    #       sweep_end(int):   level value to stop the sweep.
    #
    # Machine setup
    # machine to nominal conditions
    #
    # Example: BBBFE_gain_scan('x')
    [root_string, _1, pv_names] = mbf_system_config()
    adc = pv_names["tails"]["adc"]
    frontend = pv_names["frontend"]["base"]
    fe_gain = pv_names["frontend"]["gain"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    mbf_pv = pv_names["hardware_names"][mbf_ax]
    fe_gain_pv = f"{frontend}{fe_gain[mbf_ax]}"

    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_ax
    data["base_name"] = ["frontend_gain_scan_", mbf_ax, "_axis"]
    data["orig_gain"] = get_variable([mbf_pv, sequencer1["gaindb"]])
    data["original_setting"] = get_variable(fe_gain_pv)
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed

    # set up the sweep
    data["gain"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["gain"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"],
            -data["sweep_step"],
        )
    )
    # prealloacation
    data["adc_mean"] = []
    data["adc_max"] = []
    data["adc_min"] = []
    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")

    # moving to starting point in scan
    for pp in range(data["original_setting"], sweep_start, -sweep_step):
        set_variable(fe_gain_pv, pp)
        time.sleep(0.5)

    # measurement
    for x in range(len(data["gain"])):
        set_variable(fe_gain_pv, data["gain"][x])
        time.sleep(sweep_speed)
        data["adc_mean"][x] = max(get_variable([mbf_pv, adc["mean"]]))
        data["adc_max"][x] = max(get_variable([mbf_pv, adc["max"]]))
        data["adc_min"][x] = max(get_variable([mbf_pv, adc["min"]]))

    # move back to the original setting
    for pp in range(data["sweep_start"], data["original_setting"], data["sweep_step"]):
        set_variable(fe_gain_pv, pp)
        time.sleep(0.5)

    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")
        set_variable(f"{mbf_pv}{sequencer1['gaindb']}", data["orig_gain"])

    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## Plotting data
    if plotting == "yes":
        # for archival investigations this allows filtering by machine state.
        # but for capture this is not needed so it set to empty.
        filter_conditions: list = []
        mbf_frontend_gain_scan_archival_retrieval(
            mbf_ax, [data["time"], data["time"]], filter_conditions
        )


def BBBFE_system_phase_scan(
    mbf_ax: str,
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 10,
    sweep_end: int = 180,
    sweep_speed: int = 2,
):
    # Scans one of the individual axis system phase shifts in the
    # bunch by bunch frontend and records the strength of the tune signal['']
    # Restores the original value after the scan['']
    #
    # Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       single_bunch_location(int): location of the target bunch['']
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes['']
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes['']
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive['']
    #       sweep_start(int): phase value in degrees to start the sweep['']
    #       sweep_step(int):  phase scan step in degrees['']
    #       sweep_end(int):   phase value in degreees to stop the sweep['']
    #
    # Machine setup
    # fill some charge in bunch 'single_bunch_location' (0['2nC'])
    #
    # Example: BBBFE_system_phase_scan('x', 400)
    [root_string, _1, pv_names] = mbf_system_config()
    detector = pv_names["tails"]["Detector"]
    adc = pv_names["tails"]["adc"]
    frontend = pv_names["frontend"]["base"]
    fe_system_phase = pv_names["frontend"]["system_phase"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    mbf_pv = pv_names["hardware_names"][mbf_ax]
    if mbf_ax.lower() == "x" or mbf_ax.lower() == "y":
        fe_phase_pv = f"{pv_names['frontend']['base']}{fe_system_phase[mbf_ax]}"
    else:
        fe_phase_pv = f"{frontend}{fe_system_phase['sI']}"
        fe_phase_pvQ = f"{frontend}{fe_system_phase['sQ']}"

    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_ax
    data["base_name"] = f"system_phase_scan_{mbf_ax}_axis"
    data["orig_gain"] = get_variable(f"{mbf_pv}{sequencer1['gaindb']}")
    data["original_setting"] = get_variable(fe_phase_pv)
    if mbf_ax.lower() == "s":
        data["original_settingQ"] = get_variable(fe_phase_pvQ)
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed

    # set up the sweep
    data["phase"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["phase"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"] - data["sweep_step"],
        )
    )
    # prealloacation
    data["side1"] = []
    data["main"] = []
    data["side2"] = []
    data["adc_phase"] = []
    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")

    original_detector_setup = BBBFE_detector_setup(mbf_ax, single_bunch_location)
    # moving to starting point in scan
    for pp in range(data["original_setting"], sweep_start, -sweep_step):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if mbf_ax.lower() == "s":
        # I and Q must be in quadrature
        for pp in range(data["original_settingQ"], sweep_start, -sweep_step) + 90:
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    # measurement
    for x in range(len(data["phase"])):
        set_variable(fe_phase_pv, data["phase"][x])
        if mbf_ax.lower() == "s":
            set_variable(fe_phase_pvQ, data["phase"][x] + 90)

        time.sleep(sweep_speed)
        data["side1"][x] = max(get_variable(f"{mbf_pv}{detector['det1']['power']}"))
        data["main"][x] = max(get_variable(f"{mbf_pv}{detector['det2']['power']}"))
        data["side2"][x] = max(get_variable(f"{mbf_pv}{detector['det3']['power']}"))
        if mbf_ax.lower() == "s":
            data["adc_phase"][x] = max(get_variable(f"{mbf_pv}{adc['phase']['mean']}"))
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['min']}"))
            data["adc_meanQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['mean']}"))
            data["adc_maxQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['max']}"))
            data["adc_minQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['min']}"))
        else:
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv}{adc['min']}"))

    # move back to the original setting
    for pp in range(data["sweep_start"], data["original_setting"], data["sweep_step"]):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if mbf_ax.lower() == "s":
        # move back to the original setting
        for pp in range(
            data["sweep_start"] + 90, data["original_settingQ"], data["sweep_step"]
        ):
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")
        set_variable(f"{mbf_pv}{sequencer1['gaindb']}", data["orig_gain"])

    BBBFE_detector_restore(mbf_ax, original_detector_setup)
    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## Plotting data
    if plotting == "yes":
        # for archival investigations this allows filtering by machine state.
        # but for capture this is not needed so it set to empty.
        filter_conditions: list = []
        mbf_frontend_system_phase_scan_archival_retrieval(
            mbf_ax, [data["time"], data["time"]], filter_conditions
        )


def DORIS_target_phase_scan(
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 5,
    sweep_end: int = 180,
):
    # Scans the phase of the DORIS unit upstream of the MBF frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #      single_bunch_location (int): the location of the single bunch.
    #
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): phase value in degrees to start the sweep.
    #       sweep_step(int):  phase scan step in degrees.
    #       sweep_end(int):   phase value in degreees to stop the sweep.
    #
    # Machine setup: (manual for the time being.)
    # fill some charge in bunch 1 (0.2nC)
    #
    # Example: DORIS_target_phase_scan(400)
    [root_string, _1, pv_names] = mbf_system_config()
    detector = pv_names["tails"]["Detector"]
    doris_pv = pv_names["doris"]["phase"]
    mbf_pv_x = pv_names["hardware_names"]["x"]
    mbf_pv_y = pv_names["hardware_names"]["y"]
    mbf_pv_s = pv_names["hardware_names"]["s"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]

    # getting general environment data['']
    data = machine_environment()
    # Add the extra data to the data structure['']
    data["base_name"] = "doris_phase_scan"
    data["original_setting"] = get_variable(doris_pv)
    data["orig_gain_x"] = get_variable(f"{mbf_pv_x}{sequencer1['gaindb']}")
    data["orig_gain_y"] = get_variable(f"{mbf_pv_y}{sequencer1['gaindb']}")
    data["orig_gain_s"] = get_variable(f"{mbf_pv_s}{sequencer1['gaindb']}")
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end

    # set up the sweep
    data["phase"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["phase"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"],
            -data["sweep_step"],
        )
    )
    # prealloacation
    data["side1_x"] = []
    data["main_x"] = []
    data["side2_x"] = []
    data["side1_y"] = []
    data["main_y"] = []
    data["side2_y"] = []
    if auto_setup == "yes":
        setup_operational_mode("x", "TuneOnly")
        setup_operational_mode("y", "TuneOnly")
        setup_operational_mode("s", "TuneOnly")

    detector_setup_x = BBBFE_detector_setup("x", single_bunch_location)
    detector_setup_y = BBBFE_detector_setup("y", single_bunch_location)
    detector_setup_s = BBBFE_detector_setup("s", single_bunch_location)
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
    set_variable(doris_pv, data["original_setting"])
    if auto_setup == "yes":
        setup_operational_mode("x", "TuneOnly")
        set_variable(f"{mbf_pv_x}{sequencer1['gaindb']}", data["orig_gain_x"])
        setup_operational_mode("y", "TuneOnly")
        set_variable(f"{mbf_pv_y}{sequencer1['gaindb']}", data["orig_gain_y"])
        setup_operational_mode("s", "TuneOnly")
        set_variable(f"{mbf_pv_s}{sequencer1['gaindb']}", data["orig_gain_s"])

    BBBFE_detector_restore("x", detector_setup_x)
    BBBFE_detector_restore("y", detector_setup_y)
    BBBFE_detector_restore("s", detector_setup_s)
    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## plotting
    if plotting == "yes":
        DORIS_phase_scan_plotting(data)

    return data


def mbf_pll_phase_scan(mbf_axis: str, scan_range: int = 270, step: int = 1):
    #
    #       Args:
    #           mbf_axis(str): 'x' or 'y'
    #           scan_range(int): phase range in degree to search around the
    #                       current target phase default is 80 degrees
    #           step(int): step in degree, default is 5 degrees
    #       Returns:
    #          fll_phase_scan(struct): structure containing captured data from
    #                                  the MBF plus general operating
    #                                  conditions of the machine
    #
    # Example: fll_phase_scan = mbf_pll_peakfind('x')

    [root_path, _1, pv_names] = mbf_system_config()
    pll_phase_scan = machine_environment()
    pll_phase_scan["ax_label"] = mbf_axis
    pll_phase_scan["base_name"] = f"pll_phase_scan_{pll_phase_scan['ax_label']}_axis"
    name = pv_names["hardware_names"][mbf_axis]
    pll_tails = pv_names["tails"]["pll"]
    pll_phase_scan["scan_step"] = step
    pll_phase_scan["scan_range"] = scan_range
    pll_phase_scan["mbf_fll"]["target_bunches"] = get_variable(
        f"{name}{pll_tails['detector']['target_bunches']}"
    )
    pll_phase_scan["mbf_fll"]["gain"] = get_variable(
        f"{name}{pll_tails['nco']['gain']}"
    )
    pll_phase_scan["mbf_fll"]["target_phase"] = get_variable(
        f"{name}{pll_tails['target_phase']}"
    )
    pll_phase_scan["mbf_fll"]["KI"] = get_variable(f"{name}{pll_tails['i']}")
    pll_phase_scan["mbf_fll"]["KP"] = get_variable(f"{name}{pll_tails['p']}")
    start = get_variable(f"{name}{pll_tails['target_phase']}")
    pll_phase_scan["phase"] = range(start, start + scan_range, step)
    pll_phase_scan["phase"].extend(range(start + scan_range, start - scan_range, -step))
    pll_phase_scan["phase"].extend(range(start - scan_range, start + scan_range, step))
    pll_phase_scan["phase"].extend(range(start + scan_range, start, -step))
    pll_phase_scan["mag"] = []
    pll_phase_scan["iq"] = []
    pll_phase_scan["f"] = []
    for n in range(len(pll_phase_scan["phase"])):
        status = get_variable(f"{name}{pll_tails['status']}")
        if status == "Running":
            # the funny mod is required to get into the right range of -180 to +179
            set_variable(
                f"{name}{pll_tails['target_phase']}",
                np.mod(pll_phase_scan["phase"][n] + 180, 360) - 180,
            )
            # This will depend on the dwell time and PLL config,
            # but works with the default
            time.sleep(2)
            # get magnitude
            pll_phase_scan["mag"][n] = get_variable(
                f"{name}{pll_tails['readback']['magnitude']}"
            )
            # get phase readback
            pll_phase_scan["phase"][n] = get_variable(
                f"{name}{pll_tails['readback']['phase']}"
            )
            pll_phase_scan["iq"][n] = [1, np.i] * get_variable(
                f"{name}{pll_tails['readback']['i']}{name}{pll_tails['readback']['q']}"
            )
            pll_phase_scan["f"][n] = get_variable(
                f"{name}{pll_tails['nco']['frequency']}"
            )
        else:
            set_variable(f"{name}{pll_tails['target_phase']}", start)
            break

    save_to_archive(root_path[1], pll_phase_scan)
    print(f"Data saved to {root_path[1]}{pll_phase_scan['base_name']}")
    fll_phase_scan_plotting(pll_phase_scan)
    if not status == "Running":
        raise ValueError(
            "PLL:stoppedUnexpectedly"
            "PLL stopped during phase sweep, please restart using fll_start"
        )
    return pll_phase_scan


def pll_PI_scan(
    mbf_axis: str,
    p_vals: list[int],
    i_vals: list[int],
    save_to_archive: str = "yes",
    additional_save_location: str | None = None,
    guardbunches: int = 10,
    pll_monitor_bunches: int = 400,
):
    # This sets up the PLL loop for different P and I settings, then records various
    # statistics in order to assess which setting are most suitable['']

    [root_string, _1, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][mbf_axis]
    pll_tails = pv_names["tails"]["pll"]
    # getting general environment data['']
    pll_data = machine_environment()
    # Add the axis label to the data structure['']
    pll_data["ax_label"] = mbf_axis
    pll_data["base_name"] = ["PLL_", pll_data["ax_label"], "_PI_scan"]
    n_p = len(p_vals)
    n_i = len(i_vals)
    n_repeats = 20
    pll_data["minwf"] = np.array(ndmin=3)
    pll_data["maxwf"] = np.array(ndmin=3)
    pll_data["meanwf"] = np.array(ndmin=3)
    pll_data["stdwf"] = np.array(ndmin=3)
    pll_data["tunewf"] = np.array(ndmin=3)
    pll_data["offsetwf"] = np.array(ndmin=3)
    pll_data["i_values"] = np.array(ndmin=3)
    pll_data["p_values"] = np.array(ndmin=3)
    pll_data["dwell"] = get_variable(f"{pv_head}{pll_tails['detector']['dwell']}")
    for ser in range(n_p):
        for jfe in range(n_i):
            # initialise loop
            set_variable(f"{pv_head}{pll_tails['i']}", i_vals[jfe])
            set_variable(f"{pv_head}{pll_tails['p']}", p_vals[ser])
            mbf_pll_start(
                mbf_axis, pllbunches=pll_monitor_bunches, guardbunches=guardbunches
            )
            for ewn in range(n_repeats):
                time.sleep(1)
                data = get_variable(
                    f"{pv_head}{pll_tails['nco']['offset_waveform']}"
                    f"P{pv_head}{pll_tails['nco']['mean_offset']}"
                    f"{pv_head}{pll_tails['nco']['std_offset']}"
                    f"{pv_head}{pll_tails['nco']['tune']}"
                    f"{pv_head}{pll_tails['nco']['offset']}"
                )
                wf = data[1, :]
                pll_data["minwf"][ser, jfe, ewn] = min(wf)
                pll_data["maxwf"][ser, jfe, ewn] = max(wf)
                pll_data["meanwf"][ser, jfe, ewn] = data[1, 0]
                pll_data["stdwf"][ser, jfe, ewn] = data[2, 0]
                pll_data["tunewf"][ser, jfe, ewn] = data[3, 0]
                pll_data["offsetwf"][ser, jfe, ewn] = data[4, 0]
                pll_data["i_values"][ser, jfe, ewn] = i_vals[jfe]
                pll_data["p_values"][ser, jfe, ewn] = p_vals[ser]

    ## saving the data to a file
    if mbf_axis == "x" or mbf_axis == "y" or mbf_axis == "s":
        #     only save if not on test system
        if save_to_archive == "yes":
            save_to_archive(root_string, pll_data)

        if additional_save_location:
            scipy.savemat(additional_save_location, "pll_data")

    return pll_data


def tunescan_over_modes_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_captures: int = 1001,
    start_mode: int = 0,
    drive_bunches: list[int] = range(harmonic_number),
    feedback_state: str = "on",
    start_frequency: float = 0,
    end_frequency: float = 0.5,
):
    # top level def to run the tunescan for all modes in the selected plane['']:
    # for archival investigations this allows filtering by machine state['']
    # but for capture this is not needed so it set to empty['']
    filter_conditions: list = []
    [root_string, harmonic_number, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][mbf_axis]
    if auto_setup == "yes":
        # Programatically press the tune only button on each system
        setup_operational_mode(mbf_axis, "TuneOnly")

    # getting general environment data
    tunescan = machine_environment()
    # Add the extra data to the data structure.
    tunescan["ax_label"] = mbf_axis
    tunescan["base_name"] = f"tunescan_{tunescan['ax_label']}_axis"
    tunescan["harmonic_number"] = harmonic_number
    tunescan["auto_setup"] = auto_setup
    tunescan["plotting"] = plotting
    tunescan["additional_save_location"] = additional_save_location
    tunescan["n_captures"] = n_captures
    tunescan["start_mode"] = start_mode
    tunescan["drive_bunches"] = drive_bunches
    tunescan["feedback_state"] = feedback_state
    tunescan["start_frequency"] = start_frequency
    tunescan["end_frequency"] = end_frequency

    mbf_tunescan_over_modes_setup(tunescan)
    time.sleep(2)
    captured_data = mbf_tunescan_over_modes_capture(mbf_axis, pv_names)
    # adding to output data structure.
    data_fields = captured_data.keys()
    for je in range(len(data_fields)):
        tunescan[data_fields[je]] = captured_data[data_fields[je]]

    # reset the sweep
    ####Is this section needed or does the TuneOnly script take care of things?
    configure_tune_sweep(mbf_axis, range(harmonic_number), 1, 1, 0, 0, 0)
    set_variable(f"{pv_head}{pv_names['tails']['triggers']['mode']}", "Rearm")
    set_variable(f"{pv_head}{pv_names['tails']['Sequencer']['reset']}", 1)
    #######
    if auto_setup == "yes":
        # Programatically press the tune only button on each system
        setup_operational_mode(mbf_axis, "TuneOnly")

    ## saving the data to a file
    save_to_archive(root_string, tunescan)
    if additional_save_location:
        scipy.savemat(additional_save_location, tunescan)

    if plotting == "yes":
        mbf_tunescan_over_modes_archival_retrieval(
            mbf_axis, [tunescan["time"], tunescan["time"]], filter_conditions
        )
