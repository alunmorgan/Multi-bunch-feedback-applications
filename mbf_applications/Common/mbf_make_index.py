from scipy.io import savemat # type: ignore

from mbf_applications.Common.find_position_in_list import findPositionInList


def mbfMakeIndex(app, ax=None):

    root_string, _1, _2, _3 = mbfSystemConfig()

    if (
        not app == "Growdamp"
        and not app == "Bunch_motion"
        and not app == "Modescan"
        and not app == "Spectrum"
        and not app == "LO_scan"
        and not app == "system_phase_scan"
        and not app == "clock_phase_scan"
    ):
        raise ValueError(
            "mbf_make_index: No valid application given (Growdamp, Bunch_motion, Modescan, Spectrum, LO_scan, system_phase_scan, clock_phase_scan)"
        )

    if ax == None:
        ax = ""
        if app == "Growdamp" or app == "Modescan" or app == "Spectrum":
            raise ValueError("An axis needs to be specified")

    if (
        app == "Bunch_motion"
        or app == "LO_scan"
        or app == "system_phase_scan"
        or app == "clock_phase_scan"
    ):
        index_name = "index"
        filter_name = app
    else:
        if ax == "x" or ax == "X":
            index_name = "x_axis_index"
            filter_name = "".join((app, "_x_axis"))
        elif ax == "y" or ax == "Y":
            index_name = "y_axis_index"
            filter_name = "".join((app, "_y_axis"))
        elif ax == "s" or ax == "S":
            index_name = "s_axis_index"
            filter_name = "".join((app, "_s_axis"))
        else:
            raise ValueError(
                "mbf_make_index: No valid axis given (should be x, y or s)"
            )

    datasets = []
    for nes in root_string:
        sets_temp = dir_list_gen_tree(nes, ".mat", 1)
        datasets.append(sets_temp)

    datasets = datasets[2:-1]
    wanted_datasets_type = datasets(findPositionInList(datasets, filter_name))
    print("".join(("Creating lookup index for ", app, " ", ax)))
    if isempty(wanted_datasets_type):
        print("No files to index")
    else:
        for kse in range(len(wanted_datasets_type)):
            temp = loadmat(wanted_datasets_type[kse])
            data_name = fieldnames[temp]
            # Although the code saves eveything in 'data', older datasets have
            # a variety of names.
            if (
                data_name[0] == "data"
                or data_name[0] == "growdamp"
                or data_name[0] == "what_to_save"
            ):
                file_time[kse] = temp[data_name[0]]["time"]
                file_name[kse] = wanted_datasets_type[kse]
                ok[kse] = 1
            else:
                ok[kse] = 0
        # TODO refer back to original code.
        file_index.append(file_name(ok == 1), file_time(ok == 1))
        savemat(os.path.join(root_string[0], [app == "_", index_name]), "file_index")
