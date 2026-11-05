from analysis import (
    bunch_motion_archival_analysis,
    frontend_clock_phase_scan_archival_analysis,
    frontend_gain_scan_archival_analysis,
    frontend_system_phase_scan_archival_analysis,
    growdamp_archival_analysis,
    growthrates_archival_analysis,
    modescan_archival_analysis,
    spectra_archival_analysis,
    tunescan_over_modes_archival_analysis,
)
from plotting import (
    bunch_motion_archival_plotting,
    bunch_motion_plotting,
    frontend_clock_phase_scan_archival_plotting,
    frontend_clock_phase_scan_plotting,
    frontend_gain_scan_archival_plotting,
    frontend_gain_scan_plotting,
    frontend_system_phase_scan_archival_plotting,
    frontend_system_phase_scan_plotting,
    growdamp_archival_plotting,
    growdamp_plot_summary,
    growthrates_archival_plotting,
    modescan_archival_plotting,
    modescan_plotting,
    spectra_archival_plotting,
    tunescan_over_modes_archival_plotting,
    tunescan_over_modes_plot_summary,
)

from Common import (
    archival_conditional_filtering,
    archival_dataset_retrieval,
)


def archival_retrieval(
    selection,
    ax,
    date_range,
    measurement_specific_options,
    analysis_function,
    plotting_function,
    plotting_summary_function,
    filter_conditions,
    bypass_index,
    metadata_only,
    analysis_type,
    sweep_parameter,
    parameter_step,
    debug,
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
    #       analysis_type(str): determines the type of analysis to run 'collate' or
    #                           'sweep', the default is 'collate'.
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
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
    # Example: growdamp_archival_retrieval('x',
    #          [datetime(2023, 1, 1), datetime("now")])
    if ax:
        selection_name = f"{selection}_{ax}_axis"
    else:
        selection_name = selection

    requested_data = archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )

    if len(requested_data) == 1 and plotting_summary_function:
        [dataset, _2, _1] = analysis_function(
            requested_data,
            analysis_type="collate",
            measurement_specific_options=measurement_specific_options,
            debug=debug,
        )
        plotting_summary_function(dataset, requested_data[0])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [dataset, times, setup] = analysis_function(
                    conditioned_data,
                    analysis_type="collate",
                    measurement_specific_options=measurement_specific_options,
                    debug=debug,
                )
            elif analysis_type == "sweep":
                [dataset, times, setup] = analysis_function(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                    measurement_specific_options=measurement_specific_options,
                    debug=debug,
                )

            setup["axis"] = ax
            plotting_function(conditioned_data, dataset, times, setup)

    return dataset, times, setup


def growdamp_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    active_override=None,
    passive_override=None,
    advanced_fitting=0,
    debug=0,
):
    measurement_specific_options = {}
    measurement_specific_options["active_override"] = active_override
    measurement_specific_options["passive_override"] = passive_override
    measurement_specific_options["advanced_fitting"] = advanced_fitting
    dataset, times, setup = archival_retrieval(
        "Growdamp",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=growdamp_archival_analysis,
        plotting_function=growdamp_archival_plotting,
        plotting_summary_function=growdamp_plot_summary,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def growthrates_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    overrides=[None, None],
    advanced_fitting=0,
    current_range=[2, 150],
    debug=0,
):

    measurement_specific_options = {}
    measurement_specific_options["overrides"] = overrides
    measurement_specific_options["advanced_fitting"] = advanced_fitting

    dataset, times, setup = archival_retrieval(
        "Growthrates",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=growthrates_archival_analysis,
        plotting_function=growthrates_archival_plotting,
        plotting_summary_function=None,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def modescan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):

    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        "Modescan",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=modescan_archival_analysis,
        plotting_function=modescan_archival_plotting,
        plotting_summary_function=modescan_plotting,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def spectra_all_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    current_range=(2, 150),
):
    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        "Spectrum",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=spectra_archival_analysis,
        plotting_function=spectra_archival_plotting,
        plotting_summary_function=None,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def bunch_motion_archival_retrieval(
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
    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        selection="Bunch_motion",
        ax=None,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=bunch_motion_archival_analysis,
        plotting_function=bunch_motion_archival_plotting,
        plotting_summary_function=bunch_motion_plotting,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def frontend_clock_phase_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        selection="clock_phase_scan",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=frontend_clock_phase_scan_archival_analysis,
        plotting_function=frontend_clock_phase_scan_archival_plotting,
        plotting_summary_function=frontend_clock_phase_scan_plotting,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def frontend_gain_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        selection="frontend_gain_scan",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=frontend_gain_scan_archival_analysis,
        plotting_function=frontend_gain_scan_archival_plotting,
        plotting_summary_function=frontend_gain_scan_plotting,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def frontend_system_phase_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):

    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        selection="system_phase_scan",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=frontend_system_phase_scan_archival_analysis,
        plotting_function=frontend_system_phase_scan_archival_plotting,
        plotting_summary_function=frontend_system_phase_scan_plotting,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def tunescan_over_modes_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    active_override=None,
    passive_override=None,
    advanced_fitting=0,
    current_range=(2, 305),
    debug=0,
):

    measurement_specific_options = {}
    dataset, times, setup = archival_retrieval(
        selection="tunescan",
        ax=ax,
        date_range=date_range,
        measurement_specific_options=measurement_specific_options,
        analysis_function=tunescan_over_modes_archival_analysis,
        plotting_function=tunescan_over_modes_archival_plotting,
        plotting_summary_function=tunescan_over_modes_plot_summary,
        filter_conditions=filter_conditions,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        debug=0,
    )
    return dataset, times, setup


def frontend_gain_scan_retrival():
    pass


def frontend_system_phase_scan_retrival():
    pass


def bunch_motion_retrival():
    pass


def clock_phase_scan_retrival():
    pass


def doris_target_phase_scan_retrival():
    pass


def pll_phase_scan_retrival():
    pass


def tunescan_over_modes_retrival():
    pass


def growdamp_archive_calculate_extents(input_data):
    extents = {}
    for ke in range(len(input_data)):
        data_field_names = input_data[ke].keys()
        for haw in range(1, len(data_field_names)):
            if ~data_field_names[haw] in extents:
                # initialisation
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][0] = input_data[ke][
                        data_field_names[haw]
                    ]
                    extents[data_field_names[haw]][1] = input_data[ke][
                        data_field_names[haw]
                    ]
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][0] = input_data[ke][
                            data_field_names[haw]
                        ]
                        extents[data_field_names[haw]][1] = input_data[ke][
                            data_field_names[haw]
                        ]
            else:
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][0] = max(
                        [
                            extents[data_field_names[haw]][0],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                    extents[data_field_names[haw]][1] = min(
                        [
                            extents[data_field_names[haw]][1],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][0] = max(
                            [
                                extents[data_field_names[haw]][0],
                                input_data[ke][data_field_names[haw]],
                            ]
                        )
                        extents[data_field_names[haw]][1] = min(
                            [
                                extents[data_field_names[haw]][1],
                                input_data[ke][data_field_names[haw]],
                            ]
                        )
    return extents


def growdamp_archive_data_conditioning(data_slice):
    field_nms = data_slice.keys()
    conditioned_data = {}
    for kef in range(1, len(field_nms)):
        # This section is to deal with variations in data naming
        # and structuring over the years['']
        if field_nms[kef] == "I_bpm":
            conditioned_data["current"] = data_slice["I_bpm"]
        elif field_nms[kef] == "fill":
            conditioned_data["fill_pattern"] = data_slice["fill"]
        elif field_nms[kef] == "id":
            conditioned_data["wiggler_field_I12"] = data_slice["id"]["i12field"]
            conditioned_data["wiggler_field_I15"] = data_slice["id"]["i15field"]
        elif field_nms[kef] == "life":
            conditioned_data["beam_lifetime"] = data_slice["life"]["bpm"]["life300sec"]
        elif field_nms[kef] == "RFread":
            conditioned_data["cavity1_voltage"] = data_slice["RFread"]
            conditioned_data["cavity2_voltage"] = data_slice["RFread"]
        else:
            conditioned_data[field_nms[kef]] = data_slice[field_nms[kef]]
    return conditioned_data


def archive_retreval_investigate_metadata(requested_data: list[dict]):
    # mapping older and newer metadata
    for nfe in range(1, len(requested_data)):
        if "I_bpm" in requested_data[nfe]:
            requested_data[nfe]["current"] = requested_data[nfe]["I_bpm"]

        if "fill" in requested_data[nfe]:
            requested_data[nfe]["fill_pattern"] = requested_data[nfe]["fill"]

    for nfe in range(1, len(requested_data)):
        temp = requested_data[nfe].keys()
        if nfe == 1:
            fields = temp
        else:
            fields = list(set(fields).intersection(set(temp)))

    # remove the fields which are not useful to compare.
    inds = any(
        cat(
            2,
            fields == "ax_label",
            fields == "filename",
            fields == "data",
            fields == "time",
        ),
        2,
    )
    fields[inds] = []
    metadata = []
    for hse in range(1, len(fields)):
        for wak in range(1, len(requested_data)):
            metadata[hse][wak] = requested_data[wak][fields[hse]]

    for nfe in range(1, len(requested_data)):
        print([requested_data[nfe]["current"], "  ", requested_data[nfe]["ringmode"]])


def fll_phase_scan_archival_extraction(
    mbf_axis,
    date_range,
    scan_type="samples",
    filter_type="none",
    filter_range=(-10000, 10000),
):
    if mbf_axis == "x":
        filter_name = "fll_phase_scan_x_axis"
    elif mbf_axis == "y":
        filter_name = "fll_phase_scan_y_axis"

    requested_data = archival_dataset_retrieval(
        filter_name, date_range, "bypass_index", "no"
    )
    # some data had many NaN collumns - this is to remove them['']
    for nds in range(1, len(requested_data)):
        requested_data[nds]["f"] = requested_data[nds]["f"][:, 1]
        requested_data[nds]["mag"] = requested_data[nds]["mag"][:, 1]
        requested_data[nds]["iq"] = requested_data[nds]["iq"][:, 1]

    # filter out broken data
    data_state = np.ones(len(requested_data))
    for wns in range(1, len(requested_data)):
        if (
            max(requested_data[wns]["f"]) - min(requested_data[wns]["f"]) < 1e-9
            and max(requested_data[wns]["mag"]) - min(requested_data[wns]["mag"]) < 8e-6
        ):
            data_state[wns] = 0

    if filter_type.lower() != "none":
        # user defined filters
        for wns in range(1, len(requested_data)):
            if iscell(filter_type):
                # need to unpack the substructure['']
                data_temp = requested_data[wns]
                for ehf in range(1, len(filter_type)):
                    data_temp = data_temp[""][filter_type[ehf]]

            if data_temp < filter_range[1] or data_temp > filter_range[2]:
                data_state[wns] = 0

    requested_data[data_state == 0] = []
    fll_phase_scan_plotting_multi(requested_data, "scan_type", scan_type)
    return requested_data


def archival_conditional_filtering(requested_data, selections):
    # returns the sets of data which have metadata values below thoise given in
    # selections
    #
    #   Args:
    #       input_data{cell array of structures}
    #       selections{cell array}: collumn 1 is the name of the field in the
    #                               metadata, collumn 2 is the value to be below['']
    #   Returns:
    #       sets {cell array of structures}: Datasets which matched the criteria['']
    #
    # Example conditioned_data = archival_conditional_filtering(requested_data)
    select = np.zeros(len(requested_data))
    for nwd in range(1, len(requested_data)):
        test = NaN(size(selections, 1), 1)
        for law in range(1, selections.shape[0]):
            ref_val = selections[law][2]
            if iscell(selections[law][1]):
                test_val = requested_data[nwd]
                for jsw in range(1, len(selections[law][1])):
                    if selections[law][1][jsw] in test_val:
                        test_val = test_val[selections[law][1][jsw]]
                    else:
                        test_val = None
                        continue

            else:
                if selections[law][1] in requested_data[nwd]:
                    test_val = requested_data[nwd][selections[law][1]]
                else:
                    test_val = None

            if isnan(test_val):
                # If no valid data do not filter['']
                temp = 1
            elif iscell(test_val):
                temp = test_val == ref_val
            elif len(test_val) == 1:
                temp = test_val >= ref_val[1] and test_val <= ref_val[2]
            else:
                temp1 = test_val >= repmat(
                    ref_val(1), test_val.shape[0], test_val.shape[1]
                )
                temp2 = test_val <= repmat(
                    ref_val(2), test_val.shape[0], test_val.shape[1]
                )
                temp1 = not any(not temp1)
                temp2 = not any(not temp2)
                temp = any([temp1, temp2])

            test[law] = temp

        select[nwd] = ~any[not test]

    conditioned_data = requested_data[select]
    return conditioned_data


def archival_dataset_retrieval(
    filter_name, date_range, bypass_index="no", metadata_only="no"
):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax)['']
    #
    # Args:
    #       filter_name(str): Name of the file to select for['']
    #
    #       date_range (pair of timestamps): The range of time to extract['']
    #       bypass_index (str) : 'no' for use the pregnerated index (much faster)
    #                            'yes' for work things out from the file metatdata['']
    #                            the default is 'no'['']
    #
    # Returns:
    #       unpacked_data (cell of structures): The group of requested data
    #                                            structures['']
    #
    # Example: growdamp_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

    # Getting the desired system setup parameters['']
    [root_string, _2, _1] = system_config
    index_name = [filter_name, "_index"]
    if bypass_index == "no":
        load(os.path.join(root_string, index_name), "file_index")
        # Some error in the file index construction this just removes the unwanted
        # empty entries['']
        ck1 = 1
        ck2 = 1
        for jrs in range(file_index.shape[1]):
            if file_index[1][jrs]:
                test[1][ck1] = file_index[1][jrs]
                ck1 += 1

        for jrs in range(file_index.shape[1]):
            if file_index[2][jrs]:
                test[2][ck2] = file_index[2][jrs]
                ck2 += 1

        file_index = test
        # capture_times = cellfun(@datetime, file_index[2,:]) #FIXME
        a = find(capture_times >= date_range(1))
        b = find(capture_times <= date_range(2))
        wanted_datasets = file_index(1, (list(set(a).intersection(set(b)))))
        print("")
    else:
        print(
            "Bypassing index["
            "] This will be slower but is useful if the index is damaged and cannot be imediately regenerated["
            "]"
        )
        datasets = dir_list_gen_tree(root_string, ".mat")
        wanted_datasets_type = datasets(
            find_position_in_cell_lst(strfind(datasets, filter_name))
        )
        # removing the index file
        wanted_datasets_type[
            find_position_in_cell_lst(strfind(wanted_datasets_type, index_name))
        ] = []
        # Prefiltering on folder structure so that the code stays fast as more data
        # is added to the data store['']
        tunc = regexprep(wanted_datasets_type, root_string, "")
        for ha in range(len(tunc)):
            ind = strfind(tunc[ha], filesep)
            year = str2double(tunc[ha][1 : ind[1] - 1])
            month = str2double(tunc[ha][ind[1] + 1 : ind[2] - 1])
            day = str2double(tunc[ha][ind[2] + 1 : ind[3] - 1])
            folder_dates[ha] = datetime(year, month, day)

        a = find(
            folder_dates
            >= floor(date_range(1)) & folder_dates
            <= floor(date_range(2)) + 1
        )
        b = find(folder_dates <= floor(date_range(2)) + 1)
        wanted_datasets_type_prefiltered = wanted_datasets_type(
            list(set(a).intersection(set(b)))
        )
        in_time = np.zeros(len(wanted_datasets_type_prefiltered))
        for kse in range(1, len(wanted_datasets_type_prefiltered)):
            temp = load(wanted_datasets_type_prefiltered[kse])
            file_time = temp["data"]["time"]

            if datetime(file_time) >= date_range(1) and datetime(
                file_time
            ) <= date_range(2):
                in_time[kse] = 1

            print("[]")

        print("\n")
        wanted_datasets = wanted_datasets_type_prefiltered(in_time == 1)

    requested_data = []
    for jes in range(1, len(wanted_datasets)):
        try:
            temp = load(wanted_datasets[jes])
        except:
            [_2, corrupt_file, _1] = fileparts(wanted_datasets[jes])
            print(["skipping corrupt, file(", corrupt_file, ")"])
            continue

        data_name = fieldnames(temp)
        # Although the code saves eveything in 'data', older datasets have
        # a variety of names['']
        if (
            data_name[1] == "data"
            or data_name[1] == "growdamp"
            or data_name[1] == "what_to_save"
        ):
            requested_data[jes] = temp[data_name[1]]

    # There was some variation in the use of field names[''] This regularises them to
    # the current standard['']
    metadata_conditioned_data = condition_mbf_metadata(requested_data)
    conditioned_data = condition_mbf_data(metadata_conditioned_data)
    # expand old data sweeps so that each data entry has only one
    # measurement['']
    if "Growdamp" in filter_name:
        unpacked_data = unpack_old_growdamp_sweeps(conditioned_data)
    else:
        unpacked_data = conditioned_data

    if metadata_only == "yes":
        for nxd in range(1, len(unpacked_data)):
            unpacked_data[nxd] = rmfield(unpacked_data[nxd], "data")

    return unpacked_data


def archival_plotting_setup(requested_data, times, experimental_setup):
    # Plots the data processed by growdamp_archival_analysis['']
    # Args:
    #      requested_data(structure): data and metatdata['']
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #
    # Example: growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)
    [_3, harmonic_number, _2, _1] = system_config
    ranges_to_printlay = {"RF", "time", "current"}
    graph_text[1] = ["Analysis type: ", experimental_setup["anal_type"]]
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_labels = []
        for hw in range(1, len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"](hw)

    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    annotation(
        "textbox",
        [0, 1, -0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    # Plot the RF variation from the setpoint['']
    for hse in range(1, len(times)):
        requested_data[hse]["RF"] = requested_data[hse]["RF"] - 4.99684e8

    ck = 1
    for hrd in range(1, len(ranges_to_printlay)):
        if ranges_to_printlay[hrd] == "RF":
            graph_label = "RF variation (Hz)"
        elif ranges_to_printlay[hrd] == "current":
            graph_label = "Current (mA)"
        else:
            graph_label = ranges_to_printlay[hrd]

        if ranges_to_printlay[hrd] in requested_data[1]:
            if ranges_to_printlay[hrd] == "time":
                continue
            else:
                nexttile(t)
                xlabel("Time")
                title(ranges_to_printlay[hrd])
                data_temp = NaN(len(times), 1)
                for hse in range(1, len(times)):
                    data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

                plot[times, data_temp, "o:"]
                datetick("x", "dd-mmm-yy")
                ylabel(graph_label)
                if strcmp(ranges_to_printlay[hrd], "RF"):
                    title("reference 499.684MHz")

                ck = ck + 1

    if "fill_pattern" in requested_data[1]:
        axfp = nexttile(t)
        for hkw in range(1, len(requested_data)):
            plot[1:harmonic_number, requested_data[hkw]["fill_pattern"], "b"]

        ylim([0, inf])
        xlim([1, harmonic_number])
        set(axfp, "XTick", [])
        title("Fill pattern variation")
        ylabel("Charge (nC)")

    # add labels if it is a parameter sweep['']
    if nargin == 4 and experimental_setup["anal_type"] == "parameter_sweep":
        for tb in range(len(experimental_setup["param"], -1, 1)):
            labels[tb] = experimental_setup["param"](tb)

        legend(labels)

    return fig


def mbf_checkout_archival_retrieval(
    ax,
    date_range,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    current_range=[0, 300],
):
    # Extracts requested data from the data archive between
    # the requested times(date_range), and of the correct type (ax)['']
    # also filters out datasets with machine settings outside the specified
    # acceptable range['']
    #
    # Args:
    #       ax (str): The number of the axis (x, y, s)
    #       date_range (pair of datetime instances): The range of time to extract['']
    #       bypass_index (str) : 'no' for use the pregnerated index (much faster)
    #                            'yes' for work things out from the file metatdata['']
    #                            the default is 'no'['']
    #       metadata_only(str): 'no' return all data
    #                            'yes' remove the sample data from the output structure['']
    #                            the default is 'no'['']
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
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures['']
    #
    # Example: mbf_checkout_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])
    [root_string, _3, _2, _1] = system_config
    [filter_names, _1] = dir_list_gen(root_string, "", 1)
    filter_names = filter_names(f"DL_checkout_{ax}" in filter_names)
    filter_names = regexprep(filter_names, "_index.mat", "")
    requested_data = []
    for nfe in range(1, len(filter_names)):
        requested_data[nfe] = archival_dataset_retrieval(
            filter_names[nfe],
            date_range,
            "bypass_index",
            bypass_index,
            "metadata_only",
            metadata_only,
        )
    return requested_data
