import datetime
import time

import numpy as np
import scipy
from data_retrival import (
    bunch_motion_retrival,
    clock_phase_scan_retrival,
    doris_target_phase_scan_retrival,
    frontend_gain_scan_retrival,
    frontend_system_phase_scan_retrival,
    growdamp_archival_retrieval,
    modescan_archival_retrieval,
    pll_phase_scan_retrival,
    spectra_archival_retrieval,
    tunescan_over_modes_retrival,
)
from hardware_setup import (
    bbbfe_system_phase_scan_restore,
    bbbfe_system_phase_scan_setup,
    bunch_motion_restore,
    clock_phase_scan_restore,
    clock_phase_scan_setup,
    doris_target_phase_scan_restore,
    doris_target_phase_scan_setup,
    mbf_bunch_motion_setup,
    mbf_growdamp_setup,
    mbf_modescan_setup,
    mbf_spectrum_setup,
    mbf_tunescan_over_modes_setup,
    tunescan_over_modes_restore,
)
from measurements import (
    bbbfe_gain_scan_capture,
    bbbfe_system_phase_scan_capture,
    clock_phase_scan_capture,
    doris_target_phase_scan_capture,
    mbf_bunch_motion_capture,
    mbf_growdamp_capture,
    mbf_modescan_capture,
    mbf_pll_phase_scan_capture,
    mbf_spectrum_capture,
    mbf_tunescan_over_modes_capture,
    run_multi_axis_measurement,
    run_single_axis_measurement,
)

from Common import machine_environment


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
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       excitation_setting(str): sets whether the measurement uses an excitation to
    #                                drive a resonance or if the measurement just uses
    #                                the natural beam coupling.
    #                                Defaults to 'yes'
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
        retrival_function=growdamp_archival_retrieval,
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
        retrival_function=modescan_archival_retrieval,
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
        retrival_function=spectra_archival_retrieval,
    )


def Bunch_motion_all(
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
):
    # getting general environment data
    data = machine_environment()
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location

    run_multi_axis_measurement(
        setup_info=data,
        hardware_setup_function=mbf_bunch_motion_setup,
        capture_function=mbf_bunch_motion_capture,
        restore_function=bunch_motion_restore,
        retrival_function=bunch_motion_retrival,
    )


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

    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_ax
    data["base_name"] = ["frontend_gain_scan_", mbf_ax, "_axis"]
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=None,
        capture_function=bbbfe_gain_scan_capture,
        restore_function=None,
        retrival_function=frontend_gain_scan_retrival,
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

    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_ax
    data["base_name"] = f"system_phase_scan_{mbf_ax}_axis"
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=bbbfe_system_phase_scan_setup,
        capture_function=bbbfe_system_phase_scan_capture,
        restore_function=bbbfe_system_phase_scan_restore,
        retrival_function=frontend_system_phase_scan_retrival,
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

    # getting general environment data['']
    data = machine_environment()
    # Add the extra data to the data structure['']
    data["base_name"] = "doris_phase_scan"

    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end

    run_multi_axis_measurement(
        setup_info=data,
        hardware_setup_function=doris_target_phase_scan_setup,
        capture_function=doris_target_phase_scan_capture,
        restore_function=doris_target_phase_scan_restore,
        retrival_function=doris_target_phase_scan_retrival,
    )


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

    pll_phase_scan = machine_environment()
    pll_phase_scan["ax_label"] = mbf_axis
    pll_phase_scan["base_name"] = f"pll_phase_scan_{pll_phase_scan['ax_label']}_axis"
    pll_phase_scan["scan_step"] = step
    pll_phase_scan["scan_range"] = scan_range

    run_single_axis_measurement(
        setup_info=pll_phase_scan,
        hardware_setup_function=None,
        capture_function=mbf_pll_phase_scan_capture,
        restore_function=None,
        retrival_function=pll_phase_scan_retrival,
    )


def tunescan_over_modes_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_captures: int = 1001,
    start_mode: int = 0,
    drive_bunches: list[int] | str = "all",
    feedback_state: str = "on",
    start_frequency: float = 0,
    end_frequency: float = 0.5,
):
    # top level def to run the tunescan for all modes in the selected plane.

    # getting general environment data
    tunescan = machine_environment()
    # Add the extra data to the data structure.
    tunescan["ax_label"] = mbf_axis
    tunescan["base_name"] = f"tunescan_{tunescan['ax_label']}_axis"
    tunescan["auto_setup"] = auto_setup
    tunescan["plotting"] = plotting
    tunescan["additional_save_location"] = additional_save_location
    tunescan["n_captures"] = n_captures
    tunescan["start_mode"] = start_mode
    tunescan["drive_bunches"] = drive_bunches
    tunescan["feedback_state"] = feedback_state
    tunescan["start_frequency"] = start_frequency
    tunescan["end_frequency"] = end_frequency
    tunescan["start_state"] = "TuneOnly"
    tunescan["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=tunescan,
        hardware_setup_function=mbf_tunescan_over_modes_setup,
        capture_function=mbf_tunescan_over_modes_capture,
        restore_function=tunescan_over_modes_restore,
        retrival_function=tunescan_over_modes_retrival,
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
