from time import time

from cothread.catools import caget # type: ignore
from numpy import array # type: ignore


def machineEnvironment(exp_data={}):
    """captures the environmental variables of the machine

    exp_data is a structure containing experimental data. The state of the
    machine is added to the structure and then returned.

    Example: exp_data = machine_environment(exp_data)
    """

    # timestamp
    exp_data["time"] = time()

    # General machine parameters
    # Ring mode
    exp_data["ringmode"] = caget("SR-CS-RING-01:MODE")
    # Machine current
    exp_data["current"] = caget("SR-DI-DCCT-01:SIGNAL")
    # Fill pattern
    exp_data["fill_pattern"] = caget("SR-DI-PICO-01:BUCKETS")

    # RF frequency
    exp_data["RF"] = caget("LI-RF-MOSC-01:FREQ")
    # Cavity voltages
    exp_data["cavity1_voltage"] = caget("SR-RF-LLRF-10:CAVVOLTAGE")
    # exp_data['cavity2_voltage'] = caget('SR-RF-LLRF-20:CAVVOLTAGE')
    exp_data["cavity3_voltage"] = caget("SR-RF-LLRF-30:CAVVOLTAGE")

    # getting the kicker status
    injection = caget("LI-TI-MTGEN-01:SRPREI-MODE")
    timing = caget("LI-TI-MTGEN-01:STATUS.DESC")
    if injection == "Off":
        exp_data["kicker_status"] = "off"
    elif injection == "Every shot":
        exp_data["kicker_status"] = "on"
    elif injection == "On LINAC-PRE":
        if timing == "Idle":
            exp_data["kicker_status"] = "off"
        else:
            exp_data["kicker_status"] = "on"

    else:
        exp_data["kicker_status"] = "unknown"

    # wiggler fields
    exp_data["wiggler_field_I15"] = caget("SR15I-ID-SCMPW-01:B_REAL")
    exp_data["wiggler_field_I12"] = caget("SR12I-CS-SCMPW-01:B")

    # capturing a sample pinhole image
    a = caget("SR01C-DI-DCAM-04:PROXY:DATA")
    alims = caget(["SR01C-DI-DCAM-04:WIDTH" "SR01C-DI-DCAM-04:HEIGHT"])
    # a = a(range(alims[0]) * alims[1])
    b = []
    for tmp in a:
        if tmp < 0:
            tmp = tmp + 256
        b.append(tmp)
    b = array(b)
    exp_data["pinhole"] = b.reshape(alims[0], alims[1])

    # Feedback status
    exp_data["orbit_feedback_status"] = caget("SR01A-CS-FOFB-01:RUN")
    exp_data["tune_feedback_status"] = caget("SR-CS-TFB-01:STATUS")

    # Emittance
    exp_data["emittance_h"] = caget("SR-DI-EMIT-01:HEMIT_MEAN")
    exp_data["emittance_v"] = caget("SR-DI-EMIT-01:VEMIT_MEAN")
    exp_data["coupling"] = caget("SR-DI-EMIT-01:COUPLING_MEAN")
    exp_data["espread"] = caget("SR-DI-EMIT-01:ESPREAD_MEAN")

    # Lifetime
    # Lifetime on main display chosen for lowest error.
    exp_data["lifetime"] = caget("SR-DI-DCCT-01:LIFETIME")
    exp_data["life"]["dcct"]["life30sec"] = caget("SR-DI-DCCT-01:LIFE30")
    exp_data["life"]["dcct"]["lifeerr30sec"] = caget("SR-DI-DCCT-01:ERROR30")
    exp_data["life"]["dcct"]["cond30sec"] = caget("SR-DI-DCCT-01:COND30")
    exp_data["life"]["dcct"]["life2min"] = caget("SR-DI-DCCT-01:LIFE120")
    exp_data["life"]["dcct"]["lifeerr2min"] = caget("SR-DI-DCCT-01:ERROR120")
    exp_data["life"]["dcct"]["cond2min"] = caget("SR-DI-DCCT-01:COND120")
    exp_data["life"]["dcct"]["life5min"] = caget("SR-DI-DCCT-01:LIFE300")
    exp_data["life"]["dcct"]["lifeerr5min"] = caget("SR-DI-DCCT-01:ERROR300")
    exp_data["life"]["dcct"]["cond5min"] = caget("SR-DI-DCCT-01:COND300")
    exp_data["life"]["dcct"]["life20min"] = caget("SR-DI-DCCT-01:LIFE1200")
    exp_data["life"]["dcct"]["lifeerr20min"] = caget("SR-DI-DCCT-01:ERROR1200")
    exp_data["life"]["dcct"]["cond20min"] = caget("SR-DI-DCCT-01:COND1200")

    exp_data["life"]["bpm"]["life300sec"] = caget("SR-DI-EBPM-01:LIFE300")
    exp_data["life"]["bpm"]["life300err"] = caget("SR-DI-EBPM-01:ERROR300")
    exp_data["life"]["bpm"]["cond300sec"] = caget("SR-DI-EBPM-01:COND300")
    exp_data["life"]["bpm"]["life120sec"] = caget("SR-DI-EBPM-01:LIFE120")
    exp_data["life"]["bpm"]["life120err"] = caget("SR-DI-EBPM-01:ERROR120")
    exp_data["life"]["bpm"]["cond120sec"] = caget("SR-DI-EBPM-01:COND120")
    exp_data["life"]["bpm"]["life30sec"] = caget("SR-DI-EBPM-01:LIFE30")
    exp_data["life"]["bpm"]["life30err"] = caget("SR-DI-EBPM-01:ERROR30")
    exp_data["life"]["bpm"]["cond30sec"] = caget("SR-DI-EBPM-01:COND30")
    exp_data["life"]["bpm"]["life10sec"] = caget("SR-DI-EBPM-01:LIFE10")
    exp_data["life"]["bpm"]["life10err"] = caget("SR-DI-EBPM-01:ERROR10")
    exp_data["life"]["bpm"]["cond10sec"] = caget("SR-DI-EBPM-01:COND10")

    # Injection
    exp_data["injection"]["btssr2s"] = caget("CS-DI-XFER-01:BS-SR2")
    exp_data["injection"]["btssr10s"] = caget("CS-DI-XFER-01:BS-SR10")
    exp_data["injection"]["boostsr2s"] = caget("CS-DI-XFER-01:BR-SR2")
    exp_data["injection"]["boostsr10s"] = caget("CS-DI-XFER-01:BR-SR10")

    # IDs
    exp_data["id"]["gap02"] = caget("SR02I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap02j"] = caget("SR02J-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap03"] = caget("SR03I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap04"] = caget("SR04I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap05"] = caget("SR05I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase05(1)"] = caget("SR05I-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase05(2)"] = caget("SR05I-MO-SERVO-07:MOT.RBV")
    exp_data["id"]["gap06a"] = caget("SR06I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase06a(1)"] = caget("SR06I-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase06a(2)"] = caget("SR06I-MO-SERVO-06:MOT.RBV")
    exp_data["id"]["gap06b"] = caget("SR06I-MO-SERVC-21:CURRGAPD")
    exp_data["id"]["phase06b(1)"] = caget("SR06I-MO-SERVO-25:MOT.RBV")
    exp_data["id"]["phase06b(2)"] = caget("SR06I-MO-SERVO-26:MOT.RBV")
    exp_data["id"]["gap07"] = caget("SR04I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap08"] = caget("SR08I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase08(1)"] = caget("SR08I-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase08(2)"] = caget("SR08I-MO-SERVO-07:MOT.RBV")
    exp_data["id"]["gap09i"] = caget("SR09I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap09j"] = caget("SR09J-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase09j(1)"] = caget("SR09J-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase09j(2)"] = caget("SR09J-MO-SERVO-06:MOT.RBV")
    exp_data["id"]["phase09j(3)"] = caget("SR09J-MO-SERVO-07:MOT.RBV")
    exp_data["id"]["phase09j(4)"] = caget("SR09J-MO-SERVO-08:MOT.RBV")
    exp_data["id"]["gap10a"] = caget("SR10I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase10a(1)"] = caget("SR10I-MO-SERVO-03:MOT.RBV")
    exp_data["id"]["phase10a(2)"] = caget("SR10I-MO-SERVO-04:MOT.RBV")
    exp_data["id"]["phase10a(3)"] = caget("SR10I-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase10a(4)"] = caget("SR10I-MO-SERVO-06:MOT.RBV")
    exp_data["id"]["gap10b"] = caget("SR10I-MO-SERVC-21:CURRGAPD")
    exp_data["id"]["phase10b(1)"] = caget("SR10I-MO-SERVO-23:MOT.RBV")
    exp_data["id"]["phase10b(2)"] = caget("SR10I-MO-SERVO-24:MOT.RBV")
    exp_data["id"]["phase10b(3)"] = caget("SR10I-MO-SERVO-25:MOT.RBV")
    exp_data["id"]["phase10b(4)"] = caget("SR10I-MO-SERVO-26:MOT.RBV")
    exp_data["id"]["gap11"] = caget("SR11I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["i12field"] = caget("SR12I-CS-SCMPW-01:B")
    exp_data["id"]["gap13i"] = caget("SR13I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap13j"] = caget("SR13J-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap14"] = caget("SR14I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["i15field"] = caget("SR15I-ID-SCMPW-01:B_REAL")
    exp_data["id"]["gap16"] = caget("SR16I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap18"] = caget("SR18I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap19"] = caget("SR19I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap20i"] = caget("SR20I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap20j"] = caget("SR20J-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap21"] = caget("SR21I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["phase21(1)"] = caget("SR21I-MO-SERVO-05:MOT.RBV")
    exp_data["id"]["phase21(2)"] = caget("SR21I-MO-SERVO-06:MOT.RBV")
    exp_data["id"]["phase21(3)"] = caget("SR21I-MO-SERVO-07:MOT.RBV")
    exp_data["id"]["phase21(4)"] = caget("SR21I-MO-SERVO-08:MOT.RBV")
    exp_data["id"]["gap22"] = caget("SR22I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap23"] = caget("SR23I-MO-SERVC-01:CURRGAPD")
    exp_data["id"]["gap24"] = caget("SR24I-MO-SERVC-01:CURRGAPD")

    exp_data["orbit_x"] = caget("SR-DI-EBPM-01:SA:X")
    exp_data["orbit_y"] = caget("SR-DI-EBPM-01:SA:Y")

    return exp_data
