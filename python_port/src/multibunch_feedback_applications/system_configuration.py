import datetime

import numpy as np
from common import get_all_tunes, get_variable


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
    # Base PVs of the hardware.
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
    triggers = {}
    triggers["mode"] = ":TRG:SEQ:MODE_S"
    triggers["arm"] = ":TRG:SEQ:ARM_S.PROC"
    pv_names["trigger_inputs"] = {"SOFT", "EXT", "PM", "ADC0", "ADC1", "SEQ0", "SEQ1"}
    for trigger_ind in range(1, len(pv_names["trigger_inputs"])):
        trigger = pv_names["trigger_inputs"][trigger_ind]
        triggers[trigger]["enable_status"] = f":TRG:SEQ:{trigger}:EN_S"
        triggers[trigger]["blanking_status"] = f":TRG:SEQ:{trigger}:BL_S"

    for trigger_ind in range(1, len(pv_names["trigger_inputs"])):
        trigger = pv_names["trigger_inputs"][trigger_ind]
        triggers["MEM"][trigger]["enable_status"] = f":TRG:MEM:{trigger}:EN_S"
        triggers["MEM"][trigger]["blanking_status"] = f":TRG:MEM:{trigger}:BL_S"

    triggers["SEQ"]["arm"] = ":TRG:SEQ:ARM_S.PROC"
    triggers["SEQ"]["disarm"] = ":TRG:SEQ:DISARM_S.PROC"
    triggers["SEQ"]["mode"] = ":TRG:SEQ:MODE_S"
    triggers["SEQ"]["delay"] = ":TRG:SEQ:DELAY_S"
    # shared with other axis
    # NEED TO TAKE OFF THE X|Y BEFORE USE
    triggers["MEM"]["arm"] = ":TRG:MEM:ARM_S.PROC"
    triggers["MEM"]["disarm"] = ":TRG:MEM:DISARM_S.PROC"
    triggers["MEM"]["mode"] = ":TRG:MEM:MODE_S"
    triggers["MEM"]["delay"] = ":TRG:MEM:DELAY_S"
    triggers["soft"] = ":TRG:SOFT_S.PROC"
    triggers["soft_settings"] = ":TRG:SOFT_S.SCAN"
    triggers["shared"] = ":TRG:MODE_S"
    triggers["blanking_length"] = ":TRG:BLANKING_S"

    pv_names["tails"]["triggers"] = triggers
    ## Super Sequencer settings
    # FIXME should only have one set of calls here.
    pv_names["tails"]["Super_sequencer_count"] = ":SEQ:SUPER:COUNT_S"
    pv_names["tails"]["Super_sequencer_reset"] = ":SEQ:SUPER:RESET_S.PROC"
    pv_names["tails"]["Super_sequencer"]["count"] = ":SEQ:SUPER:COUNT_S"
    pv_names["tails"]["Super_sequencer"]["reset"] = ":SEQ:SUPER:RESET_S.PROC"
    ## Sequencer settings
    # applies to all
    sequencer = {}
    sequencer["start_state"] = ":SEQ:PC_S"
    sequencer["steady_state_bank"] = ":SEQ:0:BANK_S"
    sequencer["reset"] = ":SEQ:RESET_S.PROC"
    for n_seq in range(1, 8):
        l_seq = f"seq{n_seq}"
        sequencer[l_seq]["start_frequency"] = f":SEQ:{n_seq}:START_FREQ_S"
        sequencer[l_seq]["end_frequency"] = f":SEQ:{n_seq}:END_FREQ_S"
        sequencer[l_seq]["turns"] = f":SEQ:{n_seq}:COUNT_S"
        sequencer[l_seq]["dwell"] = f":SEQ:{n_seq}:DWELL_S"
        sequencer[l_seq]["gain"] = f":SEQ:{n_seq}:GAIN_S"
        sequencer[l_seq]["gaindb"] = f":SEQ:{n_seq}:GAIN_DB_S"
        sequencer[l_seq]["enable"] = f":SEQ:{n_seq}:ENABLE_S"
        sequencer[l_seq]["step_frequency"] = f":SEQ:{n_seq}:STEP_FREQ_S"
        sequencer[l_seq]["holdoff"] = f":SEQ:{n_seq}:HOLDOFF_S"
        sequencer[l_seq]["bank_select"] = f":SEQ:{n_seq}:BANK_S"
        sequencer[l_seq]["capture_state"] = f":SEQ:{n_seq}:CAPTURE_S"
        sequencer[l_seq]["windowing_state"] = f":SEQ:{n_seq}:ENWIN_S"
        sequencer[l_seq]["blanking_state"] = f":SEQ:{n_seq}:BLANK_S"
        sequencer[l_seq]["holdoff_state"] = f":SEQ:{n_seq}:STATE_HOLDOFF_S"
        sequencer[l_seq]["tune_pll_following"] = f":SEQ:{n_seq}:TUNE_PLL_S"
    pv_names["tails"]["Sequencer"] = sequencer

    ## Bank settings
    bbank = {}
    for n_bank in range(4):
        l_bank = f"bank{n_bank}"
        bbank[l_bank]["Output_types"] = f":BUN:{n_bank}:OUTWF_S"
        bbank[l_bank]["bunch_select"] = f":BUN:{n_bank}:BUNCH_SELECT_S"
        bbank[l_bank]["FIR"]["enablewf"] = f":BUN:{n_bank}:FIR:ENABLE_S"
        bbank[l_bank]["FIR"]["set_enable"] = f":BUN:{n_bank}:FIR:SET_ENABLE_S.PROC"
        bbank[l_bank]["FIR"]["set_disable"] = f":BUN:{n_bank}:FIR:SET_DISABLE_S.PROC"
        bbank[l_bank]["FIR"]["gainwf"] = f":BUN:{n_bank}:FIR:GAIN_S"
        bbank[l_bank]["FIR"]["gainswfdb"] = f":BUN:{n_bank}:FIR:GAIN_DB"
        #     Select which filter to use on which bunch
        bbank[l_bank]["FIR"]["selectwf"] = f":BUN:{n_bank}:FIRWF_S"
        bbank[l_bank]["FIR"]["set_select"] = f":BUN:{n_bank}:FIRWF_SET_S.PROC"
        bbank[l_bank]["NCO1"]["enablewf"] = f":BUN:{n_bank}:NCO1:ENABLE_S"
        bbank[l_bank]["NCO1"]["set_enable"] = f":BUN:{n_bank}:NCO1:SET_ENABLE_S.PROC"
        bbank[l_bank]["NCO1"]["set_disable"] = f":BUN:{n_bank}:NCO1:SET_DISABLE_S.PROC"
        bbank[l_bank]["NCO1"]["gainswf"] = f":BUN:{n_bank}:NCO1:GAIN_S"
        bbank[l_bank]["NCO1"]["gainswfdb"] = f":BUN:{n_bank}:NCO1:GAIN_DB"
        bbank[l_bank]["NCO2"]["enablewf"] = f":BUN:{n_bank}:NCO2:ENABLE_S"
        bbank[l_bank]["NCO2"]["set_enable"] = f":BUN:{n_bank}:NCO2:SET_ENABLE_S.PROC"
        bbank[l_bank]["NCO2"]["set_disable"] = f":BUN:{n_bank}:NCO2:SET_DISABLE_S.PROC"
        bbank[l_bank]["NCO2"]["gainswf"] = f":BUN:{n_bank}:NCO2:GAIN_S"
        bbank[l_bank]["NCO2"]["gainswfdb"] = f":BUN:{n_bank}:NCO2:GAIN_DB"
        bbank[l_bank]["SEQ"]["enablewf"] = f":BUN:{n_bank}:SEQ:ENABLE_S"
        bbank[l_bank]["SEQ"]["set_enable"] = f":BUN:{n_bank}:SEQ:SET_ENABLE_S.PROC"
        bbank[l_bank]["SEQ"]["set_disable"] = f":BUN:{n_bank}:SEQ:SET_DISABLE_S.PROC"
        bbank[l_bank]["SEQ"]["gainswf"] = f":BUN:{n_bank}:SEQ:GAIN_S"
        bbank[l_bank]["SEQ"]["gainswfdb"] = f":BUN:{n_bank}:SEQ:GAIN_DB"
        bbank[l_bank]["PLL"]["enablewf"] = f":BUN:{n_bank}:PLL:ENABLE_S"
        bbank[l_bank]["PLL"]["set_enable"] = f":BUN:{n_bank}:PLL:SET_ENABLE_S.PROC"
        bbank[l_bank]["PLL"]["set_disable"] = f":BUN:{n_bank}:PLL:SET_DISABLE_S.PROC"
        bbank[l_bank]["PLL"]["gainswf"] = f":BUN:{n_bank}:PLL:GAIN_S"
        bbank[l_bank]["PLL"]["gainswfdb"] = f":BUN:{n_bank}:PLL:GAIN_DB"

    pv_names["tails"]["Bunch_bank"] = bbank

    ## Detector settings
    # applies to all
    detector = {}
    detector["source"] = ":DET:SELECT_S"
    detector["fill_waveforms"] = ":DET:FILL_WAVEFORMS_S"
    detector["fir_delay"] = ":DET:FIR_DELAY_S"
    for n_det in range(4):
        l_det = ["det", n_det]
        detector[l_det]["enable"] = f":DET:{n_det}:ENABLE_S"
        detector[l_det]["bunch_selection"] = f":DET:{n_det}:BUNCHES_S"
        detector[l_det]["scale"] = f":DET:{n_det}:SCALING_S"
        detector[l_det]["I"] = f":DET:{n_det}:I"
        detector[l_det]["Q"] = f":DET:{n_det}:Q"
        detector[l_det]["power"] = f":DET:{n_det}:POWER"
        detector[l_det]["bunch_select"] = f":DET:{n_det}:BUNCH_SELECT_S"
        detector[l_det]["reset_selection"] = f":DET:{n_det}:RESET_SELECT_S.PROC"
        detector[l_det]["set_selection"] = f":DET:{n_det}:SET_SELECT_S.PROC"

    pv_names["tails"]["Detector"] = detector

    ## Memory settings
    # NEED TO TAKE OFF THE X|Y BEFORE USE.
    memory = {}
    memory["status"] = ":MEM:BUSY"
    memory["channel_select"] = ":MEM:SELECT_S"
    memory["offset"] = ":MEM:OFFSET_S"
    memory["runout"] = ":MEM:RUNOUT_S"
    memory["channel0_target"] = ":MEM:SEL0_S"
    memory["channel1_target"] = ":MEM:SEL1_S"
    pv_names["tails"]["MEM"] = memory

    pv_names["tails"]["TRG"]["memory_status"] = ":TRG:MEM:STATUS"
    ## NCO settings
    for n_nco in range(1, 3):
        l_nco = ["NCO", n_nco]
        pv_names["tails"][l_nco]["frequency"] = f":NCO{n_nco}:FREQ_S"
        pv_names["tails"][l_nco]["gain"] = f":NCO{n_nco}:GAIN_S"
        pv_names["tails"][l_nco]["gain_scalar"] = f":NCO{n_nco}:GAIN_SCALAR_S"
        pv_names["tails"][l_nco]["gaindb"] = f":NCO{n_nco}:GAIN_DB_S"
        pv_names["tails"][l_nco]["enable"] = f":NCO{n_nco}:ENABLE_S"
        pv_names["tails"][l_nco]["PLL_follow"] = f":NCO{n_nco}:TUNE_PLL_S"

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
    pll = {}
    pll["detector"]["dwell"] = ":PLL:DET:DWELL_S"
    pll["detector"]["target_bunches"] = ":PLL:DET:BUNCHES_S"
    pll["detector"]["mode"] = ":PLL:DET:SELECT_S"
    pll["detector"]["scaling"] = ":PLL:DET:SCALING_S"
    pll["detector"]["blanking"] = ":PLL:DET:BLANKING_S"
    pll["detector"]["dwell"] = ":PLL:DET:DWELL_S"
    pll["nco"]["enable"] = ":PLL:NCO:ENABLE_S"
    pll["nco"]["gain"] = ":PLL:NCO:GAIN_DB_S"
    pll["nco"]["set_frequency"] = ":PLL:NCO:FREQ_S"
    pll["nco"]["frequency"] = ":PLL:NCO:FREQ"
    pll["nco"]["offset_waveform"] = ":PLL:NCO:OFFSETWF"
    pll["nco"]["mean_offset"] = ":PLL:NCO:MEAN_OFFSET"
    pll["nco"]["std_offset"] = ":PLL:NCO:STD_OFFSET"
    pll["nco"]["offset"] = ":PLL:NCO:OFFSET"
    pll["nco"]["tune"] = ":PLL:NCO:TUNE"
    pll["start"] = ":PLL:CTRL:START_S.PROC"
    pll["stop"] = ":PLL:CTRL:STOP_S.PROC"
    pll["p"] = ":PLL:CTRL:KP_S"
    pll["i"] = ":PLL:CTRL:KI_S"
    pll["target_phase"] = ":PLL:CTRL:TARGET_S"
    pll["minumum_magnitude"] = ":PLL:CTRL:MIN_MAG_S"
    pll["maximum_offset"] = ":PLL:CTRL:MAX_OFFSET_S"
    pll["status"] = ":PLL:CTRL:STATUS"
    pll["readback"]["magnitude"] = ":PLL:FILT:MAG"
    pll["readback"]["phase"] = ":PLL:FILT:PHASE"
    pll["readback"]["i"] = ":PLL:FILT:I"
    pll["readback"]["q"] = ":PLL:FILT:Q"
    pll["stop_reasons"]["stop"] = ":PLL:CTRL:STOP:STOP"
    pll["stop_reasons"]["detector_overflow"] = ":PLL:CTRL:STOP:DET_OVF"
    pll["stop_reasons"]["offset_overflow"] = ":PLL:CTRL:STOP:OFFSET_OVF"
    pll["stop_reasons"]["magnitude_error"] = ":PLL:CTRL:STOP:MAG_ERROR"
    pv_names["tails"]["pll"] = pll
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
