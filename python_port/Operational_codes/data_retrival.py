from analysis import (
    mbf_bunch_motion_archival_analysis,
    mbf_frontend_clock_phase_scan_archival_analysis,
    mbf_frontend_gain_scan_archival_analysis,
    mbf_frontend_system_phase_scan_archival_analysis,
    mbf_growdamp_archival_analysis,
    mbf_growthrates_archival_analysis,
    mbf_modescan_archival_analysis,
    mbf_spectra_archival_analysis,
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
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
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

    requested_data = mbf_archival_dataset_retrieval(
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
        conditioned_data = mbf_archival_conditional_filtering(
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
        analysis_function=mbf_growdamp_archival_analysis,
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
        analysis_function=mbf_growthrates_archival_analysis,
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
        analysis_function=mbf_modescan_archival_analysis,
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
        analysis_function=mbf_spectra_archival_analysis,
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
        analysis_function=mbf_bunch_motion_archival_analysis,
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
        analysis_function=mbf_frontend_clock_phase_scan_archival_analysis,
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
        analysis_function=mbf_frontend_gain_scan_archival_analysis,
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
        analysis_function=mbf_frontend_system_phase_scan_archival_analysis,
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
