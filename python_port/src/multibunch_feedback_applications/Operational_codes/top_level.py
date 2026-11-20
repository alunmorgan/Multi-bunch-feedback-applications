from analysis import (
    analysis_bunch_motion,
    analysis_doris_target_phase_scan,
    analysis_frontend_clock_phase_scan,
    analysis_frontend_gain_scan,
    analysis_frontend_lo_phase_scan,
    analysis_frontend_system_phase_scan,
    analysis_growdamp,
    analysis_modescan,
    analysis_pll_phase_scan,
    analysis_pll_pi_scan,
    analysis_spectrum,
    analysis_tunescan_over_modes,
)
from data_retrival import (
    archival_retrieval,
)
from hardware_setup import (
    restore_bbbfe_system_phase_scan,
    restore_bunch_motion,
    restore_doris_target_phase_scan,
    restore_frontend_clock_phase_scan,
    restore_pll_pi_scan,
    restore_tunescan_over_modes,
    setup_bbbfe_system_phase_scan,
    setup_bunch_motion,
    setup_doris_target_phase_scan,
    setup_frontend_clock_phase_scan,
    setup_growdamp,
    setup_modescan,
    setup_pll_pi_scan,
    setup_sequencer_stage,
    setup_spectrum,
    setup_tunescan_over_modes,
)
from measurements import (
    capture_bunch_motion,
    capture_doris_target_phase_scan,
    capture_frontend_clock_phase_scan,
    capture_frontend_gain_scan,
    capture_frontend_lo_phase_scan,
    capture_frontend_system_phase_scan,
    capture_growdamp,
    capture_modescan,
    capture_pll_phase_scan,
    capture_pll_pi_scan,
    capture_spectrum,
    capture_tunescan_over_modes,
    run_multi_axis_measurement,
    run_single_axis_measurement,
)
from plotting import (
    plotting_bunch_motion,
    plotting_doris_target_phase_scan,
    plotting_frontend_clock_phase_scan,
    plotting_frontend_gain_scan,
    plotting_frontend_lo_phase_scan,
    plotting_frontend_system_phase_scan,
    plotting_growdamp,
    plotting_modescan,
    plotting_pll_phase_scan,
    plotting_pll_pi_scan,
    plotting_spectrum,
    plotting_tunescan_over_modes,
)
from system_configuration import machine_environment


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
    """Top level def to run the growdamp measurements on the:
    # selected plane
    #   Args:
    #       mbf_axis: 'x','y', or 's'
    #       auto_setup: sets whether the setup scripts will be used to put the
    #                        system into a particular state.
    #       plotting: set whether the data is plotted as well as saved.
    #       additional_save_location: fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       excitation_setting: sets whether the measurement uses an excitation to
    #                                drive a resonance or if the measurement just uses
    #                                the natural beam coupling.
    #       excitation_location: The location of the excitation in tune space.
    #       excitation_manual: if excitation_location is set to 'manual' then
    #                                 this defines the location of the excitation
    #                                 in tune space.
    #       pll_tracking: Sets if the excitation frequency follows the tune
    #                           jitter.
    #       pll_bunches: bunches the pll is active on.
    #       pll_guard_bunches: the number of bunches surrounding the pll
    #                                  bunches for which feedback is switched off.
    #       bunch_monitor: This determines which bunches are monitored
    #                                 during the measurement. Defaults to 'all' which
    #                                 means all bunches.
    #       capture_full_bunch_motion: Captures the centroid motion for the
    #                                       duration of the measuremnt.
    #                                       Defaults to no as this is a lot of data.
    # Example: growdamp_all('x')
    """
    ## Constructing the different states for the sequencer. These will be arranged
    # in various configurations depending on the experiment requested.
    #
    # bank = 1 is Feedback off
    # bank = 2 is Feedback on
    #       tune_offset: Tune fraction to offset from the peak.
    #       dwell: number of turns at each point.
    #       duration: number of points for each stage.
    growth: dict = {}
    excitation: dict = {}
    passive: dict = {}
    active: dict = {}
    spacer: dict = {}
    tune_offset: float = 0
    if mbf_axis.lower() == "x" or mbf_axis.lower() == "y":
        # Passive Growth
        growth = setup_sequencer_stage(
            duration=2500,
            dwell=1,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=1,
        )
        # Excitation
        excitation = setup_sequencer_stage(
            duration=750,
            dwell=1,
            capture="Capture",
            excitation="On",
            excitation_level="-18dB",
            bank=1,
        )
        # Passive decay (assuming no instability)
        passive = setup_sequencer_stage(
            duration=1500,
            dwell=1,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=1,
        )
        # Feedback active
        active = setup_sequencer_stage(
            duration=1500,
            dwell=1,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=2,
        )
        # Feedback active but no capture
        spacer = setup_sequencer_stage(
            duration=4000,
            dwell=1,
            capture="Discard",
            excitation="Off",
            excitation_level="-48dB",
            bank=2,
        )
    elif mbf_axis.lower() == "s":
        # Passive Growth
        growth = setup_sequencer_stage(
            duration=10,
            dwell=480,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=1,
        )
        # Excitation
        excitation = setup_sequencer_stage(
            duration=10,
            dwell=480,
            capture="Capture",
            excitation="On",
            excitation_level="-18dB",
            bank=1,
        )
        # Passive decay (assuming no instability)
        passive = setup_sequencer_stage(
            duration=10,
            dwell=480,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=1,
        )
        # Feedback active
        active = setup_sequencer_stage(
            duration=50,
            dwell=480,
            capture="Capture",
            excitation="Off",
            excitation_level="-48dB",
            bank=2,
        )
        # Feedback active but no capture
        spacer = setup_sequencer_stage(
            duration=100,
            dwell=480,
            capture="Discard",
            excitation="Off",
            excitation_level="-48dB",
            bank=2,
        )

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

    # getting general environment data.
    data = machine_environment()

    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = ["Growdamp_", mbf_axis, "_axis"]
    data["states"] = states
    data["state_names"] = state_names
    data["mbf_axis"] = mbf_axis
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["excitation_setting"] = excitation_setting
    data["excitation_location"] = excitation_location
    data["excitation_manual"] = excitation_manual
    data["pll_tracking="] = pll_tracking
    data["pll_bunches"] = pll_bunches
    data["pll_guard_bunches"] = pll_guard_bunches
    data["bunches_monitored"] = bunches_monitored
    data["capture_full_bunch_motion"] = capture_full_bunch_motion
    data["start_state"] = "Feedback"
    data["end_state"] = "Feedback"
    if "lower_sideband" in excitation_location:
        data["excitation_tune"] = (
            data["tunes"][f"{mbf_axis}_tune"]["lower_sideband"] + tune_offset
        )
    elif "upper_sideband" in excitation_location:
        data["excitation_tune"] = (
            data["tunes"][f"{mbf_axis}_tune"]["upper_sideband"] + tune_offset
        )
    elif "manual" in excitation_location:
        data["excitation_tune"] = excitation_manual
    else:
        data["excitation_tune"] = (
            data["tunes"][f"{mbf_axis}_tune"]["tune"] + tune_offset
        )

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=setup_growdamp,
        capture_function=capture_growdamp,
        restore_function=None,
    )

    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "Growdamp",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        analysed_data = analysis_growdamp(requested_data[0])
        plotting_growdamp(analysed_data, requested_data[0])


def modescan_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_repeats: int = 10,
    dwell: int = 500,
    excitation_gain: float = -30,
):
    """Top level def to run the modescan for all selected plane.:
    Args:
          mbf_axis: 'x', 'y', 's'. Defines which system you are requesting
          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting: set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          n_repeats: How many times to repeat each measurement point.
          dwell: How many turns to stay at each measurement point.
          excitation_gain: level of the excitation.

    Example  modescan_all('x')
    """
    # getting general environment data
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = f"Modescan_{mbf_axis}_axis"
    data["excitation_tune"] = data["tunes"][f"{mbf_axis}_tune"]["tune"]
    data["mbf_axis"] = mbf_axis
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["n_repeats"] = n_repeats
    data["dwell"] = dwell
    data["excitation_gain"] = excitation_gain
    data["start_state"] = "TuneOnly"
    data["end_state"] = "Feedback"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=setup_modescan,
        capture_function=capture_modescan,
        restore_function=None,
    )

    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "Modescan",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        analysed_data = analysis_modescan(requested_data[0])
        plotting_modescan(analysed_data, requested_data[0])


def mbf_spectrum_all(
    mbf_axis: str,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    n_turns: int = 1000,
    repeat: int = 1,
):
    """Top level def to run all spectral measurements on selected plane.:
    Args:
          mbf_axis: 'x', 'y', 's'. Defines which system you are requesting
          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting: set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          n_turns: number of turns to capture.
          repeat: Number of repeat points (improves the power resolution).

    Example mbf_spectrum_all
    """
    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = f"Spectrum_{mbf_axis}_axis"
    data["mbf_axis"] = mbf_axis
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["n_turns"] = n_turns
    data["repeat"] = repeat
    data["start_state"] = "TuneOnly"
    data["end_state"] = "Feedback"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=setup_spectrum,
        capture_function=capture_spectrum,
        restore_function=None,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "Spectrum",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        analysed_data = analysis_spectrum(requested_data[0])
        plotting_spectrum(analysed_data, requested_data[0])


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
        hardware_setup_function=setup_bunch_motion,
        capture_function=capture_bunch_motion,
        restore_function=restore_bunch_motion,
    )

    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "bunch_motion",
            ax=None,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        analysed_data = analysis_bunch_motion(requested_data[0])
        plotting_bunch_motion(analysed_data, requested_data[0])


def frontend_clock_phase_scan(
    mbf_ax: str,
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 10,
    sweep_end: int = 180,
):
    """Scans one of the clock phase shifts in the bunch by bunch frontend and
    records the strength of the tune signal.
    Restores the original value after the scan.

    Args:
         ax: Specifies which axis.
         single_bunch_location: the location of the single bunch.
          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting: set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          sweep_start: phase value in degrees to start the sweep.
          sweep_step:  phase scan step in degrees.
          sweep_end:   phase value in degreees to stop the sweep.

    Machine setup: (manual for the time being.)
    fill some charge in a single bunch (0.2nC)

    Example: BBBFE_clock_phase_scan('x', 400)
    """
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
        hardware_setup_function=setup_frontend_clock_phase_scan,
        capture_function=capture_frontend_clock_phase_scan,
        restore_function=restore_frontend_clock_phase_scan,
    )

    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "frontend_clock_phase_scan",
            ax=None,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        analysed_data = analysis_frontend_clock_phase_scan(requested_data[0])
        plotting_frontend_clock_phase_scan(analysed_data, requested_data[0])


def full_frontend_checkout(single_bunch_location: int):
    """BBBFE_FULL_FRONTEND_CHECKOUT
    This assumes that the machine is set up with a single bunch in the machine at
    the single_bunch_location."""
    frontend_system_phase_scan("x", single_bunch_location)
    frontend_system_phase_scan("y", single_bunch_location)
    frontend_system_phase_scan("s", single_bunch_location)
    frontend_clock_phase_scan("x", single_bunch_location)
    frontend_clock_phase_scan("y", single_bunch_location)
    frontend_clock_phase_scan("s", single_bunch_location)


def frontend_gain_scan(
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
    """Scans one of the individual axis gains in the
    bunch by bunch frontend and records the strength of the ADC signal.
    Restores the original value after the scan.

    Args:
          mbf_axis: 'x','y', or 's'
          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting: set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          sweep_start: level value to start the sweep.
          sweep_step:  level step.
          sweep_end:   level value to stop the sweep.

    Machine setup
    machine to nominal conditions

    Example: BBBFE_gain_scan('x')
    """
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
        capture_function=capture_frontend_gain_scan,
        restore_function=None,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "frontend_gain_scan",
            ax=None,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_frontend_gain_scan(requested_data[0])
        plotting_frontend_gain_scan(data_magnitude, data_phase, requested_data[0])


def frontend_system_phase_scan(
    mbf_axis: str,
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 10,
    sweep_end: int = 180,
    sweep_speed: int = 2,
):
    """Scans one of the individual axis system phase shifts in the
    bunch by bunch frontend and records the strength of the tune signal.
    Restores the original value after the scan.

    Args:
          mbf_axis: 'x','y', or 's'
          single_bunch_location: location of the target bunch.
          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting(str): set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          sweep_start: phase value in degrees to start the sweep.
          sweep_step:  phase scan step in degrees.
          sweep_end:   phase value in degreees to stop the sweep.

    Machine setup
    fill some charge in bunch 'single_bunch_location' (0.2nC)

    Example: BBBFE_system_phase_scan('x', 400)
    """
    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = f"system_phase_scan_{mbf_axis}_axis"
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
        hardware_setup_function=setup_bbbfe_system_phase_scan,
        capture_function=capture_frontend_system_phase_scan,
        restore_function=restore_bbbfe_system_phase_scan,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "frontend_system_phase_scan",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_frontend_system_phase_scan(
            requested_data[0]
        )
        plotting_frontend_system_phase_scan(
            data_magnitude, data_phase, requested_data[0]
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
    """Scans the phase of the DORIS unit upstream of the MBF frontend and
    records the strength of the tune signal.
    Restores the original value after the scan.

    Args:
         single_bunch_location: the location of the single bunch.

          auto_setup: sets whether the setup scripts will be used to put the
                           system into a particular state.
          plotting: set whether the data is plotted as well as saved.
          additional_save_location: fully defined filename to save the
                                         captured data to in addition to the
                                         main archive.
          sweep_start: phase value in degrees to start the sweep.
          sweep_step:  phase scan step in degrees.
          sweep_end:   phase value in degreees to stop the sweep.

    Machine setup: (manual for the time being.)
    fill some charge in bunch 1 (0.2nC)

    Example: DORIS_target_phase_scan(400)
    """
    # getting general environment data.
    data = machine_environment()
    # Add the extra data to the data structure.
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
        hardware_setup_function=setup_doris_target_phase_scan,
        capture_function=capture_doris_target_phase_scan,
        restore_function=restore_doris_target_phase_scan,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "doris_target_phase_scan",
            ax=None,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_doris_target_phase_scan(requested_data[0])
        plotting_doris_target_phase_scan(data_magnitude, data_phase, requested_data[0])


def mbf_pll_phase_scan(
    mbf_axis: str,
    scan_range: int = 270,
    step: int = 1,
    plotting: str = "yes",
) -> None:
    """
          Args:
              mbf_axis: 'x' or 'y'
              scan_range: phase range in degree to search around the
                          current target phase default is 80 degrees
              step: step in degree, default is 5 degrees

    Example: fll_phase_scan = mbf_pll_peakfind('x')
    """
    data = machine_environment()
    data["ax_label"] = mbf_axis
    data["base_name"] = f"pll_phase_scan_{data['ax_label']}_axis"
    data["scan_step"] = step
    data["scan_range"] = scan_range

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=None,
        capture_function=capture_pll_phase_scan,
        restore_function=None,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "pll_phase_scan",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_pll_phase_scan(requested_data[0])
        plotting_pll_phase_scan(data_magnitude, data_phase, requested_data[0])


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
    """top level def to run the tunescan for all modes in the selected plane."""

    # getting general environment data
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = f"tunescan_{data['ax_label']}_axis"
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["n_captures"] = n_captures
    data["start_mode"] = start_mode
    data["drive_bunches"] = drive_bunches
    data["feedback_state"] = feedback_state
    data["start_frequency"] = start_frequency
    data["end_frequency"] = end_frequency
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=setup_tunescan_over_modes,
        capture_function=capture_tunescan_over_modes,
        restore_function=restore_tunescan_over_modes,
    )

    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "tunescan_over_modes",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_tunescan_over_modes(requested_data[0])
        plotting_tunescan_over_modes(data_magnitude, data_phase, requested_data[0])


def BBBFE_LO_scan(
    single_bunch_location: int,
    auto_setup: str = "yes",
    plotting: str = "yes",
    additional_save_location: str | None = None,
    sweep_start: int = -180,
    sweep_step: int = 5,
    sweep_end: int = 180,
):
    """Scans the LO phase shift in the bunch by bunch frontend and
    records the strength of the tune signal.
    Restores the original value after the scan.

    Args:
        phase_centre: The phase value to center the sweep on.
        sweep_extent: The range to sweep. 45 would sweep 45 degrees
                            above and 45 degrees below the centre value.

    Example: BBBFE_LO_scan(90, 45)
    """
    # getting general environment data
    data = machine_environment()
    # Add the extra data to the data structure.
    data["base_name"] = "LO_scan"
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"
    data["phase_pv"] = "SR23C-DI-BBFE-01:PHA"

    run_multi_axis_measurement(
        setup_info=data,
        hardware_setup_function=None,
        capture_function=capture_frontend_lo_phase_scan,
        restore_function=None,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "frontend_lo_phase_scan",
            ax=None,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_frontend_lo_phase_scan(requested_data[0])
        plotting_frontend_lo_phase_scan(data_magnitude, data_phase, requested_data[0])


def pll_PI_scan(
    mbf_axis: str,
    p_vals: list[int],
    i_vals: list[int],
    auto_setup: str = "yes",
    save_to_archive: str = "yes",
    additional_save_location: str | None = None,
    plotting: str = "yes",
    guardbunches: int = 10,
    monitor_bunches: int = 400,
):
    """This sets up the PLL loop for different P and I settings, then records various
    # statistics in order to assess which setting are most suitable."""
    data = machine_environment()
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_axis
    data["base_name"] = "pll_pi_sweep"
    data["base_name"] = f"PLL_{data['ax_label']}_PI_scan"
    data["auto_setup"] = auto_setup
    data["additional_save_location"] = additional_save_location
    data["p_vals"] = p_vals
    data["i_vlas"] = i_vals
    data["guardbunches"] = guardbunches
    data["monitor_bunches"] = monitor_bunches
    data["start_state"] = "TuneOnly"
    data["end_state"] = "TuneOnly"

    run_single_axis_measurement(
        setup_info=data,
        hardware_setup_function=setup_pll_pi_scan,
        capture_function=capture_pll_pi_scan,
        restore_function=restore_pll_pi_scan,
    )
    ## Plotting data
    if plotting == "yes":
        # Retrieving from datastore to ensure data has been written.
        requested_data = archival_retrieval(
            "pll_pi_scan",
            ax=mbf_axis,
            date_range=[data["time"], data["time"]],
            filter_conditions=[],
            bypass_index="no",
            metadata_only="no",
        )
        data_magnitude, data_phase = analysis_pll_pi_scan(requested_data[0])
        plotting_pll_pi_scan(data_magnitude, data_phase, requested_data[0])
