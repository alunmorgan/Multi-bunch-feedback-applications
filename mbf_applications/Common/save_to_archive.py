from scipy.io import loadmat, savemat  # type: ignore

from mbf_applications.Common.construct_datastamped_filename import (
    constructDatastampedFilename,
)
from mbf_applications.Common.tree_gen import treeGen


def saveToArchive(root_string, data, graph_handles=None):
    """Saves the requested variables in the given filename in a location
    detemined by the time_value.
    The relavent folder structure will be generated.

    Example: save_to_archive(root_string, what_to_save)
    """

    # Generating the required directory structure.
    treeGen(root_string, data["time"])

    # construct filename and add it to the structure
    data["filename"] = constructDatastampedFilename(data["base_name"], data["time"])

    mth = data["time"][1]
    dy = data["time"][2]
    if mth < 10:
        mth = "".join(("0", mth))

    if dy < 10:
        dy = "".join(("0", dy))

    save_name = os.path.join(
        root_string, data["time"][0], mth, dy, "".join((data["filename"], ".mat"))
    )
    savemat(save_name, data)
    if not graph_handles is None:
        for heaq in range(len(graph_handles)):
            if ishandle(graph_handles(heaq)):
                graph_save_name = os.path.join(
                    root_string, data["time"][0], mth, dy, data["filename"]
                )
                saveas(
                    graph_handles(heaq),
                    "".join((graph_save_name, "_figure_", heaq, ".png")),
                )
                saveas(
                    graph_handles(heaq),
                    "".join((graph_save_name, "_figure_", heaq, ".fig")),
                )

    print("".join(("Data saved to:  ", save_name)))

    index_name = "".join((data["base_name"], "_index"))
    loadmat(os.path.join(root_string, index_name, file_index))
    file_index[0].append(save_name)
    file_index[1].append(data["time"])
    savemat(os.path.join(root_string, index_name, file_index))
    print("Index updated")
