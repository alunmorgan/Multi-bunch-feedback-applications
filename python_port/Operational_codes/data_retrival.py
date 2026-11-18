import csv
import datetime
import os

import numpy as np
import scipy

from Common import dir_list_gen, dir_list_gen_tree, reconfigure_to_lists, system_config


def archival_retrieval(
    selection: str,
    ax: str,
    date_range: list[datetime.datetime, datetime.datetime],
    filter_conditions,
    bypass_index: bool,
    metadata_only: bool,
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

    Example: growdamp_archival_retrieval('x',
             [datetime(2023, 1, 1), datetime("now")])
    """
    if ax:
        selection_name = f"{selection}_{ax}_axis"
    else:
        selection_name = selection

    requested_data = archival_retrieval_dataset(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )

    # Only keeping datasets that satify the requested machine conditions.
    conditioned_data = archival_conditional_filtering(requested_data, filter_conditions)
    if not conditioned_data:
        print("No data meeting the requirements")
        return None
    else:
        return conditioned_data


def get_wanted_datasets_from_index(index_file_path, date_range) -> list[str]:
    wanted_datasets = []
    with open(index_file_path, "r", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            sample_time = datetime.date.strptime(row[1], "%a %d %b %Y, %I:%M%p")
            if sample_time >= date_range[0] and sample_time <= date_range[1]:
                wanted_datasets.append(row[0])
    return wanted_datasets


def get_wanted_datasets_from_files(root_location, filter_name, date_range) -> list[str]:
    prefiltered_datasets = []
    wanted_datasets = []
    datasets = dir_list_gen_tree(root_location, ".mat")
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

    for data_name in prefiltered_datasets:
        temp_data = scipy.loadmat(data_name)
        if temp_data["time"] >= date_range[0] and temp_data["time"] <= date_range[1]:
            wanted_datasets.append(data_name)
    return wanted_datasets


def archival_retrieval_dataset(
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

    requested_data = []
    if bypass_index == "no":
        index_file_path = os.path.join(root_string, f"{filter_name}_index")
        wanted_datasets = get_wanted_datasets_from_index(
            index_file_path=index_file_path, date_range=date_range
        )
    else:
        print(
            """Bypassing index. This will be slower but is useful if the index is
            damaged and cannot be imediately regenerated"""
        )
        wanted_datasets = get_wanted_datasets_from_files(
            root_location=root_string, date_range=date_range
        )

    for jes in range(len(wanted_datasets)):
        try:
            temp = scipy.loadmat(wanted_datasets[jes])
        except IOError:
            _1, corrupt_file = os.path.split(wanted_datasets[jes])
            print(f"skipping corrupt, file({corrupt_file})")
            continue

        if metadata_only == "yes":
            temp.pop("data")

        requested_data.append(temp)

    return requested_data


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


def archival_extraction_pll_phase_scan(
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

    requested_data = archival_retrieval_dataset(
        filter_name, date_range, "bypass_index", "no"
    )
    # some data had many NaN collumns - this is to remove them.
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
    plotting_pll_phase_scan_multi(requested_data, "scan_type", scan_type)
    return requested_data


def archival_conditional_filtering(
    requested_data: list[dict], selections: dict
) -> list[dict]:
    """returns the sets of data which have metadata values below those given in
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


def archival_retrieval_checkout(
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

    Example: mbf_checkout_archival_retrieval('x',
                           [datetime(2023, 1, 1), datetime("now")])
    """
    root_string, _3, _2, _1 = system_config()
    filter_names = dir_list_gen(root_string, "", 1)
    filter_names = filter_names(f"DL_checkout_{ax}" in filter_names)
    filter_names = filter_names.replace("_index.mat", "")
    requested_data = []
    for nfe in range(len(filter_names)):
        requested_data[nfe] = archival_retrieval_dataset(
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
