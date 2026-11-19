import csv
import datetime
import os
import time

import numpy as np
import scipy
from cothread.catools import FORMAT_TIME, caget, caput  # type: ignore
from system_configuration import system_config


def hannwin(data: np.ndarray, dim: int = 0) -> np.ndarray:
    window = np.hanning(data.shape[dim])
    s = list(data.shape)
    s[dim] = 1
    data_windowed = data * np.matlib.repmat(window, s[0], s[1])
    return data_windowed


def movmean(data: list, window_size: int) -> list:
    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []

    # Loop through the array to consider every window.
    while i < len(data) - window_size + 1:
        # Calculate the average of current window
        window_average = sum(data[i : i + window_size]) / window_size

        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)

        # Shift window to right by one position
        i += 1
    return moving_averages


def reconfigure_to_lists(input_data: list[dict]) -> dict:
    """Change from a list of dictionaries to a dictionary of lists."""
    out: dict = {}
    data_field_names = input_data[0].keys()
    for field_name in data_field_names:
        out[field_name] = []
        for ke in range(len(input_data)):
            out[field_name].append(input_data[ke][field_name])

    return out


def generate_sweep(sweep_start: float, sweep_end: float, sweep_step: float):
    """Generate a sweep from start to end and back again."""
    sweep_vals = list(np.arange(sweep_start, sweep_end, sweep_step))
    sweep_vals.extend(
        list(
            np.arange(
                sweep_end - sweep_step,
                sweep_start,
                -sweep_step,
            )
        )
    )
    return sweep_vals


def slew_to_value(existing_value, target_value, step, pv):
    for pp in range(
        existing_value,
        target_value,
        step,
    ):
        set_variable(pv, pp)
        time.sleep(0.5)


def cat_multi_dim(
    cat_dim: int, original_data: np.ndarray, new_data: np.ndarray
) -> np.ndarray:
    """concatinates multi-dimensional data in the cat_dim dimension,
    pads the other dimensions as necessary.
    will return the combined matrix.

    example: combined_data = cat_multi_dim(cat_dim,original_data, new_data)
    """
    ## Padding the arrays to make them the same size in all dimensions
    original_data_size = original_data.shape
    new_data_size = new_data.shape
    # find max in each dimension
    max_size = np.max(np.array([original_data_size, new_data_size]), axis=0)
    padding_original = max_size - original_data_size
    padding_new = max_size - new_data_size
    # do not pad in cat_dim
    padding_original[cat_dim] = 0
    padding_new[cat_dim] = 0

    padded_original = np.pad(
        original_data,
        ((0, padding_original[0]), (0, padding_original[1]), (0, padding_original[2])),
        constant_values=np.nan,
    )
    padded_new = np.pad(
        original_data,
        ((0, padding_new[0]), (0, padding_new[1]), (0, padding_new[2])),
        constant_values=np.nan,
    )

    combined_data = np.concatenate((padded_original, padded_new), axis=cat_dim)
    return combined_data


def construct_datastamped_filename(name_str: str, c: datetime.datetime) -> str:
    """constructs a datestamped filename
    name_str is a identifier string added at the begining of the name.
    c is a datetime object.

    example filename = construct_filename('MBF', clock)
    """
    filename = f"""{name_str}_{c.day: 02d}_{c.month:02d}_{c.year}_{c.hour: 02d}-
        {c.minute: 02d}-{c.second: 02d}"""

    return filename


def dir_list_gen(directory_name: str, file_type: str) -> tuple[list[str], str]:
    """takes in a directory name and outputs the list of files filtered by file type.
    if a file type of 'dirs' is input it will output a list of directories.
    example
    names,directory_name = dir_list_gen('/home','mat')
    """
    names = []
    dirs = []
    with os.scandir(directory_name) as it:
        for entry in it:
            if not entry.name.endswith(file_type) and entry.is_file():
                names.append(entry.name)
            elif entry.is_dir():
                dirs.append(entry.name)

    if file_type == "dirs":
        names = dirs

    return names, directory_name


def dir_list_gen_tree(root_dir: str, filetype: str):
    """finds files of the requested type in current folder and all subfolders
    ignores hidden folders
    the absolute paths are returned.

    Example: [a dir_paths] =dir_list_gen_tree(root_dir, 'png')
    """
    paths = []
    for entry in os.listdir(root_dir):
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path):
            paths.extend(dir_list_gen_tree(full_path, filetype=filetype))
        else:
            head, tail = os.path.split(full_path)
            if filetype in tail:
                paths.append(full_path)

    return paths


def get_variable(variable_names, system_type="EPICS", timeout=5, datatype=None):
    """function to get a set of variables.
    This abstraction allows easier porting:
     between EPICS and TANGO (and potentially others).
    """
    if system_type.upper() == "EPICS":
        values = caget(
            variable_names, timeout=timeout, datatype=datatype, format=FORMAT_TIME
        )
        timestamps = []
        for value in values:
            timestamps.append(value.datetime)

    elif system_type.upper() == "TANGO":
        raise ValueError(
            "getVariable:systemTypeError Tango calls are not yet implemented"
        )
    else:
        raise ValueError(
            "getVariable:systemTypeError "
            "alternative sytem calls are not yet implemented",
        )

    return values, timestamps


def mode_to_frequency(RF, harmonic_number, tune, data):
    """converts a mode scan into the equivalent frequencies."""
    x_data_p1 = (RF / harmonic_number) * (range(harmonic_number / 2) + tune)
    x_data_p2 = RF - (RF / harmonic_number) * (
        range((harmonic_number / 2), (harmonic_number)) + tune
    )
    x_data = np.cat(2, x_data_p1, x_data_p2)
    x_data, ind = np.sort(x_data)
    data = data[ind]
    return x_data, data


def save_to_archive(root_string, data):
    """Saves the requested variables in the given filename in a location
    detemined by the time_value.
    The relavent folder structure will be generated.

    Example: save_to_archive(root_string, what_to_save)
    """
    # Generating the required directory structure.
    tree_gen(root_string, data["time"])
    # construct filename and add it to the structure
    data["filename"] = construct_datastamped_filename(data["base_name"], data["time"])
    save_name = os.path.join(
        root_string,
        data["time"].yr,
        f"{data['time'].mth: 02d}",
        f"{data['time'].dy: 02d}",
        f"{data['filename']}.mat",
    )
    scipy.savemat(save_name, "data", "-v7.3")
    print(["Data saved to: , ", save_name])
    update_index(data, root_string, save_name)


def set_variable(variable_names, variable_values, system_type="EPICS"):
    """function to set a group of variables[''] This abstraction allows easier porting:
    # between EPICS and TANGO (and potentially others)."""

    if system_type.upper() == "EPICS":
        caput(variable_names, variable_values)
    elif system_type.upper() == "TANGO":
        raise ValueError(
            "setVariable:systemTypeErrorTango calls are not yet implemented"
        )
    else:
        raise ValueError(
            "setVariable:systemTypeError",
            "alternative sytem calls are not yet implemented",
        )


def sub_directories(main_dir: str) -> list[str]:
    """outputs a list of sub-directories of the input directory

    example: sub_dir = sub_directories(main_dir)
    """
    # finding the subdirectories
    sub_dirs = [str(entry) for entry in os.scandir(main_dir) if entry.is_dir()]

    return sub_dirs


def tree_gen(tree_root: os.PathLike[str], clk: datetime.datetime):
    """generates a directory structure using the datetime passed in as clk
    tree_root is where you want the subdirectories to be placed."""

    leaf = os.path.join(tree_root, f"{clk.year}", f"{clk.month: 02d}", f"{clk.day:02d}")

    # generating directory tree
    if not os.path.isdir(leaf):
        os.makedirs(leaf)


def update_index(data: dict, root_string: str, save_name: str) -> None:
    index_name = f"{data['base_name']}_index"
    timestamp = data["time"].strftime("%a %d %b %Y, %I:%M%p")
    location = os.path.join(root_string, f"{index_name}.csv")
    if not os.path.isfile(location):
        os.makedirs(location)
        print("New index file created")

    with open(
        os.path.join(root_string, f"{index_name}.csv"), "a", newline=""
    ) as csvfile:
        fw = csv.writer(csvfile, delimiter=",")
        fw.writerows([save_name, timestamp])


def mbf_make_index(application_type: str, ax: str | None):
    """Writes index files to speed up archive retrival def s:
    Args:
          application_type: either 'Growdamp', 'Bunch_motion', 'Modescan',
                              'Spectrum', 'LO_scan', 'system_phase_scan',
                              'clock_phase_scan'.
          ax: 'x', 'y', or 's'

    Example mbf_make_index('Growdamp', 'x')
    """
    root_string, _2, _1 = system_config()
    if ax:
        filter_name = f"{application_type}_{ax}_axis"
    else:
        filter_name = f"{application_type}"

    datasets = dir_list_gen_tree(root_string, ".mat")
    wanted_datasets = [item for item in datasets if filter_name in item]

    print(f"Creating lookup index for {application_type} {ax}")
    if not wanted_datasets:
        print("No files to index")
    else:
        for dataset in wanted_datasets:
            data = scipy.io.loadmat(dataset)
            update_index(data, root_string, dataset)


def update_all_indexes():
    """updates all indexes in the data archive
    useful if something is corrupted."""
    mbf_make_index("LO_scan")
    mbf_make_index("clock_phase_scan")
    mbf_make_index("system_phase_scan")
    mbf_make_index("Bunch_motion")
    mbf_make_index("Spectrum", "x")
    mbf_make_index("Spectrum", "y")
    mbf_make_index("Spectrum", "s")
    mbf_make_index("Growdamp", "x")
    mbf_make_index("Growdamp", "y")
    mbf_make_index("Growdamp", "s")
    mbf_make_index("fll_phase_scan", "x")
    mbf_make_index("fll_phase_scan", "y")
    mbf_make_index("Modescan", "x")
    mbf_make_index("Modescan", "y")
    mbf_make_index("Modescan", "s")
    mbf_make_index("tunescan", "x")
    mbf_make_index("tunescan", "y")
    mbf_make_index("tunescan", "s")
