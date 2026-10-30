import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy

from Common import (
    get_operational_mode,
    get_variable,
    ind2sub,
    machine_environment,
    mbf_analysis_reorganise_for_parameter_sweep,
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
    mbf_setup_wait_for_hw_trigger,
    mbf_system_config,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def Bunch_motion_all(auto_setup="yes", plotting="yes", additional_save_location=None):
    [root_string, harmonic_number, pv_names] = mbf_system_config
    mbf_tools()
    # for archival investigations this allows filtering by machine state.
    # but for capture this is not needed so it set to empty.
    filter_conditions = []
    # getting general environment data
    bunch_motion = machine_environment()
    # Add the extra data to the data structure.
    bunch_motion["base_name"] = "Bunch_motion"
    bunch_motion["harmonic_number"] = harmonic_number
    if auto_setup == "yes":
        # Get the current FIR gains
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
        mbf_bunch_motion_archival_retrieval(
            [bunch_motion["time"], bunch_motion["time"]], filter_conditions
        )

    return


def mbf_bunch_motion_analysis(data):
    x = np.reshape(data["x"], data["num_buckets"], [])
    y = np.reshape(data["y"], data["num_buckets"], [])
    z = np.reshape(data["z"], data["num_buckets"], [])
    turn_numbers = range(x.shape[1])
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(x[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(y[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(z[:, 1:100], 2), 1, len(turn_numbers))
    x = x - x_ref
    y = y - y_ref
    z = z - z_ref
    # Find the location of the largest disturbance['']
    [minx, minindx] = min(x[:])
    [maxx, maxindx] = max(x[:])
    [miny, minindy] = min(y[:])
    [maxy, maxindy] = max(y[:])
    [minz, minindz] = min(z[:])
    [maxz, maxindz] = max(z[:])
    _1, loc = max([abs(minx), maxx, abs(miny), maxy, abs(minz), maxz])
    indexes = [minindx, maxindx, minindy, maxindy, minindz, maxindz]
    index_of_peak = indexes(loc)
    [peak_row, peak_col] = ind2sub(x.shape, index_of_peak)
    output = {}
    output["turn_of_peak"] = peak_col
    output["bucket_of_peak"] = peak_row - 1
    output["mean_bunches_x"] = np.mean(x, 1)
    output["mean_bunches_y"] = np.mean(y, 1)
    output["mean_bunches_z"] = np.mean(z, 1)
    output["std_bunches_x"] = np.std(x, ddof=1, axes=1)
    output["std_bunches_y"] = np.std(y, ddof=1, axes=1)
    output["std_bunches_z"] = np.std(z, ddof=1, axes=1)
    output["mean_turns_x"] = np.mean(x, 0)
    output["mean_turns_y"] = np.mean(y, 0)
    output["mean_turns_z"] = np.mean(z, 0)
    output["std_turns_x"] = np.std(x, ddof=1, axes=0)
    output["std_turns_y"] = np.std(y, ddof=1, axes=0)
    output["std_turns_z"] = np.std(z, ddof=1, axes=0)
    output["x_norm"] = x
    output["y_norm"] = y
    output["z_norm"] = z
    return output


def mbf_bunch_motion_archival_analysis(
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
    #                                                   data_requested, 'average')
    times = []
    param = []
    for nd in range(len(data_requested)):
        times[nd] = datetime.datetime(data_requested[nd]["time"])
        data = mbf_bunch_motion_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        states = data.keys()
        for st in range(len(states)):
            if nd == len(data_requested):
                temp_size = data[states[st]].shape
                dataset[states[st]] = []

            dataset[states[st]][nd, :, :] = data[states[st]]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        dataset, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(dataset, param, parameter_step)
        )
    elif analysis_type == "average":
        print(
            "Archive:bunch_motion:setting"
            "Ignoring the last two parameters as 'average' is set"
        )
        states = dataset.keys()
        for st in range(len(states)):
            meass = dataset[states[st]].keys()
            for ms in range(len(meass)):
                dataset[states[st]][meass[ms]] = np.mean(
                    dataset[states[st]][meass[ms]], 0
                )


def mbf_bunch_motion_archival_plotting(
    requested_data, dataset, times, experimental_setup
):
    # Plots the data processed by mbf_growdamp_archival_analysis.
    # Args:
    #       dataset (struct): containing
    #      dr_passive (numeric matrix): Passive damping rate.
    #                                   (bunches vs datasets)
    #      dr_active (numeric matrix): Passive damping rate.
    #                                   (bunches vs datasets)
    #      error_passive (numeric matrix): Error of the fit for the passive
    #                                      damping rate.
    #      error_active (numeric matrix): Error of the fit for the active
    #                                     damping rate.
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results of
    #                                    the fit errors.
    #
    # Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive,
    #                                error_active, times, setup, selections, extents)

    # Only do something if there is data to do something with['']
    if not times:
        return

    [_3, harmonic_number, _2, _1] = mbf_system_config
    this_year = datetime.datetime.now().year
    for jshe in range(1, len(requested_data)):
        requested_data[jshe]["turn_of_peak"] = dataset["turn_of_peak"](jshe)
        requested_data[jshe]["bucket_of_peak"] = dataset["bucket_of_peak"](jshe)

    ranges_to_printlay = {"RF", "current", "turn_of_peak", "bucket_of_peak"}
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    graph_text = f"Analysis type: {experimental_setup['anal_type']}"
    graph_title = "Average bunch motion"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Average bunch motion as a def of {experimental_setup['sweep_parameter']}"
            f"Using a step size of {experimental_setup['parameter_step_size']}"
            f" in the {experimental_setup['axis']} axis"
        )
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    plt.figure("Position", [50, 50, 1800, 800])
    plt.annotation(
        "textbox",
        [0, 1 - 0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    ax1 = plt.axes("OuterPosition", [0.18, 0.66, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_x"], years_input, times, 1:harmonic_number]

    plt.title(graph_title)
    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in x")
    ax2 = plt.axes("OuterPosition", [0.18, 0.33, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_y"], years_input, times, 1:harmonic_number]

    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in y")
    ax3 = plt.axes("OuterPosition", [0.18, 0, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_z"], years_input, times, 1:harmonic_number]

    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in s")

    graph_title = "Average turn motion"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Average turn motion as a def of {experimental_setup['sweep_parameter']}"
        )
        f"Using a step size of {experimental_setup['parameter_step_size']} "
        f"in the {experimental_setup['axis']} axis"

    ax4 = plt.axes("OuterPosition", [0.52, 0.66, 0.5, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_x"],
            years_input,
            times,
            range(len(dataset["mean_turns_x"])),
        )

    plt.title(graph_title)
    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in x")
    plt.legend("Location", "eastOutside")
    ax5 = plt.axes("OuterPosition", [0.52, 0.33, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_y"],
            years_input,
            years_colours,
            times,
            range(len(dataset["mean_turns_y"])),
        )

    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in y")
    ax6 = plt.axes("OuterPosition", [0.52, 0, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_z"],
            years_input,
            years_colours,
            times,
            range(len(dataset["mean_turns_z"])),
        )

    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in s")

    ck = 0
    n_graphs = len(ranges_to_printlay)
    for hrd in range(1, n_graphs):
        plt.axes(
            "OuterPosition", [0.01, 0.3 + ck * 0.6 / n_graphs, 0.2, 0.6 / n_graphs]
        )
        plt.xlabel("Time")
        plt.title(ranges_to_printlay[hrd])
        data_temp = []
        for hse in range(1, len(times)):
            data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

        plt.plot(times, data_temp, "o:")
        plt.ylabel(ranges_to_printlay[hrd])

        ck = ck + 1

    axfp = plt.axes("OuterPosition", [0.01, 0, 0.2, 0.3])
    for hkw in range(len(requested_data)):
        plt.plot(range(harmonic_number), requested_data[hkw]["fill_pattern"], "b")

    plt.ylim(0)
    plt.xlim(1, harmonic_number)
    set(axfp, "XTick", [])
    plt.title("Fill pattern variation")
    plt.ylabel("Charge (nC)")
    # add labels if it is a parameter sweep['']
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"])):
            labels[tb] = experimental_setup["param"][tb]

        plt.legend(labels)


def populate_graph(input_data, years_input, times, x_plt_axis):
    if not input_data:
        return

    y_max = max(max(input_data))
    y_min = min(min(input_data))
    years = []
    states = []
    cols = []
    for esr in range(years_input.shape[0]):
        years[esr] = years_input[esr][0]
        states[esr] = 0
        cols[esr] = years_input[esr][1]

    year_list = times.year
    if len(np.unique(year_list)) < 2:
        for ner in range(input_data.shape[0]):
            sample_time = times[ner].strftime("%a %d %b %Y, %I:%M%p")
            plt.plot(
                x_plt_axis,
                input_data[ner, :],
                "DisplayName",
                sample_time,
                "LineWidth",
                2,
            )

    else:
        for ner in range(input_data.shape[0]):
            years_ind = np.find(year_list(ner) == years)
            if states[years_ind] == 0:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "DisplayName",
                    (year_list(ner)),
                    "LineWidth",
                    2,
                )
                states[years_ind] = 1
            else:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "HandleVisibility",
                    "off",
                    "LineWidth",
                    2,
                )

    plt.xlim(x_plt_axis(1), x_plt_axis(-1))
    plt.ylim(y_min, y_max)
    plt.legend("show")


def mbf_bunch_motion_archival_retrieval(
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    selected_bunches=range(150, 161),
    selected_turns=range(600, 651),
):
    # Extracts requested data from the data archive between
    # the requested times(date_range)
    #
    # Args:
    #       date_range (pair of datetime instances): The range of time to extract.
    #       bypass_index (str) : 'no' for use the pregnerated index (much faster)
    #                            'yes' for work things out from the file metatdata.
    #                            the default is 'no'.
    #       metadata_only(str): 'no' return all data
    #                            'yes' remove the sample data from the output structure.
    #                            the default is 'no'.
    #
    # Example: mbf_bunch_motion_archival_retrieval([now-5, now])

    selection_name = "Bunch_motion"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        dataset, _2, _1 = mbf_bunch_motion_archival_analysis(
            requested_data, analysis_type="collate"
        )
        mbf_bunch_motion_plotting(
            dataset, requested_data[1], selected_bunches, selected_turns
        )
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                dataset, times, setup = mbf_bunch_motion_archival_analysis(
                    conditioned_data, analysis_type == "collate"
                )
            elif analysis_type == "parameter_sweep":
                dataset, times, setup = mbf_bunch_motion_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                )
            else:
                raise ValueError(
                    "bunch_motionArchivalRetrieval:InputError"
                    "Please select collate or sweep as the analysis type"
                )

            mbf_bunch_motion_archival_plotting(conditioned_data, dataset, times, setup)

    return dataset, times, setup


def mbf_bunch_motion_capture(pv_names):
    # simultaineously captures bunch by bunch centroid data for all three axes.
    # When armed by the code each system will start aquisition
    # on the next hardware trigger.
    #
    # Example: bunch_motion = mbf_bunch_motion_capture(pv_names)
    [turn_count, turn_offset] = mbf_bunch_motion_config
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
    mem_t = lcaGet(f"{pv_head_T}{pv_names['tails']['TRG']['memory_status']}")
    mem_s = lcaGet(f"{pv_head_L}{pv_names['tails']['TRG']['memory_status']}")
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


def mbf_bunch_motion_plotting(data, selected_bunches, selected_turns):
    x = np.reshape(data["x"], data["num_buckets"], [])
    y = np.reshape(data["y"], data["num_buckets"], [])
    z = np.reshape(data["z"], data["num_buckets"], [])
    bucket_numbers = range(data["num_buckets"])
    turn_numbers = range(x.shape[1])
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(x[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(y[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(z[:, 1:100], 2), 1, len(turn_numbers))
    x = x - x_ref
    y = y - y_ref
    z = z - z_ref
    # Find the location of the largest disturbance.
    # FIXME how do you do this using numpy?
    [minx, minindx] = min(x)
    [maxx, maxindx] = max(x)
    [miny, minindy] = min(y)
    [maxy, maxindy] = max(y)
    [minz, minindz] = min(z)
    [maxz, maxindz] = max(z)
    [_1, loc] = max([abs(minx), maxx, abs(miny), maxy, abs(minz), maxz])
    indexes = [minindx, maxindx, minindy, maxindy, minindz, maxindz]
    index_of_peak = indexes(loc)
    [peak_row, peak_col] = ind2sub(x.shape, index_of_peak)
    turn_of_peak = peak_col
    bucket_of_peak = peak_row - 1
    print(f"Start turn of kick is {turn_of_peak}")
    print(f"Main bucket kicked {bucket_of_peak}")
    fill_pattern = data["fill_pattern2"]

    meanx = np.mean(x, 1)
    meany = np.mean(y, 1)
    meanz = np.mean(z, 1)
    stdx = np.std(x, ddof=1, axes=1)
    stdy = np.std(y, ddof=1, axes=1)
    stdz = np.std(z, ddof=1, axes=1)
    f1 = plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(4, 1)
    plt.title(data["filename"], "Interpreter", "None")
    plt.xlabel("Bunches")
    # ax1 = nexttile
    plt.plot(bucket_numbers, fill_pattern)
    plt.ylabel("Charge")
    # ax2 = nexttile
    plt.plot(
        bucket_numbers,
        meanx,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meanx + stdx, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meanx - stdx, "m", "HandleVisibility", "off")
    plt.title("Horizontal motion")
    plt.ylabel("Motion")
    # ax3 = nexttile
    plt.plot(
        bucket_numbers,
        meany,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meany + stdy, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meany - stdy, "m", "HandleVisibility", "off")
    plt.title("Vertical motion")
    plt.ylabel("Motion")
    # ax4 = nexttile
    plt.plot(
        bucket_numbers,
        meanz,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meanz + stdz, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meanz - stdz, "m", "HandleVisibility", "off")
    plt.title("Longitudinal motion")
    plt.ylabel("Motion")

    f2 = plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 3)
    plt.title(t, data["filename"], "Interpreter", "None")
    plt.xlabel(t, "Turns")
    plt.imagesc(turn_numbers, bucket_numbers, x)
    plt.title("Horizontal motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    # Sometimes matlab has a delay plotting the previous plot
    # and this breaks everything.
    plt.imagesc(turn_numbers, bucket_numbers, y)
    plt.title("Vertical motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    plt.imagesc(turn_numbers, bucket_numbers, z)
    plt.title("Longitudinal motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            x[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.legend("Location", "northoutside", "NumColumns", 2)
    plt.title("Horizontal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            y[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Vertical motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            z[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Longitudinal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            x[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.legend("Location", "northoutside", "NumColumns", 2)
    plt.title("Horizontal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            y[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Vertical motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            z[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Longitudinal motion")
    # FIXME make sure the coeect graph is saved to the correct file.
    plt.savefig(f"{data['filename']}_bunches.png")
    plt.savefig(f"{data['filename']}_turns.png")


def mbf_bunch_motion_setup(pv_names):
    # Sets up all three axis so that they will take a single set of data each
    # when armed and triggered
    #
    # Example: mbf_bunch_motion_setup
    memory_triggers = pv_names["tails"]["triggers"]["MEM"]
    memory_buffers = pv_names["tails"]["MEM"]
    mbf_setup_wait_for_hw_trigger(pv_names)
    PVt = pv_names["tails"]
    mbf_systems = {"T", "L"}
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


def mbf_bunch_motion_spectra_plotting(data):
    xt = np.reshape(data["x"], data["num_buckets"], [])
    yt = np.reshape(data["y"], data["num_buckets"], [])
    zt = np.reshape(data["z"], data["num_buckets"], [])
    n_turns = xt.shape[1]
    bucket_numbers = range(data["num_buckets"])
    turn_numbers = range(n_turns)
    T = 1  # turns Sampling period
    Fs = 1 / T  # Sampling frequency
    f_scale = Fs * (range((n_turns / 2) + 1)) / n_turns
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(xt[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(yt[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(zt[:, 1:100], 2), 1, len(turn_numbers))
    xt = xt - x_ref
    yt = yt - y_ref
    zt = zt - z_ref
    x1 = np.fft(xt, [], 2)
    x1 = abs(x1 / n_turns)
    x = x1[:, 1 : n_turns / 2 + 1]
    x[:, 2:-2] = 2 * x[:, 2:-2]
    y1 = np.fft(yt, [], 2)
    y1 = abs(y1 / n_turns)
    y = y1[:, 1 : n_turns / 2 + 1]
    y[:, 2:-2] = 2 * y[:, 2:-2]
    z1 = np.fft(zt, [], 2)
    z1 = abs(z1 / n_turns)
    z = z1[:, 1 : n_turns / 2 + 1]
    z[:, 2:-2] = 2 * z[:, 2:-2]
    # Find the location of the largest disturbance.
    [maxx, maxindx] = max(x[:])
    peak_row_x, peak_col_x = ind2sub(x.shape, maxindx)
    f_of_peak_x = f_scale(peak_col_x)
    bucket_of_peak_x = peak_row_x - 1
    [maxy, maxindy] = max(y[:])
    peak_row_y, peak_col_y = ind2sub(y.shape, maxindy)
    f_of_peak_y = f_scale(peak_col_y)
    bucket_of_peak_y = peak_row_y - 1
    [maxz, maxindz] = max(z[:])
    peak_row_z, peak_col_z = ind2sub(z.shape, maxindz)
    f_of_peak_z = f_scale(peak_col_z)
    bucket_of_peak_z = peak_row_z - 1
    _1, loc = max([maxx, maxy, maxz])
    ax_labs = {"x", "y", "z"}
    print(f"Axis with most disturbance is {ax_labs[loc]}")
    print(f"Tune of main disturbance in x is {f_of_peak_x}")
    print(f"Bucket of main disturbance in x is {bucket_of_peak_x}")
    print(f"Tune of main disturbance in y is {f_of_peak_y}")
    print(f"Bucket of main disturbance in y is {bucket_of_peak_y}")
    print(f"Tune of main disturbance in z is {f_of_peak_z}")
    print(f"Bucket of main disturbance in z is {bucket_of_peak_z}")
    plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 1)
    plt.title(data["filename"], "Interpreter", "None")
    plt.ylabel("Bunches")
    plt.xlabel("Tune (1/Turns)")
    # ax2 = nexttile
    plt.imagesc(f_scale, bucket_numbers, x)
    plt.title("Horizontal motion")
    # ax3 = nexttile
    plt.imagesc(f_scale, bucket_numbers, y)
    plt.title("Vertical motion")
    # ax4 = nexttile
    plt.imagesc(f_scale, bucket_numbers, z)
    plt.title("Longitudinal motion")
    plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 1)
    plt.title(data["filename"], "Interpreter", "None")
    plt.ylabel("Bunches")
    plt.xlabel("Tune (1/Turns)")
    # ax2 = nexttile
    plt.plot(f_scale, abs(x[bucket_of_peak_x + 1, :]))
    plt.title(["Horizontal motion (bucket ", (bucket_of_peak_x), ")"])
    # ax3 = nexttile
    plt.plot(f_scale, abs(y[bucket_of_peak_y + 1, :]))
    plt.title(["Vertical motion (bucket ", (bucket_of_peak_y), ")"])
    # ax4 = nexttile
    plt.plot(f_scale, abs(z[bucket_of_peak_z + 1, :]))
    plt.title(["Longitudinal motion (bucket ", (bucket_of_peak_z), ")"])
