import datetime

import matplotlib.pyplot as plt
import numpy as np
import scipy
from Growdamp import mbf_analysis_reorganise_for_parameter_sweep

from Common import (
    ax2dev,
    get_operational_mode,
    get_variable,
    hanning,
    machine_environment,
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
    mbf_archival_plotting_setup,
    mbf_read_mem,
    mbf_restore_all,
    mbf_system_config,
    padarray,
    populate_archive_graph,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def mbf_spectra_all_archival_retrieval(
    ax,
    date_range,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    current_range=(2, 150),
):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax).
    # also filters out datasets with machine settings outside the specified
    # acceptable range['']
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
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides.
    #
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures.
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #            [datetime(2023, 1, 1), datetime("now")])
    filter_name = "Spectrum_"
    requested_data = mbf_archival_dataset_retrieval(
        filter_name, date_range, bypass_index=bypass_index, metadata_only=metadata_only
    )
    # conditioned_data = mbf_archival_conditional_filtering(requested_data,
    # 'current_range', p['Results']['current_range'])
    conditioned_data = requested_data
    if not conditioned_data:
        print("No data meeting the requirements")
    else:
        if analysis_type == "collate":
            [spec_data, times, setup] = mbf_spectra_archival_analysis(
                conditioned_data, analysis_type="collate"
            )
        elif analysis_type == "sweep":
            [spec_data, times, setup] = mbf_spectra_archival_analysis(
                conditioned_data,
                analysis_type="parameter_sweep",
                sweep_parameter=sweep_parameter,
                parameter_step=parameter_step,
            )
        else:
            raise ValueError(
                "MBF:Archive:Spectra:InputError "
                "Please select collate or sweep as the analysis type"
            )

        setup["axis"] = ax
        mbf_spectra_archival_plotting(conditioned_data, spec_data, times, setup)

    return conditioned_data


def mbf_spectra_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets[''] Then plots the results['']
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed['']
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep['']
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged[''] (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    # Returns:
    #         data_magnitude (numeric matrix):
    #         data_phase (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets['']
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis['']
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_growdamp_archival_analysis(
    #                                               data_requested, 'average')
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    # for fnd = len(data_requested):-1:1
    #     nturns_all(fnd) = data_requested[fnd]['n_turns']
    # end #for
    # max_turns = max(nturns_all)
    param = []
    times = []
    spec_data = []
    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        spec_data[nd] = mbf_spectrum_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    # Forcing results to use 3 dimensions to allow accumulation and averaging over
    # experiments['']
    fnames = spec_data[0].keys()
    spec_data_temp = {}
    for sbd in range(len(fnames)):
        spec_data_temp[fnames[sbd]] = np.array(ndmin=3)
        for brs in range(1, len(data_requested)):
            data_size = spec_data[brs][fnames[sbd]].shape
            target_size = spec_data_temp[fnames[sbd]].shape
            spec_data_temp[fnames[sbd]] = padarray(
                spec_data_temp[fnames[sbd]],
                [0, data_size(1) - target_size(2), data_size(2) - target_size(3)],
                None,
                "post",
            )
            spec_data_temp[fnames[sbd]][
                brs, range(data_size[0]), range(data_size[1])
            ] = np.permute(spec_data[brs][fnames[sbd]], [3, 1, 2])

    spec_data = spec_data_temp
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        for sbd in range(1, len(fnames)):
            [spec_data[fnames[sbd]], experimental_setup["param"]] = (
                mbf_analysis_reorganise_for_parameter_sweep(
                    spec_data[fnames[sbd]], param, parameter_step
                )
            )

    elif analysis_type == "average":
        print(
            "Archive:Spectra:setting "
            "Ignoring the last two parameters as 'average' is set"
        )
        for sbd in range(len(fnames)):
            spec_data[fnames[sbd]] = np.mean((fnames[sbd]), 0)


def mbf_spectra_archival_plotting(requested_data, spec_data, times, experimental_setup):
    # Plots the data processed by mbf_growdamp_archival_analysis.
    # Args:
    #      data_magnitude (numeric matrix):
    #      data_phase (numeric matrix):
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results of
    #                                    the fit errors.
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude,
    #                                 data_phase, times, setup, selections, extents)
    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Spectra"
    mbf_archival_plotting_setup(requested_data, times, experimental_setup)
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
        graph_title = f"{experimental_setup['axis']} axis {graph_title} as a def of "
        f"{experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']}"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    if experimental_setup["anal_type"] == "parameter_sweep":
        scale_length = spec_data["bunch_tune_scale"].shape[1]
        for nfd in range(spec_data["bunch_tune_scale"].shape[0]):
            plot_data_tune = np.mean(spec_data["bunch_f_data"][nfd, :, :], 2)
            plt.plot(
                spec_data["bunch_tune_scale"][nfd, scale_length / 2 + 1 : -1],
                plot_data_tune[scale_length / 2 + 1 : -1],
            )

        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            spec_data["bunch_f"],
            years_input,
            years_colours,
            times,
            spec_data["bunch_tune_scale"][1, :, :],
        )

    plt.title(graph_title)
    plt.xlabel("Tune")
    plt.ylabel("Magnitude")

    if experimental_setup["anal_type"] == "parameter_sweep":
        for nfd in range(spec_data["bunch_f_scale"].shape[0]):
            plot_data_f = np.mean(spec_data["bunch_f_data"][nfd, :, :], 2)
            plt.plot(
                spec_data["bunch_f_scale"][nfd, scale_length / 2 + 1 : -1] * 1e-3,
                plot_data_f[scale_length / 2 + 1 : -1],
            )

        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            spec_data["bunch_f"],
            years_input,
            times,
            spec_data["bunch_f_scale"][1, :, :],
        )

    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Magnitude (Power)")

    bunches = spec_data["bunch_f_data"].shape[1]
    if experimental_setup["anal_type"] == "parameter_sweep":
        plot_data_2d = sum(spec_data["bunch_f_data"][:, :, :], 1)
        plt.imagesc(
            spec_data["bunch_f_scale"][1, scale_length / 2 + 1 : -1] * 1e-3,
            range(bunches),
            plot_data_2d[:, scale_length / 2 + 1 : -1],
        )  # TEMP FIXME
        plt.ylabel("Bunches")
        plt.xlabel("Frequency (kHz)")
    else:
        populate_archive_graph(
            spec_data["bunch_f_bunches"], years_input, times, x_plt_axis
        )
        plt.ylabel("Average position deviation from the mean")
        plt.xlabel("Bunch")

    plt.plt.figure("Position", [50, 50, 1400, 800])
    plt.title("Spectra of all measurements")
    plt.xlabel("Tune")
    for jw in range(spec_data["bunch_f_data"].shape[0]):
        plot_data = abs(spec_data["bunch_f_data"][jw, :, :])
        plt.imagesc(spec_data["bunch_tune_scale"][jw, :, :], x_plt_axis, plot_data)
        plt.colorbar
        plt.title(requested_data[jw]["time"].strftime("%a %d %b %Y, %I:%M%p"))


def mbf_spectra_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    current_range=(2, 300),
):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax).
    # also filters out datasets with machine settings outside the specified
    # acceptable range['']
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
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides.
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #             [datetime(2023, 1, 1), datetime("now")])
    selection_names = {"Spectrum_", ["Spectrum_", ax, "_axis"]}
    requested_data = []
    for jsw in range(1, len(selection_names)):
        temp_data = mbf_archival_dataset_retrieval(
            selection_names[jsw],
            date_range,
            bypass_index=bypass_index,
            metadata_only=metadata_only,
        )
        for issd in range(1, len(temp_data)):
            if type(temp_data[issd]["raw_data"]) is dict:
                temp_data[issd]["raw_data"] = temp_data[issd]["raw_data"][f"{ax}_data"]
                temp_data[issd]["base_name"] = [
                    temp_data[issd]["base_name"],
                    ax,
                    "_axis",
                ]

        requested_data = np.vertcat(requested_data, temp_data)

    # only one dataset then plot the single measurement graphs['']
    if len(requested_data) == 1:
        [spec_data, _2, _1] = mbf_spectra_archival_analysis(
            requested_data, "analysis_type", "collate"
        )
        mbf_spectrum_plotting(requested_data[1], spec_data)
        # Plot the trend graphs['']
    else:
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [spec_data, times, setup] = mbf_spectra_archival_analysis(
                    conditioned_data, analysis_type="collate"
                )
            elif analysis_type == "sweep":
                [spec_data, times, setup] = mbf_spectra_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                )
            else:
                raise ValueError(
                    "MBF:Archive:Spectra:InputError "
                    "Please select collate or sweep as the analysis type"
                )

            setup["axis"] = ax
            mbf_spectra_archival_plotting(conditioned_data, spec_data, times, setup)

    return spec_data, times, setup


def mbf_spectrum(mbf_axis, n_turns, fold=1, repeat=1):
    # generates an spectragram of all bunches['']
    #
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are
    #                       requesting
    #       n_turns (int): The number of turns to capture['']
    #       fold (int): The number of times to fold the data along the
    #                   frequency axis[''] This enhances power resolution
    #                   at the cost of frequency resolution['']
    #       repeat (int): Repeat the capture this many times in order to
    #                     improve the power resolution['']
    #
    # Example: mbf_spectrum('x',10000)
    ## Getting the desired system setup parameters['']
    [root_string, harmonic_number, pv_names, trigger_inputs] = mbf_system_config

    # Generate the base PV name['']
    pv_head = pv_names["hardware_names"][mbf_axis]
    if mbf_axis == "s":
        system_name = pv_names["hardware_names"]["L"]
    else:
        system_name = pv_names["hardware_names"]["T"]

    PVt = pv_names["tails"]
    # getting general environment data['']
    mbf_spec = machine_environment
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
        bunch_data = bunch_data ^ 2 + (xf1[:, 1 : -1 / 2]) ^ 2  # accumulating
    data = {}
    data["bunch_data"] = bunch_data
    data["bunch_bunches"] = np.sum(bunch_data[""] ^ 2, 1)
    data["bunch_tune"] = np.sum(bunch_data[""] ^ 2, 2)
    data["tune_data"] = np.fft.fftshift(mode_data, 2)
    data["mode_modes"] = np.sum(bunch_data[""] ^ 2, 1)
    data["mode_tune"] = np.sum(mode_data[1 : -1 / 2, :][""] ^ 2, 2)
    data["tune_axis"] = np.linspace(0, ["5"], len(data["bunch_tune"]))
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
    [_1, pi] = max(data["mode_tune"])
    ax3 = plt.subplot("position", [0.02, 0.11, 0.7, 0.24])
    plt.plot(data["bunch_data"][pi, :])
    plt.xlabel(f"Bunches at peak tune {data['tune_axis'][pi]}")
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
    plt.plot(data["mode_axis"][data["tune_data"][pi, :]])
    plt.xlabel(f"Modes at peak tune {data['tune_axis'][pi]}")
    set(ax6, "YTick", [])

    data["time"] = datetime.datetime.now()
    data["base_name"] = ["Spectrum_", mbf_axis, "_axis"]
    ## saving the data to a file
    save_to_archive(root_string, data, graph_handles)
    mbf_restore_all()

    return data


def hannwin(data, dim=None):
    s = data.shape
    if not dim:
        [_1, dim] = max(s)

    rh = s
    rh[dim] = 1
    t = np.linspace(0, 2 * np.pi, s[dim] + 1)
    t = t[0:-2]
    h = 1 - np.cos(t)
    data_windowed = data * (np.repmat(np.fft.shiftdim(h, dim), rh))
    return data_windowed


def mbf_spectrum_all(
    mbf_axis,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    n_turns=1000,
    repeat=1,
):
    # Top level def to run all spectral measurements on selected plane['']:
    # Args:
    #       mbf_axis (str): 'x', 'y', 's'[''] Defines which system you are requesting
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes['']
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes['']
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive['']
    #       n_turns (int): number of turns to capture[''] Default is 1000['']
    #       repeat (int): Number of repeat points (improves the power resolution)['']
    #                     Default is 1['']
    #
    # Example mbf_spectrum_all
    [root_string, harmonic_number, pv_names] = mbf_system_config
    pv_head = pv_names["hardware_names"][mbf_axis]
    # for archival investigations this allows filtering by machine state['']
    # but for capture this is not needed so it set to empty['']
    filter_conditions = []
    # getting general environment data['']
    spectrum = machine_environment
    # Add the extra data to the data structure['']
    spectrum["ax_label"] = mbf_axis
    spectrum["base_name"] = f"Spectrum_{mbf_axis}_axis"
    spectrum["harmonic_number"] = harmonic_number
    spectrum["mbf_axis"] = mbf_axis
    spectrum["auto_setup"] = auto_setup
    spectrum["plotting"] = plotting
    spectrum["additional_save_location"] = additional_save_location
    spectrum["n_turns"] = n_turns
    spectrum["repeat"] = repeat

    if auto_setup == "yes":
        # Get the current FIR gain
        orig_fir_gain = get_variable(f"{pv_head}{':FIR:GAIN_S'}")
        # Programatically press the tune only button on each system['']
        setup_operational_mode(mbf_axis, "TuneOnly")

    spectrum["mbf_state"] = get_operational_mode(mbf_axis)
    mbf_spectrum_setup(spectrum, pv_names)
    spectrum["raw_data"] = mbf_spectrum_capture(spectrum, pv_names)
    if auto_setup == "yes":
        setup_operational_mode(mbf_axis, "Feedback")
        # Setting the FIR gain to its original value['']
        set_variable(f"{pv_head}{':FIR:GAIN_S'}", orig_fir_gain)

    ## saving the data to a file
    save_to_archive(root_string, spectrum)
    if additional_save_location:
        scipy.savemat(additional_save_location, spectrum)

    if plotting == "yes":
        mbf_spectra_archival_retrieval(
            mbf_axis, [spectrum["time"], spectrum["time"]], filter_conditions
        )


def mbf_spectrum_analysis(input_data):
    # Analysis the raw time data from the mbf system in order to
    # generate a spectrogram of all bunches['']
    #
    # Args:
    #       raw_data (cell array): Multiple sets of time data['']
    #       turns_override(int): Forces the analysis to use a certain number of
    #                            turns in the analysis[''] This is useful for
    #                            comparing different datasets['']
    #                            Time domain data is eihter padded or trimmed
    #                            as needed['']
    # Returns:
    #           data (structure): analysed data['']
    #
    # Example: data = mbf_spectrum_analysis(raw_data, 1)
    if isstruct(input_data["raw_data"]):
        temp = input_data["raw_data"].keys()
        input_data["raw_data"] = input_data["raw_data"][temp[1]]

    # for k=1:raw_data['repeat']
    #     data_length=len(raw_data['raw_data'][k])
    for k in range(input_data["repeat"]):
        # Individual bunch analysis['']
        # turn into matrix bunches x turns
        xx = np.reshape(input_data["raw_data"][k], input_data["harmonic_number"], [])
        # subtract the average position per bunch
        xx = xx - np.repmat(np.mean(xx, 2), 1, input_data["n_turns"])
        motion_only = np.reshape(xx, 1, [])  # stretch out again
        hanning_filter = hanning(len(motion_only))
        motion_only_windowed = motion_only * hanning_filter
        motion_only_windowed_padded = padarray(
            motion_only_windowed,
            [
                0,
                (input_data["harmonic_number"] * input_data["n_turns"])
                - len(motion_only_windowed),
            ],
            0,
            "post",
        )
        motion_only_windowed_padded = np.reshape(
            motion_only_windowed_padded, input_data["harmonic_number"], []
        )
        # find the overall spectrum of the motion
        # with the static position offsets removed.
        xf1 = abs(np.fft(motion_only_windowed_padded, [], 2)) / input_data["n_turns"]
        if k == 1:
            bunch_motion = xx
            bunch_motion_spectrum = xf1
        else:
            bunch_motion_spectrum = bunch_motion_spectrum + xf1  # accumulating
            bunch_motion = bunch_motion + xx  # accumulating

    # Generating the frquency scales
    frev = input_data["RF"] / input_data["harmonic_number"]
    timescale = range(input_data["n_turns"]) / frev  # sec
    timestep = timescale[1] - timescale[0]
    bunch_motion_f_scale = (
        1
        / timestep
        * range(
            -(input_data["n_turns"] / 2) + 1,
            (input_data["n_turns"] / 2) / input_data["n_turns"],
        )
    )  # Hz
    data = {}
    data["bunch_motion"] = bunch_motion
    data["bunch_motion_timescale"] = timescale
    data["bunch_f_data"] = bunch_motion_spectrum
    data["bunch_f_bunches"] = sum(bunch_motion_spectrum ^ 2, 2)
    data["bunch_f"] = sum(bunch_motion_spectrum ^ 2, 1)
    data["bunch_f_scale"] = bunch_motion_f_scale
    data["bunch_tune_scale"] = bunch_motion_f_scale / (
        input_data["RF"] / input_data["harmonic_number"]
    )
    return data


def mbf_spectrum_capture(input_settings, pv_names):
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
    captured_data = []
    for k in range[repeat:-1, 1]:
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


def mbf_spectrum_plotting(requested_data, analysed_data):
    # Plots the data saved and analysed by the earlier mbf_spectrum def s['']:
    # Args:
    #         all_data(structure): analysed data['']
    #
    # Example: mbf_spectrum_plotting(data
    if max(max(analysed_data["bunch_f_data"])) == 0:
        print("No data to plot")
        return

    plt.figure("Position", [20, 40, 1200, 800])
    fig, ax = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    fig.title(
        f"MBF spectrum results {requested_data['ax_label']} axis "
        f"{requested_data['time'].strftime('%a %d %b %Y, %I:%M%p')} "
        f"Current: {round(requested_data['current'])} mA"
    )
    signal_per_bunch = sum(analysed_data["bunch_f_data"], 2)
    frequency_all_bunches = sum(analysed_data["bunch_f_data"], 1)

    plt.imagesc(
        "Xdata",
        analysed_data["bunch_f_scale"][""] * 1e-3,
        "Ydata",
        range(len(analysed_data["bunch_f_bunches"])),
        "Cdata",
        analysed_data["bunch_f_data"],
        [-3, 0] + max(max(analysed_data["bunch_f_data"])),
    )
    plt.colorbar("westoutside")
    set(ax[0], "YAxisLocation", "right")
    set(ax[0], "YDir", "normal")
    set(ax[0], "XTick", [])
    set(ax[0], "YTick", [])
    # plt.title(axis_label)
    # bunches graph
    plt.plot(signal_per_bunch, range(len(analysed_data["bunch_f_bunches"])))
    set(ax[1], "YAxisLocation", "right")
    set(ax[1], "XAxisLocation", "top")
    set(ax[1], "XTick", [])
    plt.ylabel("Bunch number")

    # Frequency graph
    ax[2].plot(analysed_data["bunch_f_scale"] * 1e-3, frequency_all_bunches)
    plt.xlabel("Frequency (KHz)")
    plt.xlim(
        min(analysed_data["bunch_f_scale"]) * 1e-3,
        max(analysed_data["bunch_f_scale"]) * 1e-3,
    )
    plt.ylim(0, max(frequency_all_bunches))
    # Tune graph
    ax[3].plot(analysed_data["bunch_tune_scale"], frequency_all_bunches)
    ax[3].ylim([0, max(frequency_all_bunches)])
    lims = ax[3].ylim
    ax[3].plot(
        [
            requested_data["tunes"]["x_tune"]["tune"],
            requested_data["tunes"]["x_tune"]["tune"],
        ],
        [0, lims[1]],
        ":r",
        "LineWidth",
        2,
        "DisplayName",
        "Horizontal tune",
    )
    ax[3].plot(
        [
            requested_data["tunes"]["y_tune"]["tune"],
            requested_data["tunes"]["y_tune"]["tune"],
        ],
        [0, lims[1]],
        ":c",
        "LineWidth",
        2,
        "DisplayName",
        "Vertical tune",
    )
    ax[3].plot(
        [
            requested_data["tunes"]["s_tune"]["tune"],
            requested_data["tunes"]["s_tune"]["tune"],
        ],
        [0, lims[1]],
        ":g",
        "LineWidth",
        2,
        "DisplayName",
        "Longitudinal tune",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["x_tune"]["tune"],
            -requested_data["tunes"]["x_tune"]["tune"],
        ],
        [0, lims[1]],
        ":r",
        "LineWidth",
        2,
        "DisplayName",
        "Horizontal tune",
        "HandleVisibility",
        "off",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["y_tune"]["tune"],
            -requested_data["tunes"]["y_tune"]["tune"],
        ],
        [0, lims[1]],
        ":c",
        "LineWidth",
        2,
        "DisplayName",
        "Vertical tune",
        "HandleVisibility",
        "off",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["s_tune"]["tune"],
            -requested_data["tunes"]["s_tune"]["tune"],
        ],
        [0, lims[1]],
        ":g",
        "LineWidth",
        2,
        "DisplayName",
        "Longitudinal tune",
        "HandleVisibility",
        "off",
    )
    plt.xlabel("Tune")


def mbf_spectrum_setup(input_settings, pv_names):
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
    for trigger_ind in range(1, len(trigger_inputs)):
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
