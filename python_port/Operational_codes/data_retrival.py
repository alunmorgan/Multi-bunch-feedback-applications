import csv
import datetime
import os
from types import FunctionType

import numpy as np
import scipy
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

from Common import dir_list_gen, dir_list_gen_tree, reconfigure_to_lists, system_config


def archival_retrieval(
    selection: str,
    ax: str,
    date_range: list[datetime.datetime, datetime.datetime],
    measurement_specific_options: dict,
    analysis_function: FunctionType,
    plotting_function: FunctionType,
    plotting_summary_function: FunctionType,
    filter_conditions,
    bypass_index: bool,
    metadata_only: bool,
    analysis_type: str,
    sweep_parameter: str,
    parameter_step: float,
    debug: bool,
):
    """Extracts requested data from the data archive between
    the requested times(date_range), and of the correct type (ax).
    also filters out datasets with machine settings outside the specified
    acceptable range.

    Args:
          ax: The number of the axis (x, y, s)
          date_range: The range of time to extract.
          bypass_index: 'no' for use the pregnerated index (much faster)
                               'yes' for work things out from the file metatdata.
                               the default is 'no'.
          metadata_only: 'no' return all data
                               'yes' remove the sample data from the output structure.
                               the default is 'no'.
          analysis_type: determines the type of analysis to run 'collate' or
                              'sweep', the default is 'collate'.
          sweep_parameter: Parameter to be used. This name must exist
                                 in the data structure. (only needed if
                                 anal_type set to 'parameter sweep')
          parameter_step_size: Defines the spacing of the steps in
                                       the parameter sweep.
                                       Multiple data sets which are on the same
                                       step will be averaged. (only needed if
                                       anal_type set to 'parameter sweep')
          overrides: Two values setting the number of turns to
                                       analyse (passive, active)
          debug: if 1 then outputs graphs of individual modes to allow
                                       selection nof appropriate overrides.


    Example: growdamp_archival_retrieval('x',
             [datetime(2023, 1, 1), datetime("now")])
    """
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
        # Only keeping datasets that satify the requested machine conditions.
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


def retrieve_single_axis_data(
    retrieval_function: FunctionType, mbf_axis: str, timestamp: datetime.datetime
):
    dataset, times, setup = retrieval_function(
        mbf_axis, [timestamp, timestamp], filter_conditions=[]
    )
    return dataset


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
    extents: dict = {}
    data = reconfigure_to_lists(input_data)
    data_field_names = data.keys()
    for field_name in data_field_names:
        if field_name == "time" or (
            data[field_name] is float | int and len(data[field_name]) == 1
        ):
            extents[field_name][0] = max(data[field_name])
            extents[field_name][1] = min(data[field_name])

    return extents


def archive_retreval_investigate_metadata(requested_data: list[dict]) -> list[list]:

    for nfe in range(1, len(requested_data)):
        temp = requested_data[nfe].keys()
        if nfe == 1:
            fields = temp
        else:
            fields = list(set(fields).intersection(set(temp)))

    # remove the fields which are not useful to compare.
    not_to_compare: list[str] = ["ax_label", "filename", "data", "time"]
    fields = [item for item in fields if item not in not_to_compare]

    metadata = []
    for hse in range(len(fields)):
        for wak in range(len(requested_data)):
            metadata[hse][wak] = requested_data[wak][fields[hse]]
    return metadata


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


def archival_conditional_filtering(
    requested_data: list[dict], selections: dict
) -> list[dict]:
    """returns the sets of data which have metadata values below thoise given in
    selections

      Args:
          input_data
          selections: fields match those in the metadata
                      value is the value to be below.
      Returns:
          sets: Datasets which matched the criteria.

    Example conditioned_data = archival_conditional_filtering(requested_data)
    """
    data = reconfigure_to_lists(requested_data)
    indicies_to_remove: list = []
    for selection in selections.key():
        indicies_to_remove.extend(
            [
                index
                for index, item in enumerate(data[selection])
                if item > selections[selection]
            ]
        )
    # reverse sorting to not mess up the indexing when using pop.
    indicies_to_remove = list(set(indicies_to_remove)).sort(reverse=True)
    for ind in indicies_to_remove:
        requested_data.pop(ind)

    return requested_data


def archival_dataset_retrieval(
    filter_name: str,
    date_range: list,
    bypass_index: bool = "no",
    metadata_only: bool = "no",
) -> list[dict]:
    """Extracts requested data from the data archive between
    the requested times(date_range), and of the correct type (ax).

    Args:
          filter_name: Name of the file to select for.

          date_range: The range of time to extract.
          bypass_index: 'no' for use the pregnerated index (much faster)
                        'yes' for work things out from the file metatdata.

    Returns:
          unpacked_data: The group of requested data structures.

    Example: archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])
    """
    # Getting the desired system setup parameters.
    root_string, _2, _1 = system_config()
    index_name = [filter_name, "_index"]
    data = []
    if bypass_index == "no":
        with open(os.path.join(root_string, index_name), "r", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                data.append(row)

        file_index = test
        # capture_times = cellfun(@datetime, file_index[2,:]) #FIXME
        a = find(capture_times >= date_range[0])
        b = find(capture_times <= date_range[1])
        wanted_datasets = file_index(1, (list(set(a).intersection(set(b)))))
        print("")
    else:
        print(
            """Bypassing index. This will be slower but is useful if the index is 
            damaged and cannot be imediately regenerated"""
        )
        prefiltered_datasets = []
        datasets = dir_list_gen_tree(root_string, ".mat")
        # Prefiltering on folder structure so that the code stays fast as more data
        # is added to the data store.
        for dataset in datasets:
            h1, fname = os.path.split(dataset)
            h2, day = os.path.split(h1)
            h3, month = os.path.split(h2)
            _1, year = os.path.split(h3)
            file_date = datetime.datetime(year, month, day)
            if (
                filter_name in fname
                and file_date >= date_range[0]
                and file_date <= date_range[1]
            ):
                prefiltered_datasets.append(dataset)
        wanted_data = []
        for data_name in prefiltered_datasets:
            temp_data = scipy.loadmat(data_name)
            if (
                temp_data["time"] >= date_range[0]
                and temp_data["time"] <= date_range[1]
            ):
                wanted_data.append(data_name)

    requested_data = []
    for jes in range(len(wanted_datasets)):
        try:
            temp = scipy.loadmat(wanted_datasets[jes])
        except:
            _1, corrupt_file = os.path.split(wanted_datasets[jes])
            print(f"skipping corrupt, file({corrupt_file})")
            continue
        if metadata_only == "yes":
            temp.pop("data")

        requested_data[jes] = temp
    return requested_data


def mbf_checkout_archival_retrieval(
    ax: str,
    date_range: list,
    bypass_index: bool = "no",
    metadata_only: bool = "no",
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    current_range: list[float] = [0, 300],
) -> list[dict]:
    """Extracts requested data from the data archive between
    the requested times(date_range), and of the correct type (ax).
    also filters out datasets with machine settings outside the specified
    acceptable range.

    Args:
          ax: The number of the axis (x, y, s)
          date_range: The range of time to extract.
          bypass_index: 'no' for use the pregnerated index (much faster)
                               'yes' for work things out from the file metatdata.
          metadata_only: 'no' return all data
                         'yes' remove the sample data from the output structure.
          sweep_parameter: Parameter to be used. This name must exist
                                 in the data structure. (only needed if
                                 anal_type set to 'parameter sweep')
          parameter_step_size: Defines the spacing of the steps in the parameter sweep.
                                       Multiple data sets which are on the same
                                       step will be averaged. (only needed if
                                       anal_type set to 'parameter sweep')

    Returns:
          conditioned_data: The group of requested data structures.

    Example: mbf_checkout_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])
    """
    root_string, _3, _2, _1 = system_config()
    filter_names = dir_list_gen(root_string, "", 1)
    filter_names = filter_names(f"DL_checkout_{ax}" in filter_names)
    filter_names = regexprep(filter_names, "_index.mat", "")
    requested_data = []
    for nfe in range(len(filter_names)):
        requested_data[nfe] = archival_dataset_retrieval(
            filter_names[nfe],
            date_range,
            "bypass_index",
            bypass_index,
            "metadata_only",
            metadata_only,
        )
    return requested_data


def frontend_lo_phase_scan_retrival():
    pass


def pll_pi_scan_retrival():
    pass
