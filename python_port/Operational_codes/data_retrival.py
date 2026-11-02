import numpy as np

from Common import (
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
)


def mbf_growthrates_archival_retrieval(
    ax,
    date_range,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    overrides=(None, None),
    advanced_fitting=0,
    current_range=(2, 150),
    debug=0,
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
    # Example: mbf_growdamp_archival_retrieval('x',
    #         [datetime(2023, 1, 1), datetime("now")])
    if ax.lower() == "x":
        filter_name = "Growthrates_x_axis"
    elif ax.lower() == "y":
        filter_name = "Growthrates_y_axis"
    elif ax.lower() == "s":
        filter_name = "Growthrates_s_axis"
    else:
        raise ValueError(
            "MBF:Archive:InputError mbf_archival_dataset_retrieval: "
            "No valid axis given (should be x, y or s)"
        )

    requested_data = mbf_archival_dataset_retrieval(
        filter_name, date_range, bypass_index=bypass_index, metadata_only=metadata_only
    )
    # Only keeping datasets that satify the requested machine conditions['']
    conditioned_data = mbf_archival_conditional_filtering(
        requested_data, current_range=current_range
    )
    if not conditioned_data:
        print("No data meeting the requirements")
    else:
        if analysis_type == "collate":
            [dr_growth, dr_active, error_growth, error_active, times, setup] = (
                mbf_growthrates_archival_analysis(
                    conditioned_data,
                    analysis_type="collate",
                    overrides=overrides,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            )
        elif analysis_type == "sweep":
            [dr_growth, dr_active, error_growth, error_active, times, setup] = (
                mbf_growthrates_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                    overrides=overrides,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            )
        else:
            raise ValueError(
                "MBF:Archive:InputError Please select collate or sweep "
                "as the analysis type"
            )

        setup["axis"] = ax
        mbf_growthrates_archival_plotting(
            conditioned_data,
            dr_growth,
            dr_active,
            error_growth,
            error_active,
            times,
            setup,
        )
        return conditioned_data


def growdamp_archive_calculate_extents(input_data):
    extents = {}
    for ke in range(len(input_data)):
        data_field_names = input_data[ke].keys()
        for haw in range(1, len(data_field_names)):
            if ~data_field_names[haw] in extents:
                # initialisation
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][1] = input_data[ke][
                        data_field_names[haw]
                    ]
                    extents[data_field_names[haw]][2] = input_data[ke][
                        data_field_names[haw]
                    ]
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][1] = input_data[ke][
                            data_field_names[haw]
                        ]
                        extents[data_field_names[haw]][2] = input_data[ke][
                            data_field_names[haw]
                        ]
            else:
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][1] = max(
                        [
                            extents[data_field_names[haw]][1],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                    extents[data_field_names[haw]][2] = min(
                        [
                            extents[data_field_names[haw]][2],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][1] = max(
                            [
                                extents[data_field_names[haw]][1],
                                input_data[ke][data_field_names[haw]],
                            ]
                        )
                        extents[data_field_names[haw]][2] = min(
                            [
                                extents[data_field_names[haw]][2],
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


def mbf_growdamp_archival_retrieval(
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
    # Example: mbf_growdamp_archival_retrieval('x',
    #          [datetime(2023, 1, 1), datetime("now")])
    selection_name = ["Growdamp_", ax, "_axis"]
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        [dataset, _2, _1] = mbf_growdamp_archival_analysis(
            requested_data,
            analysis_type="collate",
            active_override=active_override,
            passive_override=passive_override,
            advanced_fitting=advanced_fitting,
            debug=debug,
        )
        mbf_growdamp_plot_summary(dataset, requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [dataset, times, setup] = mbf_growdamp_archival_analysis(
                    conditioned_data,
                    analysis_type="collate",
                    active_override=active_override,
                    passive_override=passive_override,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            elif analysis_type == "sweep":
                [dataset, times, setup] = mbf_growdamp_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                    active_override=active_override,
                    passive_override=passive_override,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )

            setup["axis"] = ax
            mbf_growdamp_archival_plotting(conditioned_data, dataset, times, setup)

    return dataset, times, setup


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


def mbf_frontend_clock_phase_scan_archival_retrieval(
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
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                              structures.
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #                  [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"clock_phase_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_clock_phase_scan_plotting(requested_data[1])
    else:
        conditioned_data = mbf_archival_conditional_filtering(requested_data)
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_clock_phase_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_clock_phase_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )

            setup["axis"] = ax
            mbf_frontend_clock_phase_scan_archival_plotting(
                conditioned_data, leading, excited, following, times, setup
            )

    return conditioned_data


def mbf_frontend_gain_scan_archival_retrieval(
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
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures.
    #
    # Example: mbf_frontend_gain_scan_archival_retrieval('x',
    #                          [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"frontend_gain_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_gain_scan_plotting(requested_data[1])
    else:
        conditioned_data = mbf_archival_conditional_filtering(requested_data)
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [adc_mean, adc_max, adc_min, times, setup] = (
                    mbf_frontend_gain_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [adc_mean, adc_max, adc_min, times, setup] = (
                    mbf_frontend_gain_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )

            setup["axis"] = ax
            mbf_frontend_gain_scan_archival_plotting(
                conditioned_data, adc_mean, adc_max, adc_min, times, setup
            )

    return conditioned_data


def mbf_frontend_system_phase_scan_archival_retrieval(
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
    selection_name = f"system_phase_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_system_phase_scan_plotting(requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions.
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_system_phase_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_system_phase_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )
            else:
                raise ValueError(
                    "archivalDatasetRetrieval:InputError "
                    "Please select collate or sweep as the analysis type"
                )

            setup["axis"] = ax
            mbf_frontend_system_phase_scan_archival_plotting(
                conditioned_data, leading, excited, following, times, setup
            )


def mbf_tunescan_over_modes_archival_retrieval(
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
    # Example: mbf_tunescan_over_modes_archival_retrieval('x',
    #                       [datetime(2023, 1, 1), datetime("now")])

    selection_name = ["tunescan_", ax, "_axis"]
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        #     [dataset,  _2 ,  _1 ] =
        #         mbf_tunescan_over_modes_archival_analysis(requested_data)
        mbf_tunescan_over_modes_plot_summary(requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                pass
                #             [dataset, times, setup] =
                #           mbf_tunescan_over_modes_archival_analysis(conditioned_data)
            elif analysis_type == "sweep":
                pass
                #             [dataset, times, setup] =
                #           mbf_tunescan_over_modes_archival_analysis(conditioned_data)

            #         setup['axis'] = ax
            #         mbf_tunescan_over_modes_archival_plotting(conditioned_data,
            #                      dataset, times, setup)

    return dataset, times, experimental_setup
