import csv
import datetime
import os

import numpy as np
import scipy
from cothread.catools import FORMAT_TIME, caget, caput

from Operational_codes.hardware_setup import get_all_tunes


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


def condition_mbf_metadata(input_data: list[dict]) -> list[dict]:
    """Mapping values in old datasets to defined variables."""
    output_data = input_data
    for jgr in range(len(input_data)):
        if "gddata" in input_data[jgr]:
            output_data[jgr]["data"] = input_data[jgr]["gddata"]

        if "gddata_freq" in input_data[jgr]:
            output_data[jgr]["data_freq"] = input_data[jgr]["gddata_freq"]

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


def construct_datastamped_filename(name_str: str, c: datetime.datetime) -> str:
    """constructs a datestamped filename
    name_str is a identifier string added at the begining of the name.
    c is a datetime object.

    example filename = construct_filename('MBF', clock)
    """
    filename = f"{name_str}_{c.day: 02d}_{c.month:02d}_{c.year}_{c.hour: 02d}-{c.minute: 02d}-{c.second: 02d}"
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


def machine_environment():
    """captures the environmental variables of the machine

    Example: exp_data = machine_environment()
    """
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
    injection = get_variable["LI-TI-MTGEN-01:SRPREI-MODE"]
    timing = get_variable["LI-TI-MTGEN-01:STATUS.DESC"]
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
    a = np.reshape(a, alims(1), [])
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


def system_config():
    # root_path is the location for captured data.
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
        ":MEM:BUSY"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
    )
    pv_names["tails"]["MEM"]["channel_select"] = (
        ":MEM:SELECT_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
    )
    pv_names["tails"]["MEM"]["offset"] = (
        ":MEM:OFFSET_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
    )
    pv_names["tails"]["MEM"]["runout"] = (
        ":MEM:RUNOUT_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
    )
    pv_names["tails"]["MEM"]["channel0_target"] = (
        ":MEM:SEL0_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
    )
    pv_names["tails"]["MEM"]["channel1_target"] = (
        ":MEM:SEL1_S"  # NEED TO TAKE OFF THE X|Y BEFORE USE.
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
    # FIXME index files need to be csv rather than mat.
    file_index = []
    print(["Data saved to: , ", save_name])
    index_name = f"{data['base_name']}_index"
    if os.path.isfile(os.path.join(root_string, f"{index_name}.csv")):
        with open(
            os.path.join(root_string, f"{index_name}.csv"), "rw", newline=""
        ) as csvfile:
            f = csv.reader(csvfile, delimiter=",")
            f.append([save_name, data["time"].strftime("%a %d %b %Y, %I:%M%p")])
            fw = csv.writer(csvfile, delimiter=",")
            fw.writerows(f)

        print("Index updated")
    else:
        file_index[1][1] = save_name
        file_index[2][1] = data["time"].strftime("%a %d %b %Y, %I:%M%p")
        scipy.savemat(
            os.path.join(root_string, f"{index_name}.mat"), "file_index", "-v7.3"
        )
        print("New index file created")


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


def sub_directories(main_dir: os.PathLike[str]) -> list[str]:
    """outputs a list of sub-directories of the input directory

    example: sub_dir = sub_directories(main_dir)
    """
    # finding the subdirectories
    sub_dirs = [entry for entry in main_dir.iterdir() if entry.is_dir()]

    return sub_dirs


def tree_gen(tree_root: os.PathLike[str], clk: datetime.datetime):
    """generates a directory structure using the datetime passed in as clk
    tree_root is where you want the subdirectories to be placed."""

    leaf = os.path.join(tree_root, f"{clk.year}", f"{clk.month: 02d}", f"{clk.day:02d}")

    # generating directory tree
    if not os.path.isdir(leaf):
        os.makedirs(leaf)


def mbf_make_index(application_type: str, ax: str):
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
    wanted_datasets_type = datasets(
        find_position_in_cell_lst(strfind(datasets, filter_name))
    )
    print(f"Creating lookup index for {application_type} {ax}")
    if not wanted_datasets_type:
        print("No files to index")
    else:
        ok = np.zeros(len(wanted_datasets_type))
        file_time: list = []
        file_name: list[str] = []
        for kse in range(1, len(wanted_datasets_type)):
            try:  # handling corrupted input files
                temp = os.load(wanted_datasets_type[kse])
            except me1:
                ok[kse] = 0
                print(f"{me1} message")

            data_name = temp.keys()
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
