import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy

from Common import (
    get_operational_mode,
    get_variable,
    machine_environment,
    mbf_analysis_reorganise_for_parameter_sweep,
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
    mbf_archival_plotting_setup,
    mbf_system_config,
    mode_to_frequency,
    populate_archive_graph,
    reestablish_tune_measurement,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def mbf_modescan_analysis(modescan):
    # Analyses the captured modescan data.
    #     Args:
    #         modescan (structure): captured data
    #     Returns:
    #         data_magnitude (vector of floats): averaged signal magnitude over modes.
    #         data_phase (vector of floats): averaged signal phase over modes.
    #
    # Example [data_magnitude, data_phase] = mbf_modescan_analysis(modescan)
    n_repeats = len(modescan["magnitude"])
    data_magnitude_accumulator = np.empty((modescan["harmonic_number"], n_repeats))
    data_phase_accumulator = np.empty((modescan["harmonic_number"], n_repeats))
    for ks in range(n_repeats):
        data_magnitude_accumulator[:, ks] = abs(
            modescan["magnitude"][ks][1, 1 : modescan["harmonic_number"]]
        )
        data_phase_accumulator[:, ks] = modescan["phase"][ks][
            1, 1 : modescan["harmonic_number"]
        ]

    data_magnitude = sum(data_magnitude_accumulator, 2) / n_repeats
    data_phase = sum(data_phase_accumulator, 2) / n_repeats
    data_phase = np.unwrap(data_phase / 180 * np.pi) / np.pi * 180
    data_phase = data_phase - data_phase[1]
    return data_magnitude, data_phase


def mbf_modescan_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets. Then plots the results.
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed.
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides.
    #
    # Returns:
    #         data_magnitude (numeric matrix):
    #         data_phase (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_growdamp_archival_analysis(
    #                                               data_requested, 'average')
    times = []
    param = []
    data_magnitude = []
    data_phase = []

    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        data_magnitude[nd], data_phase[nd] = mbf_modescan_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        [data_magnitude, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                data_magnitude, param, parameter_step
            )
        )
        [data_phase, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                data_phase, param, parameter_step
            )
        )
    elif analysis_type == "average":
        print(
            "Archive:Modescan:setting",
            'Ignoring the last two parameters as "average" is set',
        )
        data_magnitude = np.mean(data_magnitude, 0)
        data_phase = np.mean(data_phase, 0)


def mbf_modescan_archival_plotting(
    requested_data, data_magnitude, data_phase, times, experimental_setup
):
    # Plots the data processed by mbf_growdamp_archival_analysis['']
    # Args:
    #      data_magnitude (numeric matrix):
    #      data_phase (numeric matrix):
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude,
    #                                data_phase, times, setup, selections, extents)
    # Only do something if there is data to do something with['']
    if not times:
        return

    graph_title = "Modescan"
    fig = mbf_archival_plotting_setup(requested_data, times, experimental_setup)
    harmonic_number = requested_data[1]["harmonic_number"]
    x_plt_axis = range(harmonic_number)
    this_year = datetime.datetime.now().year
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = f"Modescan as a def of {experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(1, len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    # FIXME

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, data_magnitude)
        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            data_magnitude, years_input, years_colours, times, x_plt_axis
        )

    fig.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Magnitude")
    ymin = min(min(data_magnitude, [], 2))
    ymin = min(ymin, 0)

    ymax = max(max(data_magnitude, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    plt.xlim([x_plt_axis[1], x_plt_axis[-1]])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, data_phase)
        plt.legend(graph_labels)
    else:
        populate_archive_graph(data_phase, years_input, times, x_plt_axis)

    plt.plot(
        x_plt_axis,
        np.ones(len(x_plt_axis)) * 90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        x_plt_axis,
        np.ones(len(x_plt_axis)) * -90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    fig.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Phase")
    ymin = min([min(min(data_phase, [], 2)), -90])
    ymax = max([max(max(data_phase, [], 2)), 90])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    plt.xlim([x_plt_axis[1], x_plt_axis[-1]])


def mbf_modescan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax).
    # also filters out datasets with machine settings outside the specified
    # acceptable range.
    #
    # Args:
    #       ax (str): The number of the axis (x, y, s)
    #       date_range (pair of datetime instances): The range of time to extract.
    #       bypass_index (str) : 'no' for use the pregnerated index (much faster)
    #                            'yes' for work things out from the file metatdata.
    #                            the default is 'no'.
    #       metadata_only(str): 'no' return all data
    #                            'yes' remove the sample data from the output structure.
    #                            the default is 'no'.
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #          [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"Modescan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        [data_magnitude, data_phase, _2, _1] = mbf_modescan_archival_analysis(
            requested_data, analysis_type="collate"
        )
        mbf_modescan_plotting(data_magnitude, data_phase, requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [data_magnitude, data_phase, times, setup] = (
                    mbf_modescan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [data_magnitude, data_phase, times, setup] = (
                    mbf_modescan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )
            else:
                raise ValueError(
                    "modescanArchivalRetrieval:InputError. "
                    "Please select collate or sweep as the analysis type",
                )

            setup["axis"] = ax
            mbf_modescan_archival_plotting(
                conditioned_data, data_magnitude, data_phase, times, setup
            )

    return data_magnitude, data_phase, times, setup


def mbf_modescan_capture(input_settings, pv_names):
    # wrapper def to call modescan, gather data on the environment:
    # and to save the resultant data['']
    #
    #   Args:
    #       mbf_axis (str): Selects which MBF axis to work on (x, y, s)['']
    #       n_repeats (int): The number of repeat datapoints to capture
    #   Returns:
    #       modescan (struct): data structure containing the experimental
    #                          results and the machine conditions['']
    #                          [optional output]
    #
    # example data = mbf_modescan_capture('x', 100)
    modescan = {}
    pv_head = pv_names["hardware_names"][input_settings["mbf_axis"]]
    for hs in range(input_settings["n_repeats"]):
        modescan["magnitude"][hs] = get_variable[[pv_head, ":TUNE:DMAGNITUDE"]]
        modescan["phase"][hs] = get_variable[[pv_head, ":TUNE:DPHASE"]]

    return modescan


def mbf_modescan_config(mbf_axis):
    # Contains the axis specific settings desired for the modescan experiment['']
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are
    #                       requesting
    #
    # Example: settings = mbf_modescan_config('x')
    settings = {}
    if mbf_axis == "x":
        settings["axis_label"] = "x"
        settings["axis_number"] = 1
        settings["ex_level"] = -18  # excitation level in dB['']
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB['']
        settings["seq_gain"] = -42  # sequencer gain in dB['']
    elif mbf_axis == "y":
        settings["axis_label"] = "y"
        settings["axis_number"] = 2
        settings["ex_level"] = -18  # excitation level in dB['']
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB['']
        settings["seq_gain"] = -42  # sequencer gain in dB['']
    elif mbf_axis == "s":
        settings["axis_label"] = "s"
        settings["axis_number"] = 3
        settings["ex_level"] = -18  # excitation level in dB['']
        settings["dwell"] = 200
        settings["det_gain"] = -24  # detector gain in dB['']
        settings["seq_gain"] = -42  # sequencer gain in dB['']


def mbf_modescan_plotting(data_magnitude, data_phase, modescan):
    # Plots the effectiveness of correction across all modes['']
    #
    # Args:
    #       data_magnitude(vector of floats): averaged signal magnitude over modes['']
    #       data_phase(vector of floats): averaged signal phase over modes['']
    #       modescan(structure): captured data
    #
    # Example: mbf_modescan_plotting(data_magnitude, data_phase, modescan)

    # FIXME
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    fig.suptitle(
        f"MBF modescan results {modescan['ax_label']} axis "
        f"{modescan['time'].strftime('%d_%m_%y-%H-%M-%S')}"
        f"Current: {(round(modescan['current']))} mA",
    )
    plt.plot(data_magnitude[1 : modescan["harmonic_number"]])
    plt.xlim([1, modescan["harmonic_number"]])
    fig.title("Amplitude")
    plt.xlabel("Modes")

    plt.plot(data_phase(), "DisplayName", "data", "LineWidth", 2)

    plt.plot(
        range(modescan["harmonic_number"]),
        np.ones(modescan["harmonic_number"]) * -90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        range(modescan["harmonic_number"]),
        np.ones(modescan["harmonic_number"]) * 90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    plt.title("Phase (deg)")
    plt.xlim([1, modescan["harmonic_number"]])
    plt.legend("Location", "northoutside")
    plt.xlabel("Modes")
    [_1, data_mag] = mode_to_frequency(
        modescan["RF"],
        modescan["harmonic_number"],
        modescan["tunes"][""]([modescan["ax_label"], "_tune"])["tune"],
        data_magnitude,
    )
    [x_data, data_phse] = mode_to_frequency(
        modescan["RF"],
        modescan["harmonic_number"],
        modescan["tunes"][""]([modescan["ax_label"], "_tune"])["tune"],
        data_phase,
    )

    plt.plot(x_data * 1e-6, data_mag)
    plt.xlim([0, max(x_data * 1e-6)])
    plt.title("Amplitude")
    plt.xlabel("Frequency (MHz)")

    plt.plot(x_data * 1e-6, data_phse, "DisplayName", "data", "LineWidth", 2)
    # take the mean of an even number of points to make things more robust['']
    grad_start = np.mean(data_phse[1:4])
    grad_end = np.mean(data_phse[-5:-1])
    target_grad = (grad_end - grad_start) / x_data[-1]
    phase_offset = x_data * target_grad
    phase_angle = np.round(phase_offset[-1] * 10) / 10
    delay_time = np.round(phase_offset[-1] / (360 * x_data[-1]) * 1e12)
    velocity_factor = 0.7
    adjustment_length = round(delay_time * 1e-12 * velocity_factor * 3e8 * 1e3)
    plt.plot(
        phase_offset + grad_start,
        "DisplayName",
        [
            "fit ",
            (phase_angle),
            " degrees total, delay = ",
            (delay_time),
            "ps, adjustment length approx ",
            (adjustment_length),
            "mm",
        ],
        "LineWidth",
        2,
    )
    plt.plot(
        x_data * 1e-6,
        np.ones(len(x_data)) * -90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        x_data * 1e-6,
        np.ones(len(x_data)) * 90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    plt.title("Phase (deg)")
    plt.xlim([1, max(x_data * 1e-6)])
    plt.legend("Location", "northoutside")
    plt.xlabel("Frequency (MHz)")


def mbf_modescan_setup(input_settings, pv_names):
    # Sets up the MBF system to be ready for a modescan measurement['']
    #
    #   Args:
    #       input_settings(struct): contains all the setup information['']
    #       pv_names(struct): contains the locations of all the machine parameters['']
    #
    # example: mbf_modescan_setup(input_settings, pv_names)
    mbf_tools()
    # Generate the base PV name['']
    system_axis = pv_names["hardware_names"][input_settings["mbf_axis"]]
    # state 1 of sequencer
    seq = pv_names["tails"]["Sequencer"]["seq1"]
    set_variable(
        f"{system_axis}{seq['start_frequency']}", input_settings["excitation_tune"]
    )
    set_variable(f"{system_axis}{seq['step_frequency']}", 1)
    set_variable(f"{system_axis}{seq['turns']}", input_settings["harmonic_number"] - 1)
    set_variable(f"{system_axis}{seq['holdoff']}", 0)
    set_variable(f"{system_axis}{seq['dwell']}", input_settings["dwell"])
    set_variable(f"{system_axis}{seq['bank_select']}", "Bank 1")
    set_variable(f"{system_axis}{seq['capture_state']}", "Capture")
    set_variable(f"{system_axis}{seq['windowing_state']}", "Disabled")
    set_variable(f"{system_axis}{seq['gaindb']}", input_settings["excitation_gain"])
    set_variable(f"{system_axis}{seq['blanking_state']}", "Off")


def modescan_all(
    mbf_axis,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    n_repeats=10,
    dwell=500,
    excitation_gain=-30,
):
    # Top level def to run the modescan for all selected plane.:
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       n_repeats(int): How many times to repeat each measurement point.
    #       dwell (int): How many turns to stay at each measurement point.
    #       excitation_gain(float): level of the excitation.
    #
    # Example  modescan_all('x')
    [root_string, harmonic_number, pv_names] = mbf_system_config
    pv_head = pv_names["hardware_names"][mbf_axis]
    # for archival investigations this allows filtering by machine state.
    # but for capture this is not needed so it set to empty.
    filter_conditions = []
    # getting general environment data
    modescan = machine_environment
    # Add the extra data to the data structure.
    modescan["ax_label"] = mbf_axis
    modescan["base_name"] = f"Modescan_{mbf_axis}_axis"
    modescan["harmonic_number"] = harmonic_number
    modescan["excitation_tune"] = modescan["tunes"][""](f"{mbf_axis}_tune")["tune"]
    temp = get_variable(f"{pv_head}:FIR:GAIN_S")
    modescan["fir_gain"] = temp[1]
    modescan["auto_setup"] = auto_setup
    modescan["plotting"] = plotting
    modescan["additional_save_location"] = additional_save_location
    modescan["n_repeats"] = n_repeats
    modescan["dwell"] = dwell
    modescan["excitation_gain"] = excitation_gain

    if auto_setup == "yes":
        # Programatically press the tune only button on each system['']
        setup_operational_mode(mbf_axis, "TuneOnly")

    modescan["mbf_state"] = get_operational_mode(mbf_axis)
    # Setup the MBF ready for the measurement['']
    mbf_modescan_setup(modescan, pv_names)
    time.sleep(2)
    # Capturing data['']
    captured_data = mbf_modescan_capture(modescan, pv_names)
    # adding to output data structure['']
    data_fields = captured_data.keys()
    for je in range(1, len(data_fields)):
        modescan[data_fields[je]] = captured_data[data_fields[je]]

    if auto_setup == "yes":
        setup_operational_mode(mbf_axis, "Feedback")
        # Setting the FIR gain to its original value['']
        set_variable(f"{pv_head}:FIR:GAIN_S", modescan["fir_gain"])
    else:
        reestablish_tune_measurement(mbf_axis)

    ## saving the data to a file
    save_to_archive(root_string, modescan)
    if additional_save_location:
        scipy.savemat(additional_save_location, modescan)

    ## Plotting data
    if plotting == "yes":
        mbf_modescan_archival_retrieval(
            mbf_axis, [modescan["time"], modescan["time"]], filter_conditions
        )
