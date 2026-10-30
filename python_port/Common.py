import datetime
import os

import numpy as np
import scipy


def movmean(data, window_size):
    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []

    # Loop through the array to consider every window.
    while i < len(data) - window_size + 1:
        # Calculate the average of current window
        window_average = np.sum(data[i : i + window_size]) / window_size

        # Store the average of current
        # window in moving average list
        moving_averages.append(window_average)

        # Shift window to right by one position
        i += 1
        return moving_averages


def archive_graphs(root_string, metadata, graph_handles=()):
    # Saves the requested graphs in the given filename in a location
    # detemined by the time_value['']
    # The relavent folder structure will be generated['']
    #
    #   Args:
    #       root_string (str):
    #       data (struct): original captured meta data
    #       graph_handles
    # Example: archive_graphs(root_string, data, graph_handles)
    # Generating the required directory structure['']
    tree_gen(root_string, metadata["time"])
    # construct filename and add it to the structure
    metadata["filename"] = construct_datastamped_filename(
        metadata["base_name"], metadata["time"]
    )
    mth = metadata["time"](2)
    dy = metadata["time"](3)
    if mth < 10:
        mth = "0" + (mth)

    if dy < 10:
        dy = "0" + (dy)

    for heaq in range(1, len(graph_handles)):
        if ishandle(graph_handles(heaq)):
            graph_save_name = os.path.join(
                root_string, (metadata["time"][1]), mth, dy, metadata["filename"]
            )
            plt.savefig(
                graph_handles(heaq), f"{graph_save_name}, _figure_, {heaq}, .png]"
            )
            plt.savefig(
                graph_handles(heaq), f"{graph_save_name}, _figure_, {heaq}, .fig"
            )


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


def cat_multi_dim(cat_dim: int, original_data, new_data):
    # concatinates multi-dimensional data in the cat_dim dimension,
    # pads the other dimensions as necessary.
    # If given 1 output will give the combined matrix.
    # If given 2 outputs will output the padded components
    # example
    # varargout = cat_multi_dim(cat_dim,original_data, new_data)
    pad_dims = [0, 1, 2, 3]
    pad_dims[pad_dims == cat_dim] = []
    ## Padding the arrays to make them the same size in all dimensions
    sizes = []
    for n in range(4):
        if new_data.shape[pad_dims[n]] > original_data.shape[pad_dims[n]]:
            if pad_dims[n] == 0:
                sizes[n] = new_data.shape[n] - original_data.shape[n]
                if sizes[n] == 0:
                    sizes[n] = 1
            else:
                sizes[n] = original_data.shape[n]

            od_padding = NaN(sizes[0], sizes[1], sizes[2], sizes[3])
            # If the data is a character array, converting the
            # NaN padding matrix into an array of spaces to stop
            # the warning messages['']
            if ischar(original_data) == 1:
                od_padding[isnan(od_padding)] = " "
                od_padding = char(od_padding)

            original_data = cat(pad_dims[n], original_data, od_padding)

        if new_data.shape[pad_dims[n]] < original_data.shape[pad_dims[n]]:
            if pad_dims[n] == 0:
                sizes[n] = original_data.shape[n] - new_data.shape[n]
                if sizes[n] == 0:
                    sizes[n] = 1
            else:
                sizes[n] = new_data.shape[n]

            nd_padding = NaN(sizes[0], sizes[1], sizes[2], sizes[3])
            # If the data is a character array, converting the
            # NaN padding matrix into an array of spaces to stop
            # the warning messages['']
            if ischar(new_data) == 1:
                nd_padding[isnan(nd_padding)] = " "
                nd_padding = char(nd_padding)

            new_data = cat(pad_dims[n], new_data, nd_padding)

    ## Combining the padded arrays
    combined_data = cat(cat_dim, original_data, new_data)
    if nargout == 1:
        varargout = [combined_data]
    elif nargout == 2:
        varargout = [original_data][new_data]

    return varargout


def condition_mbf_data(input_data):
    # Mapping values in old datasets to defined variables['']
    # Initialisation
    n_datasets = len(input_data)
    output_data = input_data
    for jgr in range[n_datasets:-1, 1]:
        if "data" in input_data[jgr]:
            continue

        if "gddata" in input_data[jgr]:
            output_data[jgr]["data"] = input_data[jgr]["gddata"]

        if "gddata_freq" in input_data[jgr]:
            output_data[jgr]["data_freq"] = input_data[jgr]["gddata_freq"]

    return output_data


def condition_mbf_metadata(input_data):
    # Mapping values in old datasets to defined variables['']
    # Initialisation
    n_datasets = len(input_data)
    output_data = input_data
    for jgr in range[n_datasets:-1, 1]:
        if "I_bpm" in input_data[jgr]:
            output_data[jgr]["current"] = input_data[jgr]["I_bpm"]

        if "I_dcct5" in input_data[jgr]:
            output_data[jgr]["current"] = input_data[jgr]["I_dcct5"]

        if "fill" in input_data[jgr]:
            output_data[jgr]["fill_pattern"] = input_data[jgr]["fill"]

        if "RFread" in input_data[jgr]:
            output_data[jgr]["cavity1_voltage"] = input_data[jgr]["RFread"](1)
            output_data[jgr]["cavity2_voltage"] = input_data[jgr]["RFread"](2)

        if "life" in input_data[jgr] and "bpm" in input_data[jgr]["life"]:
            output_data[jgr]["beam_lifetime"] = input_data[jgr]["life"]["bpm"][
                "life300sec"
            ]

        if "id" in input_data[jgr]:
            output_data[jgr]["wiggler_field_I12"] = input_data[jgr]["id"]["i12field"]
            output_data[jgr]["wiggler_field_I15"] = input_data[jgr]["id"]["i15field"]

        if "qy" in input_data[jgr]:
            output_data[jgr]["tune"] = input_data[jgr]["qy"]

        if "qx" in input_data[jgr]:
            output_data[jgr]["tune"] = input_data[jgr]["qx"]

        if "tunes" in input_data[jgr]:
            output_data[jgr]["tune"] = input_data[jgr]["tunes"]

    return output_data


def construct_datastamped_filename(name_str, c):
    # constructs a datestamped filename
    # name_str is a identifier string added at the begining of the name['']
    # c is a time vector such as generated by the clock def ['']:
    #
    # example filename = construct_filename('MBF', clock)
    yr = c(1)
    mth = c(2)
    dy = c(3)
    hr = c(4)
    mn = c(5)
    sec = round(c(6))
    if c(2) < 10:
        mth = "0" + mth

    if c(3) < 10:
        dy = "0" + dy

    if c(4) < 10:
        hr = "0" + hr

    if c(5) < 10:
        mn = "0" + mn

    if c(6) < 10:
        sec = "0" + sec

    filename = f"{name_str}_{dy}_{mth}_{yr}_{hr}-{mn}-{sec}"
    return filename


def dir_list_gen(directory_name, file_type, quiet_flag=0):
    # takes in a directory name and outputs the list of files
    # as a cell array of strings filtered by file type['']
    # if a file type of 'dirs' is input it will output a list of directories['']
    # asks for a file if a name is not provided
    # the 3 input makes it quiet or verbose (1 = quiet) if not given assume
    # verbose['']
    # if 1 output given give absolute paths, if 2 are given outputs absolute
    # directory and a list of filenames['']
    # example
    # [names,directory_name]=dir_list_gen['U:\','mat',1]
    ## Input conditioning

    # removes leading . of file_type if present
    if not file_type and file_type(1) == ".":
        file_type = file_type[2:-1]

    # adding a trailing / to the directory name if running under linux
    # adding a trailing \ to the directory name if running under windows
    if os.name == "posix":
        if directory_name[-1] != "/":
            directory_name = [directory_name, "/"]
    else:
        if directory_name[-1] != "\\":
            directory_name = [directory_name, "\\"]

    a = os.listdir(directory_name)
    if not a:
        print("Directory does not exist")
        names = []
        directory_name = ""
        return

    dir_state = []
    names = a[1]["name"]
    dir_state[1, 1] = a[1]["isdir"]
    for fa in range(2, len(a)):
        names = cat_multi_dim(1, names, a[fa]["name"])
        dir_state[fa, 1] = a[fa]["isdir"]

    ## Formatting the output
    if nargout == 1:
        # making the file path absolute
        names = strcat(repmat(directory_name, names.shape[0], 1), names)
    elif nargout == 2:
        pass
    else:
        raise ValueError("dirlistgen:IOErrorWrong number of outputs (should be 1 or 2)")

    ## Finding the apropriate filetype in the list
    if file_type == "dirs":
        dirs = names[dir_state == 1]
        dot_ind = 0
        dot_dot_ind = 0
        for hd in range(1, len(dirs)):
            # remove the . and .. found on linux systems
            if dirs[hd] == ".":
                dot_ind = hd

            if dirs[hd] == "..":
                dot_dot_ind = hd

        if dot_ind != 0 and dot_dot_ind != 0:
            dirs[dot_ind, dot_dot_ind] = []
        elif dot_ind == 0 and dot_dot_ind != 0:
            dirs[dot_dot_ind] = []
        elif dot_ind != 0 and dot_dot_ind == 0:
            dirs[dot_ind] = []

        if not dirs:
            names = []
            if quiet_flag != 1:
                print("No directories found")

        else:
            names = dirs
            if quiet_flag != 1:
                print([(names.shape[0]), " directories found"])

    else:
        if not file_type:
            ind = regexpi(names, "[]$")
        else:
            ind = regexpi(names, [r"\[" "]", file_type, "$"])

        fk = 1
        ind2 = NaN(ind.shape[0])
        for kjsd in range(1, ind.shape[0]):
            if not cell2mat(ind(kjsd)) != 1:
                ind2[fk] = kjsd
                fk = fk + 1

        ind2[fk:-1] = []
        if fk == 1:
            if quiet_flag != 1:
                print(["No files with extension ", file_type, ", found"])

            names = []
        else:
            names = names(ind2)
            if quiet_flag != 1:
                print([(names.shape[0]), " files with extension ", file_type, " found"])

    return names, directory_name


def dir_list_gen_tree(root_dir, type, quiet):
    # finds files of the requested type in current folder and all subfolders
    # ignores hidden folders
    # if one output is given then the absolute paths are returned['']
    # if two output are given then the files names and directory paths are
    # returned separately['']
    #
    # Example: [a dir_paths] =dir_list_gen_tree(root_dir, 'png', 1)
    a = []
    dir_paths = []
    if nargin < 3:
        quiet = 0

    if root_dir[-1] == filesep and not root_dir[-2] == ":":
        root_dir = root_dir[1 : -1 - 1]

    # returns a list of files of the requested type in the current directory['']
    full_names = dir_list_gen(root_dir, type, "quiet_flag", quiet)
    # returns a list of directories in the current directory['']
    [sub_dir, _1] = dir_list_gen(root_dir, "dirs", "quiet_flag", quiet)
    if full_names != 1 and sub_dir != 1:
        return

    if sub_dir != 0:
        for sejh in range(1, len(sub_dir)):
            sub_dir_path = os.path.join(root_dir, sub_dir[sejh])
            # recursively call itself
            full_names_sub = dir_list_gen_tree(sub_dir_path, type, quiet)
            if full_names_sub != 0:
                if full_names != 0:
                    full_names = cat(1, full_names, full_names_sub)
                else:
                    full_names = full_names_sub

    if full_names != 1:
        return

    dir_paths = []
    f_names = []
    for pao in range(1, full_names.shape[0]):
        nmd = full_names[pao]
        ks = find(nmd == filesep, 1, "last")
        dir_paths[pao] = nmd[1:ks]
        f_names[pao] = nmd[ks + 1 : -1]

    if nargout == 1:
        # making the file path absolute
        a = full_names
    elif nargout == 2:
        a = f_names
    else:
        error("Wrong number of outputs (should be 1 or 2)")

    return a, dir_paths


def find_position_in_cell_lst(tmp):
    # returns the indicies of a cell array where the cell is not empty['']
    # will also work for a vector (yes/no)['']
    if iscell(tmp) == 0:
        if tmp != 0:
            sel = 1
        else:
            sel = []

    else:
        hsd = 1
        sel = NaN(len(tmp))
        for he in range(1, len(tmp)):
            if tmp[he] != 0:
                sel[hsd] = he
                hsd = hsd + 1

        sel[hsd:-1] = []
        if hsd == 1:
            sel = []


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

    requested_data = mbf_archival_dataset_retrieval(
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
    return sel


def get_all_tunes(axes="xys", n_trys=20):
    # captures the current tune on all MBF systems['']
    # if the value is NaN the code will try again for up to 20 tries['']
    #   Args:
    #       selected_axes(str): 'xys'
    #
    #   Returns:
    #       tunes(struct): tune and sideband values['']
    #
    # Example: tunes = get_all_tunes('xy')
    [_2, _1, pv_names] = mbf_system_config
    # Initialisation and ensuring the datastructure is consistent regardless of the
    # number of axes asked for['']
    tunes = {}
    tunes["x_tune"]["tune"] = None
    tunes["x_tune"]["lower_sideband"] = None
    tunes["x_tune"]["upper_sideband"] = None
    tunes["y_tune"]["tune"] = None
    tunes["y_tune"]["lower_sideband"] = None
    tunes["y_tune"]["upper_sideband"] = None
    tunes["s_tune"]["tune"] = None
    tunes["s_tune"]["lower_sideband"] = None
    tunes["s_tune"]["upper_sideband"] = None
    # Finding the current tunes for the requested axes['']
    for bds in range(1, len(axes)):
        temp_axis = axes[bds]
        ax_name = [temp_axis, "_tune"]
        for nfs in range(1, n_trys):
            try:
                tunes[ax_name]["tune"] = get_variable(
                    [
                        pv_names["hardware_names"][temp_axis],
                        pv_names["tails"]["tune"]["centre"],
                    ]
                )
            except ValueError:
                tunes[ax_name]["tune"] = None

            try:
                tunes[ax_name]["lower_sideband"] = get_variable(
                    [
                        pv_names["hardware_names"][temp_axis],
                        pv_names["tails"]["tune"]["left"],
                    ]
                )
            except ValueError:
                tunes[ax_name]["lower_sideband"] = None

            try:
                tunes[ax_name]["upper_sideband"] = get_variable(
                    [
                        pv_names["hardware_names"][temp_axis],
                        pv_names["tails"]["tune"]["right"],
                    ]
                )
            except ValueError:
                tunes[ax_name]["upper_sideband"] = None

            if nfs == n_trys and (tunes[ax_name]["tune"] == None):
                print(["Unable to get, ", temp_axis, " axis tune value"])
                continue

            if tunes[ax_name]["tune"] == None:
                sleep(0.3)

    return tunes


def get_operational_mode(mbf_axis):
    if mbf_axis == "x":
        state = get_variable["SR23C-DI-TMBF-01:X:BUN:MODE"]
    elif mbf_axis == "y":
        state = get_variable["SR23C-DI-TMBF-01:Y:BUN:MODE"]
    elif mbf_axis == "s":
        state = get_variable["SR23C-DI-LMBF-01:IQ:BUN:MODE"]
    else:
        raise ValueError("common:get_operational_mode", "Unexpected axis")

    if "Feedback on" in state:
        return_state = "Feedback"
    else:
        return_state = "TuneOnly"

    return return_state


def get_variable(variable_names, system_type="EPICS", nmax=None, datatype=None):
    # def to get a set of variables[''] This abstraction allows easier porting:
    # between EPICS and TANGO (and potentially others)
    if system_type.upper() == "EPICS":
        if nmax == None and datatype == None:
            [value, timestamp] = lcaGet(variable_names)
        elif nmax != None and datatype == None:
            [value, timestamp] = lcaGet(variable_names, nmax)
        elif nmax != None and datatype != None:
            [value, timestamp] = lcaGet(variable_names, nmax, datatype)
    elif system_type.upper() == "TANGO":
        error["getVariable:systemTypeError", "Tango calls are not yet implemented"]
    else:
        error[
            "getVariable:systemTypeError",
            "alternative sytem calls are not yet implemented",
        ]

    return value, timestamp


def hannwin(data, dim):
    s = data.shape
    if nargin < 2:
        [_1, dim] = max(s)

    rh = s
    rh[dim] = 1
    t = linspace(0, 2 * pi, s(dim) + 1)
    t = t[1 : -1 - 1]
    h = 1 - cos(t)
    data_windowed = data[""] * (repmat(shiftdim(h, dim), rh))

    return data_windowed


def machine_environment():
    # captures the environmental variables of the machine
    #
    # Example: exp_data = machine_environment(NaN)
    # timestamp
    exp_data = {}
    exp_data["time"] = datetime.today()
    ## General machine parameters
    # Tunes
    exp_data["tunes"] = get_all_tunes
    # Ring mode
    exp_data["ringmode"] = get_variable["SR-CS-RING-01:MODE"]
    # Machine current
    exp_data["current"] = get_variable["SR-DI-DCCT-01:SIGNAL"]
    # Fill pattern
    exp_data["fill_pattern"] = get_variable["SR-DI-PICO-01:BUCKETS"]
    exp_data["fill_pattern2"] = get_variable["SR-DI-PICO-02:BUCKETS"]
    exp_data["fill_pattern_180"] = get_variable["SR-DI-PICO-01:BUCKETS_180"]
    exp_data["fill_pattern2_180"] = get_variable["SR-DI-PICO-02:BUCKETS_180"]
    # RF frequency
    exp_data["RF"] = get_variable["LI-RF-MOSC-01:FREQ"]
    # Cavity voltages
    try:
        exp_data["cavity1_voltage"] = get_variable["SR-RF-LLRF-10:CAVVOLTAGE"]
    except ValueError:
        exp_data["cavity1_voltage"] = None

    try:
        exp_data["cavity2_voltage"] = get_variable["SR-RF-LLRF-20:CAVVOLTAGE"]
    except ValueError:
        exp_data["cavity2_voltage"] = None

    try:
        exp_data["cavity3_voltage"] = get_variable["SR-RF-LLRF-30:CAVVOLTAGE"]
    except ValueError:
        exp_data["cavity3_voltage"] = None

    # getting the kicker status
    injection = cell2mat(get_variable["LI-TI-MTGEN-01:SRPREI-MODE"])
    timing = cell2mat(get_variable["LI-TI-MTGEN-01:STATUS.DESC"])
    if injection.lower() == "Off":
        exp_data["kicker_status"] = "off"
    elif injection.lower() == "every shot":
        exp_data["kicker_status"] = "on"
    elif injection.upper() == "ON LINAC-PRE":
        if timing.lower() == "idle":
            exp_data["kicker_status"] = "off"
        else:
            exp_data["kicker_status"] = "on"

    else:
        exp_data["kicker_status"] = "unknown"

    # wiggler fields
    exp_data["wiggler_field_I15"] = get_variable["SR15I-ID-SCMPW-01:B_REAL"]
    exp_data["wiggler_field_I12"] = get_variable["SR12I-CS-SCMPW-01:B"]
    # capturing a sample pinhole image
    a = get_variable["SR01C-DI-DCAM-04:PROXY:DATA"]
    alims = get_variable[["SR01C-DI-DCAM-04:WIDTH", "SR01C-DI-DCAM-04:HEIGHT"]]
    a = a[1 : alims(1) * alims(2)]
    a = reshape(a, alims(1), [])
    a[a < 0] = (a[a < 0]) + 256
    exp_data["pinhole"] = a
    # Feedback status
    exp_data["orbit_feedback_status"] = get_variable["SR01A-CS-FOFB-01:RUN"]
    exp_data["tune_feedback_status"] = get_variable["SR-CS-TFB-01:STATUS"]
    # Emittance
    exp_data["emittance_h"] = get_variable["SR-DI-EMIT-01:HEMIT_MEAN"]
    exp_data["emittance_v"] = get_variable["SR-DI-EMIT-01:VEMIT_MEAN"]
    exp_data["coupling"] = get_variable["SR-DI-EMIT-01:COUPLING_MEAN"]
    exp_data["espread"] = get_variable["SR-DI-EMIT-01:ESPREAD_MEAN"]
    # Lifetime
    exp_data["lifetime"] = get_variable[
        "SR-DI-DCCT-01:LIFETIME"
    ]  # Lifetime on main printlay chosen for lowest error['']
    exp_data["life"]["dcct"]["life30sec"] = get_variable["SR-DI-DCCT-01:LIFE30"]
    exp_data["life"]["dcct"]["lifeerr30sec"] = get_variable["SR-DI-DCCT-01:ERROR30"]
    exp_data["life"]["dcct"]["cond30sec"] = get_variable["SR-DI-DCCT-01:COND30"]
    exp_data["life"]["dcct"]["life2min"] = get_variable["SR-DI-DCCT-01:LIFE120"]
    exp_data["life"]["dcct"]["lifeerr2min"] = get_variable["SR-DI-DCCT-01:ERROR120"]
    exp_data["life"]["dcct"]["cond2min"] = get_variable["SR-DI-DCCT-01:COND120"]
    exp_data["life"]["dcct"]["life5min"] = get_variable["SR-DI-DCCT-01:LIFE300"]
    exp_data["life"]["dcct"]["lifeerr5min"] = get_variable["SR-DI-DCCT-01:ERROR300"]
    exp_data["life"]["dcct"]["cond5min"] = get_variable["SR-DI-DCCT-01:COND300"]
    exp_data["life"]["dcct"]["life20min"] = get_variable["SR-DI-DCCT-01:LIFE1200"]
    exp_data["life"]["dcct"]["lifeerr20min"] = get_variable["SR-DI-DCCT-01:ERROR1200"]
    exp_data["life"]["dcct"]["cond20min"] = get_variable["SR-DI-DCCT-01:COND1200"]
    exp_data["life"]["bpm"]["life300sec"] = get_variable["SR-DI-EBPM-01:LIFE300"]
    exp_data["life"]["bpm"]["life300err"] = get_variable["SR-DI-EBPM-01:ERROR300"]
    exp_data["life"]["bpm"]["cond300sec"] = get_variable["SR-DI-EBPM-01:COND300"]
    exp_data["life"]["bpm"]["life120sec"] = get_variable["SR-DI-EBPM-01:LIFE120"]
    exp_data["life"]["bpm"]["life120err"] = get_variable["SR-DI-EBPM-01:ERROR120"]
    exp_data["life"]["bpm"]["cond120sec"] = get_variable["SR-DI-EBPM-01:COND120"]
    exp_data["life"]["bpm"]["life30sec"] = get_variable["SR-DI-EBPM-01:LIFE30"]
    exp_data["life"]["bpm"]["life30err"] = get_variable["SR-DI-EBPM-01:ERROR30"]
    exp_data["life"]["bpm"]["cond30sec"] = get_variable["SR-DI-EBPM-01:COND30"]
    exp_data["life"]["bpm"]["life10sec"] = get_variable["SR-DI-EBPM-01:LIFE10"]
    exp_data["life"]["bpm"]["life10err"] = get_variable["SR-DI-EBPM-01:ERROR10"]
    exp_data["life"]["bpm"]["cond10sec"] = get_variable["SR-DI-EBPM-01:COND10"]
    # Injection
    exp_data["injection"]["btssr2s"] = get_variable["CS-DI-XFER-01:BS-SR2"]
    exp_data["injection"]["btssr10s"] = get_variable["CS-DI-XFER-01:BS-SR10"]
    exp_data["injection"]["boostsr2s"] = get_variable["CS-DI-XFER-01:BR-SR2"]
    exp_data["injection"]["boostsr10s"] = get_variable["CS-DI-XFER-01:BR-SR10"]
    # IDs
    exp_data["id"]["gap02"] = get_variable["SR02I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap02j"] = get_variable["SR02J-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap03"] = get_variable["SR03I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap04"] = get_variable["SR04I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap05"] = get_variable["SR05I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase05"][1] = get_variable["SR05I-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase05"][2] = get_variable["SR05I-MO-SERVO-07:MOT.RBV"]
    exp_data["id"]["gap06a"] = get_variable["SR06I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase06a"][1] = get_variable["SR06I-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase06a"][2] = get_variable["SR06I-MO-SERVO-06:MOT.RBV"]
    exp_data["id"]["gap06b"] = get_variable["SR06I-MO-SERVC-21:CURRGAPD"]
    exp_data["id"]["phase06b"][1] = get_variable["SR06I-MO-SERVO-25:MOT.RBV"]
    exp_data["id"]["phase06b"][2] = get_variable["SR06I-MO-SERVO-26:MOT.RBV"]
    exp_data["id"]["gap07"] = get_variable["SR04I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap08"] = get_variable["SR08I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase08"][1] = get_variable["SR08I-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase08"][2] = get_variable["SR08I-MO-SERVO-07:MOT.RBV"]
    exp_data["id"]["gap09i"] = get_variable["SR09I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap09j"] = get_variable["SR09J-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase09j"][1] = get_variable["SR09J-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase09j"][2] = get_variable["SR09J-MO-SERVO-06:MOT.RBV"]
    exp_data["id"]["phase09j"][3] = get_variable["SR09J-MO-SERVO-07:MOT.RBV"]
    exp_data["id"]["phase09j"][4] = get_variable["SR09J-MO-SERVO-08:MOT.RBV"]
    exp_data["id"]["gap10a"] = get_variable["SR10I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase10a"][1] = get_variable["SR10I-MO-SERVO-03:MOT.RBV"]
    exp_data["id"]["phase10a"][2] = get_variable["SR10I-MO-SERVO-04:MOT.RBV"]
    exp_data["id"]["phase10a"][3] = get_variable["SR10I-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase10a"][4] = get_variable["SR10I-MO-SERVO-06:MOT.RBV"]
    exp_data["id"]["gap10b"] = get_variable["SR10I-MO-SERVC-21:CURRGAPD"]
    exp_data["id"]["phase10b"][1] = get_variable["SR10I-MO-SERVO-23:MOT.RBV"]
    exp_data["id"]["phase10b"][2] = get_variable["SR10I-MO-SERVO-24:MOT.RBV"]
    exp_data["id"]["phase10b"][3] = get_variable["SR10I-MO-SERVO-25:MOT.RBV"]
    exp_data["id"]["phase10b"][4] = get_variable["SR10I-MO-SERVO-26:MOT.RBV"]
    exp_data["id"]["gap11"] = get_variable["SR11I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["i12field"] = get_variable["SR12I-CS-SCMPW-01:B"]
    exp_data["id"]["gap13i"] = get_variable["SR13I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap13j"] = get_variable["SR13J-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap14"] = get_variable["SR14I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["i15field"] = get_variable["SR15I-ID-SCMPW-01:B_REAL"]
    exp_data["id"]["gap16"] = get_variable["SR16I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap18"] = get_variable["SR18I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap19"] = get_variable["SR19I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap20i"] = get_variable["SR20I-MO-SERVC-01:CURRGAPD"]
    # exp_data['id']['gap20j'] = get_variable['SR20J-MO-SERVC-01:CURRGAPD']
    exp_data["id"]["gap21"] = get_variable["SR21I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["phase21"][1] = get_variable["SR21I-MO-SERVO-05:MOT.RBV"]
    exp_data["id"]["phase21"][2] = get_variable["SR21I-MO-SERVO-06:MOT.RBV"]
    exp_data["id"]["phase21"][3] = get_variable["SR21I-MO-SERVO-07:MOT.RBV"]
    exp_data["id"]["phase21"][4] = get_variable["SR21I-MO-SERVO-08:MOT.RBV"]
    exp_data["id"]["gap22"] = get_variable["SR22I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap23"] = get_variable["SR23I-MO-SERVC-01:CURRGAPD"]
    exp_data["id"]["gap24"] = get_variable["SR24I-MO-SERVC-01:CURRGAPD"]
    exp_data["orbit_x"] = get_variable["SR-DI-EBPM-01:SA:X"]
    exp_data["orbit_y"] = get_variable["SR-DI-EBPM-01:SA:Y"]
    mbf_systems = {"SR23C-DI-TMBF-01:X", "SR23C-DI-TMBF-01:Y", "SR23C-DI-LMBF-01:IQ"}
    mbf_cards = {"SR23C-DI-TMBF-01", "SR23C-DI-TMBF-01", "SR23C-DI-LMBF-01"}
    mbf_axes = {"x", "y", "s"}
    for sjkh in range(1, len(mbf_systems)):
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["target_bunches"] = get_variable[
            [mbf_systems[sjkh], ":PLL:DET:BUNCHES_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["nco"]["gain"] = get_variable[
            [mbf_systems[sjkh], ":PLL:NCO:GAIN_DB_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["nco"]["freq"] = get_variable[
            [mbf_systems[sjkh], ":PLL:NCO:FREQ_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["nco"]["enable"] = get_variable[
            [mbf_systems[sjkh], ":PLL:NCO:ENABLE_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["integral"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:KI_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["proportional"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:KP_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["maglim"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:MIN_MAG_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["offsetlim"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:MAX_OFFSET_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["target_phase"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:TARGET_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["detector"]["source"] = get_variable[
            [mbf_systems[sjkh], ":PLL:DET:SELECT_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["detector"]["gain"] = get_variable[
            [mbf_systems[sjkh], ":PLL:DET:SCALING_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["detector"]["dwell"] = get_variable[
            [mbf_systems[sjkh], ":PLL:DET:DWELL_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["detector"]["blanking"] = get_variable[
            [mbf_systems[sjkh], ":PLL:DET:BLANKING_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["status"]["state"] = get_variable[
            [mbf_systems[sjkh], ":PLL:CTRL:STATUS"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["status"]["stopped_by_user"] = (
            get_variable[[mbf_systems[sjkh], ":PLL:CTRL:STOP:STOP"]]
        )
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["status"]["detector_overflow"] = (
            get_variable[[mbf_systems[sjkh], ":PLL:STA:DET_OVF"]]
        )
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["status"]["magnitude_error"] = (
            get_variable[[mbf_systems[sjkh], ":PLL:STA:MAG_ERROR"]]
        )
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["status"]["offset_overflow"] = (
            get_variable[[mbf_systems[sjkh], ":PLL:STA:OFFSET_OVF"]]
        )
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["readbacks"]["magnitude"] = get_variable[
            [mbf_systems[sjkh], ":PLL:FILT:MAG"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["readbacks"]["magnitudedb"] = (
            get_variable[[mbf_systems[sjkh], ":PLL:FILT:MAG_DB"]]
        )
        exp_data["mbf"][mbf_axes[sjkh]]["pll"]["readbacks"]["phase"] = get_variable[
            [mbf_systems[sjkh], ":PLL:FILT:PHASE"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["delays"]["fine"] = get_variable[
            [mbf_cards[sjkh], ":DLY:DAC:FINE_DELAY_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["delays"]["course"] = get_variable[
            [mbf_cards[sjkh], ":DLY:DAC:COARSE_DELAY_S"]
        ]
        exp_data["mbf"][mbf_axes[sjkh]]["delays"]["turn_offset"] = get_variable[
            [mbf_cards[sjkh], ":DLY:TURN:OFFSET_S"]
        ]

    exp_data["bbbfe"]["x_input_level"] = get_variable["SR23C-DI-BBFE-01:LEV:X.DESC"]
    exp_data["bbbfe"]["y_input_level"] = get_variable["SR23C-DI-BBFE-01:LEV:Y.DESC"]
    exp_data["bbbfe"]["i_input_level"] = get_variable["SR23C-DI-BBFE-01:LEV:I.DESC"]
    exp_data["bbbfe"]["lo_phase"] = get_variable["SR23C-DI-BBFE-01:PHA"]
    exp_data["bbbfe"]["x_phase"] = get_variable["SR23C-DI-BBFE-01:PHA:OFF:X"]
    exp_data["bbbfe"]["y_phase"] = get_variable["SR23C-DI-BBFE-01:PHA:OFF:Y"]
    exp_data["bbbfe"]["it_phase"] = get_variable["SR23C-DI-BBFE-01:PHA:OFF:IT"]
    exp_data["bbbfe"]["il_phase"] = get_variable["SR23C-DI-BBFE-01:PHA:OFF:IL"]
    exp_data["bbbfe"]["clk1"] = get_variable["SR23C-DI-BBFE-01:PHA:CLO:1"]
    exp_data["bbbfe"]["clk2"] = get_variable["SR23C-DI-BBFE-01:PHA:CLO:2"]
    exp_data["bbbfe"]["clk3"] = get_variable["SR23C-DI-BBFE-01:PHA:CLO:3"]
    exp_data["bbbfe"]["clk4"] = get_variable["SR23C-DI-BBFE-01:PHA:CLO:4"]
    return exp_data


def mbf_archival_conditional_filtering(requested_data, selections):
    # returns the sets of data which have metatdata values below thoise given in
    # selections
    #
    #   Args:
    #       input_data{cell array of structures}
    #       selections{cell array}: collumn 1 is the name of the field in the
    #                               metadata, collumn 2 is the value to be below['']
    #   Returns:
    #       sets {cell array of structures}: Datasets which matched the criteria['']
    #
    # Example conditioned_data = mbf_archival_conditional_filtering(requested_data)
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


def mbf_archival_dataset_retrieval(
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
    # Example: mbf_growdamp_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

    # Getting the desired system setup parameters['']
    [root_string, _2, _1] = mbf_system_config
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
        datasets = dir_list_gen_tree(root_string, "mat", 1)
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


def mbf_archival_plotting_setup(requested_data, times, experimental_setup):
    # Plots the data processed by mbf_growdamp_archival_analysis['']
    # Args:
    #      requested_data(structure): data and metatdata['']
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #
    # Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)
    [_3, harmonic_number, _2, _1] = mbf_system_config
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
    [root_string, _3, _2, _1] = mbf_system_config
    [filter_names, _1] = dir_list_gen(root_string, "", 1)
    filter_names = filter_names(f"DL_checkout_{ax}" in filter_names)
    filter_names = regexprep(filter_names, "_index.mat", "")
    requested_data = []
    for nfe in range(1, len(filter_names)):
        requested_data[nfe] = mbf_archival_dataset_retrieval(
            filter_names[nfe],
            date_range,
            "bypass_index",
            bypass_index,
            "metadata_only",
            metadata_only,
        )


def mbf_make_index(application_type, ax):
    # Writes index files to speed up archive retrival def s:
    # Args:
    #       application_type(str): either 'Growdamp', 'Bunch_motion', 'Modescan',
    #                           'Spectrum', 'LO_scan', 'system_phase_scan',
    #                           'clock_phase_scan'['']
    #       ax(str): 'x', 'y', or 's'
    #
    # Example mbf_make_index('Growdamp', 'x')
    [root_string, _2, _1] = mbf_system_config
    if (
        application_type == "Bunch_motion"
        or application_type == "LO_scan"
        or application_type == "system_phase_scan"
        or application_type == "clock_phase_scan"
    ):
        ax = ""
        index_name = "index"
        filter_name = application_type
    else:
        if ax.lower() == "x":
            index_name = "x_axis_index"
            filter_name = [application_type, "_x_axis"]
        elif ax.lower() == "y":
            index_name = "y_axis_index"
            filter_name = [application_type, "_y_axis"]
        elif ax.lower() == "s":
            index_name = "s_axis_index"
            filter_name = [application_type, "_s_axis"]
        else:
            error("makeIndex:InputError", "No valid axis given (should be x, y or s)")

    datasets = dir_list_gen_tree(root_string, ".mat", 1)
    wanted_datasets_type = datasets(
        find_position_in_cell_lst(strfind(datasets, filter_name))
    )
    print(["Creating lookup index for, ", application_type, " ", ax])
    if not wanted_datasets_type:
        print("No files to index")
    else:
        ok = np.zeros(len(wanted_datasets_type))
        file_time = []
        file_name = []
        for kse in range(1, len(wanted_datasets_type)):
            try:  # handling corrupted input files
                temp = load(wanted_datasets_type[kse])
            except me1:
                ok[kse] = 0
                print(f"{me1} message")

            data_name = fieldnames(temp)
            # Although the code saves eveything in 'data', older datasets have
            # a variety of names['']
            if (
                data_name[1] == "data"
                or data_name[1] == "growdamp"
                or data_name[1] == "what_to_save"
            ):
                file_time[kse] = temp[data_name[1]]["time"]
                file_name[kse] = wanted_datasets_type[kse]
                ok[kse] = 1
            else:
                #             print(fieldnames(temp))
                ok[kse] = 0

        file_index = cat(1, file_name[ok == 1], file_time[ok == 1])
        save(fullfile(root_string, [application_type, "_", index_name]), "file_index")


def mbf_setup_wait_for_hw_trigger(pv_names):
    memory_triggers = pv_names["tails"]["triggers"]["MEM"]
    sequencer_triggers = pv_names["tails"]["triggers"]["SEQ"]
    mbf_axes = {"x", "y", "s"}
    # Disarm all the sequencers
    for ekf in range(1, len(mbf_axes)):
        set_variable(
            [pv_names["hardware_names"][mbf_axes[ekf]], sequencer_triggers["disarm"]], 1
        )

    mbf_systems = {"T", "L"}
    for hse in range(1, 2):
        # Generate the base PV name['']
        pv_head = pv_names["hardware_names"][mbf_systems[hse]]
        # set up the appropriate triggering
        # Stop triggering first, otherwise there's a good chance the first thing
        # we'll do is loose the beam as we change things['']
        for trigger_ind in range(1, len(pv_names["trigger_inputs"])):
            trigger = pv_names["trigger_inputs"][trigger_ind]
            set_variable([pv_head, memory_triggers[trigger]["enable_status"]], "Ignore")
            set_variable([pv_head, memory_triggers[trigger]["blanking_status"]], "All")

        # Set the trigger to one shot
        set_variable([pv_head, memory_triggers["mode"]], "One Shot")
        # Set the triggering to External only
        set_variable([pv_head, memory_triggers["EXT"]["enable_status"]], "Enable")

    return requested_data


def mbf_system_config():
    #       harmonic_number (int): Harmonic number of the machine['']
    # root_path is the location for captured data['']
    root_path = "/dls/ops-data/Diagnostics/MBF/"
    harmonic_number = 936
    ## RF frequency
    pv_names = {}
    pv_names["RF"] = "SR-CS-RFFB-01:TARGET"
    ## Beam current
    pv_names["current"] = "SR-DI-DCCT-01:SIGNAL"
    ## Bunch pattern
    pv_names["bunch_pattern"] = "SR-DI-PICO-01:BUCKETS_180"
    pv_names["bunch_pattern2"] = "SR-DI-PICO-02:BUCKETS_180"
    ## Topup countdown
    pv_names["topup"]["countdown"] = "SR-CS-FILL-01:COUNTDOWN"
    ## Pinhole PVs
    pv_names["pinhole1"] = "SR01C-DI-DCAM-04"
    pv_names["pinhole2"] = "SR01C-DI-DCAM-05"
    ## Emittance measurement
    pv_names["emittance"]["status"] = "SR-DI-EMIT-01:STATUS"
    pv_names["emittance"]["x"]["val"] = "SR-DI-EMIT-01:HEMIT"
    pv_names["emittance"]["x"]["mean"] = "SR-DI-EMIT-01:HEMIT_MEAN"
    pv_names["emittance"]["x"]["error"] = "SR-DI-EMIT-01:HERROR"
    pv_names["energy_spread"]["val"] = "SR-DI-EMIT-01:ESPREAD"
    pv_names["energy_spread"]["mean"] = "SR-DI-EMIT-01:ESPREAD_MEAN"
    pv_names["emittance"]["y"]["val"] = "SR-DI-EMIT-01:VEMIT"
    pv_names["emittance"]["y"]["mean"] = "SR-DI-EMIT-01:VEMIT_MEAN"
    pv_names["emittance"]["y"]["error"] = "SR-DI-EMIT-01:VERROR"
    pv_names["coupling"]["val"] = "SR-DI-EMIT-01:COUPLING"
    pv_names["coupling"]["mean"] = "SR-DI-EMIT-01:COUPLING_MEAN"
    pv_names["beam_size"]["pinhole1"]["sigmax"] = "SR-DI-EMIT-01:P1:SIGMAX"
    pv_names["beam_size"]["pinhole1"]["sigmay"] = "SR-DI-EMIT-01:P1:SIGMAY"
    pv_names["beam_size"]["pinhole2"]["sigmax"] = "SR-DI-EMIT-01:P2:SIGMAX"
    pv_names["beam_size"]["pinhole2"]["sigmay"] = "SR-DI-EMIT-01:P2:SIGMAY"
    ## External trigger
    pv_names["Hardware_trigger"] = "LI-TI-MTGEN-01:BS-DI-MODE"
    ## DORIS PVs
    pv_names["doris"]["phase"] = "SR23C-DI-DORIS-01:TARGET_S"
    ## Frontend PVs
    pv_names["frontend"]["base"] = "SR23C-DI-BBFE-01"
    pv_names["frontend"]["system_phase"]["x"] = ":PHA:OFF:X"
    pv_names["frontend"]["system_phase"]["y"] = ":PHA:OFF:Y"
    pv_names["frontend"]["system_phase"]["sI"] = ":PHA:OFF:IT"
    pv_names["frontend"]["system_phase"]["sQ"] = ":PHA:OFF:IL"
    pv_names["frontend"]["clock_phase"]["x"] = ":PHA:CLO:3"
    pv_names["frontend"]["clock_phase"]["y"] = ":PHA:CLO:3"
    pv_names["frontend"]["clock_phase"]["s"] = ":PHA:CLO:4"
    pv_names["frontend"]["gain"]["x"] = ":LEV:X.DESC"
    pv_names["frontend"]["gain"]["y"] = ":LEV:Y.DESC"
    pv_names["frontend"]["gain"]["s"] = ":LEV:I.DESC"
    ## Backend PVs
    # Base PVs of the hardware['']
    pv_names["hardware_names"]["T"] = "SR23C-DI-TMBF-01"
    pv_names["hardware_names"]["L"] = "SR23C-DI-LMBF-01"
    pv_names["hardware_names"]["mem"]["x"] = pv_names["hardware_names"]["T"]
    pv_names["hardware_names"]["mem"]["y"] = pv_names["hardware_names"]["T"]
    pv_names["hardware_names"]["mem"]["s"] = pv_names["hardware_names"]["L"]
    pv_names["hardware_names"]["x"] = [pv_names["hardware_names"]["T"], ":X"]
    pv_names["hardware_names"]["y"] = [pv_names["hardware_names"]["T"], ":Y"]
    pv_names["hardware_names"]["s"] = [pv_names["hardware_names"]["L"], ":IQ"]
    pv_names["hardware_names"]["lab"] = "TS-DI-TMBF-02"
    # test system
    pv_names["hardware_names"]["mem"]["tx"] = pv_names["hardware_names"]["lab"]
    pv_names["hardware_names"]["mem"]["ty"] = pv_names["hardware_names"]["lab"]
    pv_names["hardware_names"]["tx"] = [pv_names["hardware_names"]["lab"], ":X"]
    pv_names["hardware_names"]["ty"] = [pv_names["hardware_names"]["lab"], ":Y"]
    ## Trigger settings
    pv_names["tails"]["triggers"]["mode"] = ":TRG:SEQ:MODE_S"
    pv_names["tails"]["triggers"]["arm"] = ":TRG:SEQ:ARM_S.PROC"
    pv_names["trigger_inputs"] = {"SOFT", "EXT", "PM", "ADC0", "ADC1", "SEQ0", "SEQ1"}
    for trigger_ind in range(1, len(pv_names["trigger_inputs"])):
        trigger = pv_names["trigger_inputs"][trigger_ind]
        pv_names["tails"]["triggers"][trigger]["enable_status"] = [
            ":TRG:SEQ:",
            trigger,
            ":EN_S",
        ]
        pv_names["tails"]["triggers"][trigger]["blanking_status"] = [
            ":TRG:SEQ:",
            trigger,
            ":BL_S",
        ]

    pv_names["tails"]["triggers"]["SEQ"]["arm"] = ":TRG:SEQ:ARM_S.PROC"
    pv_names["tails"]["triggers"]["SEQ"]["disarm"] = ":TRG:SEQ:DISARM_S.PROC"
    pv_names["tails"]["triggers"]["SEQ"]["mode"] = ":TRG:SEQ:MODE_S"
    pv_names["tails"]["triggers"]["SEQ"]["delay"] = ":TRG:SEQ:DELAY_S"
    # shared with other axis
    pv_names["tails"]["triggers"]["MEM"]["arm"] = (
        ":TRG:MEM:ARM_S.PROC"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["MEM"]["disarm"] = (
        ":TRG:MEM:DISARM_S.PROC"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["MEM"]["mode"] = (
        ":TRG:MEM:MODE_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["MEM"]["delay"] = (
        ":TRG:MEM:DELAY_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["soft"] = (
        ":TRG:SOFT_S.PROC"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["soft_settings"] = (
        ":TRG:SOFT_S.SCAN"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["shared"] = (
        ":TRG:MODE_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["triggers"]["blanking_length"] = (
        ":TRG:BLANKING_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    for trigger_ind in range(1, len(pv_names["trigger_inputs"])):
        trigger = pv_names["trigger_inputs"][trigger_ind]
        pv_names["tails"]["triggers"]["MEM"][trigger]["enable_status"] = [
            ":TRG:MEM:",
            trigger,
            ":EN_S",
        ]
        pv_names["tails"]["triggers"]["MEM"][trigger]["blanking_status"] = [
            ":TRG:MEM:",
            trigger,
            ":BL_S",
        ]

    ## Super Sequencer settings
    pv_names["tails"]["Super_sequencer_count"] = ":SEQ:SUPER:COUNT_S"
    pv_names["tails"]["Super_sequencer_reset"] = ":SEQ:SUPER:RESET_S.PROC"
    pv_names["tails"]["Super_sequencer"]["count"] = ":SEQ:SUPER:COUNT_S"
    pv_names["tails"]["Super_sequencer"]["reset"] = ":SEQ:SUPER:RESET_S.PROC"
    ## Sequencer settings
    # pv_names['tails']['Sequencer']['Base'] = ':SEQ'
    # pv_names['tails']['Sequencer']['start_frequency'] = ':START_FREQ_S'
    # pv_names['tails']['Sequencer']['end_frequency'] = ':END_FREQ_S'
    # pv_names['tails']['Sequencer']['dwell'] = ':DWELL_S'
    # pv_names['tails']['Sequencer']['gain'] = ':GAIN_S'
    # pv_names['tails']['Sequencer']['gaindb'] = ':GAIN_DB_S'
    # pv_names['tails']['Sequencer']['enable'] = ':ENABLE_S'
    # pv_names['tails']['Sequencer']['step_frequency'] = ':STEP_FREQ_S'
    # pv_names['tails']['Sequencer']['holdoff'] = ':HOLDOFF_S'
    # pv_names['tails']['Sequencer']['bank_select'] = ':BANK_S'
    # pv_names['tails']['Sequencer']['capture_state'] = ':CAPTURE_S'
    # pv_names['tails']['Sequencer']['windowing_state'] = ':ENWIN_S'
    # pv_names['tails']['Sequencer']['blanking_state'] = ':BLANK_S'
    # applies to all
    pv_names["tails"]["Sequencer"]["start_state"] = ":SEQ:PC_S"
    pv_names["tails"]["Sequencer"]["steady_state_bank"] = ":SEQ:0:BANK_S"
    pv_names["tails"]["Sequencer"]["reset"] = ":SEQ:RESET_S.PROC"
    # pv_names['tails']['Sequencer']['count'] = ':COUNT_S'
    for n_seq in range(1, 7):
        n_seq_label = n_seq
        l_seq = ["seq", n_seq_label]
        pv_names["tails"]["Sequencer"][l_seq]["start_frequency"] = [
            ":SEQ:",
            n_seq_label,
            ":START_FREQ_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["end_frequency"] = [
            ":SEQ:",
            n_seq_label,
            ":END_FREQ_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["turns"] = [
            ":SEQ:",
            n_seq_label,
            ":COUNT_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["dwell"] = [
            ":SEQ:",
            n_seq_label,
            ":DWELL_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["gain"] = [
            ":SEQ:",
            n_seq_label,
            ":GAIN_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["gaindb"] = [
            ":SEQ:",
            n_seq_label,
            ":GAIN_DB_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["enable"] = [
            ":SEQ:",
            n_seq_label,
            ":ENABLE_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["step_frequency"] = [
            ":SEQ:",
            n_seq_label,
            ":STEP_FREQ_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["holdoff"] = [
            ":SEQ:",
            n_seq_label,
            ":HOLDOFF_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["bank_select"] = [
            ":SEQ:",
            n_seq_label,
            ":BANK_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["capture_state"] = [
            ":SEQ:",
            n_seq_label,
            ":CAPTURE_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["windowing_state"] = [
            ":SEQ:",
            n_seq_label,
            ":ENWIN_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["blanking_state"] = [
            ":SEQ:",
            n_seq_label,
            ":BLANK_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["holdoff_state"] = [
            ":SEQ:",
            n_seq_label,
            ":STATE_HOLDOFF_S",
        ]
        pv_names["tails"]["Sequencer"][l_seq]["tune_pll_following"] = [
            ":SEQ:",
            n_seq_label,
            ":TUNE_PLL_S",
        ]

    ## Bank settings
    # pv_names['tails']['Bunch_bank']['Base'] = ':BUN'
    # pv_names['tails']['Bunch_bank']['Gains'] = ':GAINWF_S'
    # pv_names['tails']['Bunch_bank']['Output_types'] = ':OUTWF_S'
    # pv_names['tails']['Bunch_bank']['FIR_select'] = ':FIRWF_S'
    # pv_names['tails']['Bunch_bank']['FIR_set_enable'] = ':FIR:SET_ENABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['FIR_enable'] = ':FIR:ENABLE_S'
    # pv_names['tails']['Bunch_bank']['NCO1_set_enable'] = ':NCO1:SET_ENABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['NCO2_set_enable'] = ':NCO2:SET_ENABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['NCO1_enable'] = ':NCO1:ENABLE_S'
    # pv_names['tails']['Bunch_bank']['NCO2_enable'] = ':NCO2:ENABLE_S'
    # pv_names['tails']['Bunch_bank']['SEQ_set_enable'] = ':SEQ:SET_ENABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['SEQ_enable'] = ':SEQ:ENABLE_S'
    # pv_names['tails']['Bunch_bank']['PLL_enable'] = ':PLL:SET_ENABLE_S'
    # pv_names['tails']['Bunch_bank']['FIR_set_disable'] = ':FIR:SET_DISABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['FIR_disable'] = ':FIR:DISABLE_S'
    # pv_names['tails']['Bunch_bank']['NCO1_disable'] = ':NCO1:SET_DISABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['NCO2_disable'] = ':NCO2:SET_DISABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['SEQ_disable'] = ':SEQ:SET_DISABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['PLL_disable'] = ':PLL:SET_DISABLE_S['PROC']'
    # pv_names['tails']['Bunch_bank']['FIR_gains'] = ':FIR:GAIN_S'
    # pv_names['tails']['Bunch_bank']['NCO1_gains'] = ':NCO1:GAIN_S'
    # pv_names['tails']['Bunch_bank']['NCO2_gains'] = ':NCO2:GAIN_S'
    # pv_names['tails']['Bunch_bank']['SEQ_gains'] = ':SEQ:GAIN_S'
    # pv_names['tails']['Bunch_bank']['PLL_gains'] = ':PLL:GAIN_S'
    for n_bank in range(0, 3):
        n_bank_label = n_bank
        l_bank = ["bank", n_bank_label]
        pv_names["tails"]["Bunch_bank"][l_bank]["Output_types"] = [
            ":BUN:",
            n_bank_label,
            ":OUTWF_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["bunch_select"] = [
            ":BUN:",
            n_bank_label,
            ":BUNCH_SELECT_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["enablewf"] = [
            ":BUN:",
            n_bank_label,
            ":FIR:ENABLE_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["set_enable"] = [
            ":BUN:",
            n_bank_label,
            ":FIR:SET_ENABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["set_disable"] = [
            ":BUN:",
            n_bank_label,
            ":FIR:SET_DISABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["gainwf"] = [
            ":BUN:",
            n_bank_label,
            ":FIR:GAIN_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["gainswfdb"] = [
            ":BUN:",
            n_bank_label,
            ":FIR:GAIN_DB",
        ]
        #     Select which filter to use on which bunch
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["selectwf"] = [
            ":BUN:",
            n_bank_label,
            ":FIRWF_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["FIR"]["set_select"] = [
            ":BUN:",
            n_bank_label,
            ":FIRWF_SET_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO1"]["enablewf"] = [
            ":BUN:",
            n_bank_label,
            ":NCO1:ENABLE_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO1"]["set_enable"] = [
            ":BUN:",
            n_bank_label,
            ":NCO1:SET_ENABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO1"]["set_disable"] = [
            ":BUN:",
            n_bank_label,
            ":NCO1:SET_DISABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO1"]["gainswf"] = [
            ":BUN:",
            n_bank_label,
            ":NCO1:GAIN_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO1"]["gainswfdb"] = [
            ":BUN:",
            n_bank_label,
            ":NCO1:GAIN_DB",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO2"]["enablewf"] = [
            ":BUN:",
            n_bank_label,
            ":NCO2:ENABLE_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO2"]["set_enable"] = [
            ":BUN:",
            n_bank_label,
            ":NCO2:SET_ENABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO2"]["set_disable"] = [
            ":BUN:",
            n_bank_label,
            ":NCO2:SET_DISABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO2"]["gainswf"] = [
            ":BUN:",
            n_bank_label,
            ":NCO2:GAIN_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["NCO2"]["gainswfdb"] = [
            ":BUN:",
            n_bank_label,
            ":NCO2:GAIN_DB",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["SEQ"]["enablewf"] = [
            ":BUN:",
            n_bank_label,
            ":SEQ:ENABLE_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["SEQ"]["set_enable"] = [
            ":BUN:",
            n_bank_label,
            ":SEQ:SET_ENABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["SEQ"]["set_disable"] = [
            ":BUN:",
            n_bank_label,
            ":SEQ:SET_DISABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["SEQ"]["gainswf"] = [
            ":BUN:",
            n_bank_label,
            ":SEQ:GAIN_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["SEQ"]["gainswfdb"] = [
            ":BUN:",
            n_bank_label,
            ":SEQ:GAIN_DB",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["PLL"]["enablewf"] = [
            ":BUN:",
            n_bank_label,
            ":PLL:ENABLE_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["PLL"]["set_enable"] = [
            ":BUN:",
            n_bank_label,
            ":PLL:SET_ENABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["PLL"]["set_disable"] = [
            ":BUN:",
            n_bank_label,
            ":PLL:SET_DISABLE_S.PROC",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["PLL"]["gainswf"] = [
            ":BUN:",
            n_bank_label,
            ":PLL:GAIN_S",
        ]
        pv_names["tails"]["Bunch_bank"][l_bank]["PLL"]["gainswfdb"] = [
            ":BUN:",
            n_bank_label,
            ":PLL:GAIN_DB",
        ]

    ## Detector settings
    # applies to all
    pv_names["tails"]["Detector"]["source"] = ":DET:SELECT_S"
    pv_names["tails"]["Detector"]["fill_waveforms"] = ":DET:FILL_WAVEFORMS_S"
    pv_names["tails"]["Detector"]["fir_delay"] = ":DET:FIR_DELAY_S"
    for n_det in range(0, 3):
        n_det_label = n_det
        l_det = ["det", n_det_label]
        pv_names["tails"]["Detector"][l_det]["enable"] = [
            ":DET:",
            n_det_label,
            ":ENABLE_S",
        ]
        pv_names["tails"]["Detector"][l_det]["bunch_selection"] = [
            ":DET:",
            n_det_label,
            ":BUNCHES_S",
        ]  # How do you set all?
        pv_names["tails"]["Detector"][l_det]["scale"] = [
            ":DET:",
            n_det_label,
            ":SCALING_S",
        ]  # gain?
        pv_names["tails"]["Detector"][l_det]["I"] = [":DET:", n_det_label, ":I"]
        pv_names["tails"]["Detector"][l_det]["Q"] = [":DET:", n_det_label, ":Q"]
        pv_names["tails"]["Detector"][l_det]["power"] = [":DET:", n_det_label, ":POWER"]
        pv_names["tails"]["Detector"][l_det]["bunch_select"] = [
            ":DET:",
            n_det_label,
            ":BUNCH_SELECT_S",
        ]
        pv_names["tails"]["Detector"][l_det]["reset_selection"] = [
            ":DET:",
            n_det_label,
            ":RESET_SELECT_S.PROC",
        ]
        pv_names["tails"]["Detector"][l_det]["set_selection"] = [
            ":DET:",
            n_det_label,
            ":SET_SELECT_S.PROC",
        ]

    ## Memory settings
    pv_names["tails"]["MEM"]["status"] = (
        ":MEM:BUSY"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["MEM"]["channel_select"] = (
        ":MEM:SELECT_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["MEM"]["offset"] = (
        ":MEM:OFFSET_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["MEM"]["runout"] = (
        ":MEM:RUNOUT_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["MEM"]["channel0_target"] = (
        ":MEM:SEL0_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["MEM"]["channel1_target"] = (
        ":MEM:SEL1_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE['']
    )
    pv_names["tails"]["TRG"]["memory_status"] = ":TRG:MEM:STATUS"
    ## NCO settings
    for n_nco in range(1, 2):
        n_nco_label = n_nco
        l_nco = ["NCO", n_nco_label]
        pv_names["tails"][l_nco]["frequency"] = [":NCO", n_nco_label, ":FREQ_S"]
        pv_names["tails"][l_nco]["gain"] = [":NCO", n_nco_label, ":GAIN_S"]
        pv_names["tails"][l_nco]["gain_scalar"] = [
            ":NCO",
            n_nco_label,
            ":GAIN_SCALAR_S",
        ]
        pv_names["tails"][l_nco]["gaindb"] = [":NCO", n_nco_label, ":GAIN_DB_S"]
        pv_names["tails"][l_nco]["enable"] = [":NCO", n_nco_label, ":ENABLE_S"]
        pv_names["tails"][l_nco]["PLL_follow"] = [":NCO", n_nco_label, ":TUNE_PLL_S"]

    ## FIR settings
    pv_names["tails"]["FIR"]["gain"] = ":FIR:GAIN_S"
    pv_names["tails"]["FIR"]["gaindb"] = ":FIR:GAIN_DB_S"
    pv_names["tails"]["FIR"]["method_of_construction"] = ":FIR:USEWF_S"
    ## Tune settings
    pv_names["tails"]["tune"]["sync_tune"] = ":TUNE:SYNCTUNE"
    pv_names["tails"]["tune"]["centre"] = ":TUNE:CENTRE:TUNE"
    pv_names["tails"]["tune"]["left"] = ":TUNE:LEFT:TUNE"
    pv_names["tails"]["tune"]["right"] = ":TUNE:RIGHT:TUNE"
    pv_names["tails"]["tune"]["centre_width"] = ":TUNE:CENTRE:WIDTH"
    pv_names["tails"]["tune"]["left_width"] = ":TUNE:LEFT:WIDTH"
    pv_names["tails"]["tune"]["right_width"] = ":TUNE:RIGHT:WIDTH"
    pv_names["tails"]["tune"]["centre_height"] = ":TUNE:CENTRE:HEIGHT"
    pv_names["tails"]["tune"]["left_height"] = ":TUNE:LEFT:HEIGHT"
    pv_names["tails"]["tune"]["right_height"] = ":TUNE:RIGHT:HEIGHT"
    ## PLL settings
    pv_names["tails"]["pll"]["detector"]["dwell"] = ":PLL:DET:DWELL_S"
    pv_names["tails"]["pll"]["detector"]["target_bunches"] = ":PLL:DET:BUNCHES_S"
    pv_names["tails"]["pll"]["detector"]["mode"] = ":PLL:DET:SELECT_S"
    pv_names["tails"]["pll"]["detector"]["scaling"] = ":PLL:DET:SCALING_S"
    pv_names["tails"]["pll"]["detector"]["blanking"] = ":PLL:DET:BLANKING_S"
    pv_names["tails"]["pll"]["detector"]["dwell"] = ":PLL:DET:DWELL_S"
    pv_names["tails"]["pll"]["nco"]["enable"] = ":PLL:NCO:ENABLE_S"
    pv_names["tails"]["pll"]["nco"]["gain"] = ":PLL:NCO:GAIN_DB_S"
    pv_names["tails"]["pll"]["nco"]["set_frequency"] = ":PLL:NCO:FREQ_S"
    pv_names["tails"]["pll"]["nco"]["frequency"] = ":PLL:NCO:FREQ"
    pv_names["tails"]["pll"]["nco"]["offset_waveform"] = ":PLL:NCO:OFFSETWF"
    pv_names["tails"]["pll"]["nco"]["mean_offset"] = ":PLL:NCO:MEAN_OFFSET"
    pv_names["tails"]["pll"]["nco"]["std_offset"] = ":PLL:NCO:STD_OFFSET"
    pv_names["tails"]["pll"]["nco"]["offset"] = ":PLL:NCO:OFFSET"
    pv_names["tails"]["pll"]["nco"]["tune"] = ":PLL:NCO:TUNE"
    pv_names["tails"]["pll"]["start"] = ":PLL:CTRL:START_S.PROC"
    pv_names["tails"]["pll"]["stop"] = ":PLL:CTRL:STOP_S.PROC"
    pv_names["tails"]["pll"]["p"] = ":PLL:CTRL:KP_S"
    pv_names["tails"]["pll"]["i"] = ":PLL:CTRL:KI_S"
    pv_names["tails"]["pll"]["target_phase"] = ":PLL:CTRL:TARGET_S"
    pv_names["tails"]["pll"]["minumum_magnitude"] = ":PLL:CTRL:MIN_MAG_S"
    pv_names["tails"]["pll"]["maximum_offset"] = ":PLL:CTRL:MAX_OFFSET_S"
    pv_names["tails"]["pll"]["status"] = ":PLL:CTRL:STATUS"
    pv_names["tails"]["pll"]["readback"]["magnitude"] = ":PLL:FILT:MAG"
    pv_names["tails"]["pll"]["readback"]["phase"] = ":PLL:FILT:PHASE"
    pv_names["tails"]["pll"]["readback"]["i"] = ":PLL:FILT:I"
    pv_names["tails"]["pll"]["readback"]["q"] = ":PLL:FILT:Q"
    pv_names["tails"]["pll"]["stop_reasons"]["stop"] = ":PLL:CTRL:STOP:STOP"
    pv_names["tails"]["pll"]["stop_reasons"]["detector_overflow"] = (
        ":PLL:CTRL:STOP:DET_OVF"
    )
    pv_names["tails"]["pll"]["stop_reasons"]["offset_overflow"] = (
        ":PLL:CTRL:STOP:OFFSET_OVF"
    )
    pv_names["tails"]["pll"]["stop_reasons"]["magnitude_error"] = (
        ":PLL:CTRL:STOP:MAG_ERROR"
    )
    ## ADC buffers
    pv_names["tails"]["adc"]["delta"] = ":ADC:MMS:DELTA"
    pv_names["tails"]["adc"]["max"] = ":ADC:MMS:MAX"
    pv_names["tails"]["adc"]["mean"] = ":ADC:MMS:MEAN"
    pv_names["tails"]["adc"]["min"] = ":ADC:MMS:MIN"
    pv_names["tails"]["adc"]["std"] = ":ADC:MMS:STD"
    pv_names["tails"]["adc"]["reject_count"] = ":ADC:REJECT_COUNT_S"
    pv_names["tails"]["adc"]["phase"]["mean"] = ":ADC:PHASE_MEAN"
    pv_names["tails"]["adc"]["dram_source"] = ":ADC:DRAM_SOURCE_S"
    pv_names["tails"]["adc"]["loopback"] = ":ADC:LOOPBACK_S"
    ## DAC buffers
    pv_names["tails"]["dac"]["delta"] = ":DAC:MMS:DELTA"
    pv_names["tails"]["dac"]["max"] = ":DAC:MMS:MAX"
    pv_names["tails"]["dac"]["mean"] = ":DAC:MMS:MEAN"
    pv_names["tails"]["dac"]["min"] = ":DAC:MMS:MIN"
    pv_names["tails"]["dac"]["std"] = ":DAC:MMS:STD"
    pv_names["tails"]["dac"]["dram_source"] = ":DAC:DRAM_SOURCE_S"
    return root_path, harmonic_number, pv_names


def mode_to_frequency(RF, harmonic_number, tune, data):
    # converts a mode scan into the equivalent frequencies['']
    x_data_p1 = (RF / harmonic_number) * (range(harmonic_number / 2) + tune)
    x_data_p2 = RF - (RF / harmonic_number) * [
        range((harmonic_number / 2), (harmonic_number)) + tune
    ]
    x_data = cat(2, x_data_p1, x_data_p2)
    [x_data, I] = sort(x_data)
    data = data(I)
    # Function identical to MEAN, except NaNs are discounted['']
    #
    # Similar replacements exist for NONANMEAN, NONANMEDIAN, NONANSTD,
    # NONANSUM and NONANCUMSUM which are all part of the NaN-suite['']
    return x_data, data


def nonanmean(y0, dim):
    if nargin == 1:
        dim = find(y0.shape != 1, 1, "first")

    if not dim:
        # this covers the case when there is only one value
        dim = 1

    nan_list = isnan(y0)
    y0[isnan(y0)] = 0
    y = sum(y0, dim) / (y0.shape[dim] - sum(nan_list, dim))


def populate_archive_graph(input_data, years_input, times, x_plt_axis):
    if not input_data:
        return

    y_max = max(max(input_data))
    y_min = min(min(input_data))
    for esr in range(years_input.shape[0]):
        years[esr] = years_input[esr][1]
        states[esr] = 0
        cols[esr] = years_input[esr][2]

    sample_year_temp = datevec(times)
    year_list = sample_year_temp[:, 1]
    if len(unique(year_list)) < 2:
        for ner in range(1, input_data.shape[0]):
            sample_time = datevec(times(ner))
            sample_time = datestr(sample_time)
            plot(x_plt_axis, input_data[ner, :], "DisplayName", sample_time)

    else:
        for ner in range(1, input_data.shape[0]):
            years_ind = find(year_list(ner) == years)
            if states(years_ind) == 0:
                plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "DisplayName",
                    (years[years_ind]),
                )
                states[years_ind] = 1
            else:
                plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "HandleVisibility",
                    "off",
                )

    xlim([min(x_plt_axis), max(x_plt_axis)])
    ylim([y_min, y_max])
    legend("show")


def save_to_archive(root_string, data):
    # Saves the requested variables in the given filename in a location
    # detemined by the time_value['']
    # The relavent folder structure will be generated['']
    #
    # Example: save_to_archive(root_string, what_to_save)
    # Generating the required directory structure['']
    date_vector = datevec(data["time"])
    tree_gen(root_string, date_vector)
    # construct filename and add it to the structure
    data["filename"] = construct_datastamped_filename(data["base_name"], date_vector)
    mth = date_vector[2]
    dy = date_vector[3]
    if mth < 10:
        mth = "0" + mth
    if dy < 10:
        dy = "0" + dy

    save_name = os.path.join(
        root_string, (date_vector(1)), mth, dy, f"{data['filename']}.mat"
    )
    scipy.savemat(save_name, "data", "-v7.3")
    # print[['Data saved simulated: , ',save_name]]
    print[["Data saved to: , ", save_name]]
    index_name = [data["base_name"], "_index"]
    if exist(fullfile(root_string, [index_name, ".mat"]), "file"):
        load(fullfile(root_string, [index_name, ".mat"]), "file_index")
        new_ind = file_index.shape[1] + 1
        file_index[1][new_ind] = save_name
        file_index[2][new_ind] = date_vector
        save(fullfile(root_string, [index_name, ".mat"]), "file_index", "-v7.3")
        print("Index updated")
    else:
        file_index[1][1] = save_name
        file_index[2][1] = date_vector
        save(fullfile(root_string, [index_name, ".mat"]), "file_index", "-v7.3")
        print("New index file created")


def set_variable(variable_names, variable_values, system_type="EPICS"):
    # def to set a group of variables[''] This abstraction allows easier porting:
    # between EPICS and TANGO (and potentially others)
    if system_type.upper() == "EPICS":
        lcaPut(variable_names, variable_values)
    elif system_type.upper() == "TANGO":
        raise ValueError(
            "setVariable:systemTypeErrorTango calls are not yet implemented"
        )
    else:
        raise ValueError(
            "setVariable:systemTypeError",
            "alternative sytem calls are not yet implemented",
        )


def setup_operational_mode(mbf_axis, operational_mode):
    # Runs the setup scripts underlying the blue buttons['']
    # This allows the system to be put into a known state['']
    #   Args:
    #       mbf_axis (char): x, y or  s
    #       operational_mode (char): 'TuneOnly', 'TuneSpecial' or 'Feedback'
    mbf_axis = mbf_axis.lower()
    expected_axis_values = ["x", "y", "s", "it"]
    expected_operational_modes = ["TuneOnly", "TuneSpecial", "Feedback"]
    mbf_axis = validatestring(mbf_axis, expected_axis_values)
    action = validatestring(operational_mode, expected_operational_modes)
    if mbf_axis == "it":
        mbf_axis = "s"

    [_2, _1, pv_names] = mbf_system_config
    device = pv_names["hardware_names"][mbf_axis]
    if action == "TuneOnly":
        action = "TUNE"
    elif action == "TuneSpecial":
        action = "AP"
    elif action == "Feedback":
        action = "FB"

    # Pick up the base directory
    [rc, gui_dir] = system("configure-ioc s -p DI-MBF-gui-dir")
    assert (rc == 0, "Error running `configure-ioc`")
    gui_dir = strip(gui_dir, "right")  # Get rid of trailing newline
    # construct the bash command
    description = "Setting MBF defaults"
    bash_command = print(
        "#s/#s '#s' mbf-setup-tune #s #s",
        gui_dir,
        "/epics/opi/scripts/mbf-run-command",
        description,
        device,
        action,
    )
    rc = system(bash_command)
    assert (rc == 0, "Error running mbf-setup-tune")
    return y


def sub_directories(main_dir):
    # outputs a list of sub-directories of the input directory
    #
    # example: sub_dir = sub_directories(main_dir)
    # finding the subdirectories
    files = dir(main_dir)
    lc = len(files)
    tk = 1
    inds = []
    for rn in range(1, lc):
        if files(rn)["isdir"] == 1:
            inds[tk] = rn
            tk = tk + 1

    inds[tk:-1] = []
    if tk == 1:
        tc = 1
        folders = files(inds)
        sub_dir = []
        for tb in range(1, len(folders)):
            if folders(tb)["name"] == "." or folders(tb)["name"] == "..":
                pass
                # skip the . and .. found on linux systems.
            else:
                sub_dir[tc] = folders(tb)["name"]
                tc = tc + 1

        sub_dir[tc:-1] = []
    else:
        sub_dir = []


def tree_gen(tree_root, c):
    # generates a directory structure using the time vector from clock
    # tree_root is where you want the subdirectoires to be placed
    # cl is the clock vector
    # Adapting to windows or linux paths
    if ispc == 1:
        slash = "\\"
    else:
        slash = "/"

    yr = c(1)
    mth = c(2)
    dy = c(3)
    if c(2) < 10:
        mth = ["0", mth]

    if c(3) < 10:
        dy = ["0", dy]

    # generating directory tree
    if exist([tree_root, yr, slash], "dir") == 0:
        system(["mkdir ", tree_root, yr, slash])

    if exist([tree_root, yr, slash, mth, slash], "dir") == 0:
        system(["mkdir ", tree_root, yr, slash, mth, "/"])

    if exist([tree_root, yr, slash, mth, slash, dy, slash], "dir") == 0:
        system(["mkdir ", tree_root, yr, slash, mth, slash, dy, slash])

    return sub_dir


def tune_fit(tune_scale, tune_trace):
    # a = width
    # b = centre
    # c= height scaling
    # Lorentz fix with the center locked at the max value['']
    [start_height, ind] = max(tune_trace)
    start_centre = tune_scale(ind)
    start_width = 1e-4
    fo = fitoptions(
        "Method",
        "NonlinearLeastSquares",
        "Lower",
        [0, 0],
        "Upper",
        [Inf, Inf],
        "StartPoint",
        [start_width, start_height / 2 * pi * start_width],
    )
    ft = fittype(
        "c []* ((1 []/ pi) * 0.5 []* a / ((x - n)^2 + (0.5 []* a)[]^2))",
        "problem",
        "n",
        "options",
        fo,
    )
    [fit_curve, gof2] = fit(tune_scale, tune_trace, ft, "problem", start_centre)
    # figure
    # plot(tune_scale, tune_trace)
    # hold on
    # plot(fit_curve, 'm')


def update_all_indexes():
    # updates all indexes in the data archive
    # useful if something is corrupted['']
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
