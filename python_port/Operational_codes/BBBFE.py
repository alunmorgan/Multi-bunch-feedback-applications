import datetime
import re
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy
from Growdamp import mbf_analysis_reorganise_for_parameter_sweep

from Common import (
    get_variable,
    machine_environment,
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
    mbf_archival_plotting_setup,
    mbf_system_config,
    populate_archive_graph,
    save_to_archive,
    set_variable,
    setup_operational_mode,
)


def BBBFE_LO_scan(phase_centre, sweep_extent):
    # Scans the LO phase shift in the bunch by bunch frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #     phase_centre (int): The phase value to center the sweep on.
    #     sweep_extent (int): The range to sweep. 45 would sweep 45 degrees
    #                         above and 45 degrees below the centre value.
    #
    # Example: BBBFE_LO_scan(90, 45)
    root_string = mbf_system_config
    data = []
    data["phase_pv"] = "SR23C-DI-BBFE-01:PHA"
    old_val = get_variable(data["phase_pv"])
    data["n"] = range(
        phase_centre - sweep_extent,
        phase_centre + sweep_extent,
        np.ceil(sweep_extent / 20),
    )
    data["t1"] = []
    data["t2"] = []
    data["t3"] = []
    for jd in range(len(data["n"])):
        set_variable(data["phase_pv"], data["n"](jd))
        time.sleep(2)
        data["t1"][jd] = max(get_variable("SR23C-DI-TMBF-01:TUNE:POWER"))
        data["t2"][jd] = max(get_variable("SR23C-DI-TMBF-02:TUNE:POWER"))
        data["t3"][jd] = max(get_variable("SR23C-DI-TMBF-03:TUNE:POWER"))

    set_variable(data["phase_pv"], old_val)
    graph_handles = plt.figure
    plt.plt.plot(
        data["n"],
        data["t1"][""] / max(data["t1"]),
        "b",
        data["n"],
        data["t2"][""] / max(data["t2"]),
        "r",
        data["n"],
        data["t3"][""] / max(data["t3"]),
        "c",
    )
    plt.plt.xlabel("LO phase (degrees)")
    plt.plt.ylabel("tune max value (normalised)")
    plt.plt.legend("X", "Y", "S")
    data["time"] = datetime.datetime.now()
    data["base_name"] = "LO_scan"
    ## saving the data to a file
    save_to_archive(root_string, data, graph_handles)


def BBBFE_bunch_phase_variation_simulation(mbf_axis):
    # This def moves the phase between -60 and +60 around the nominal phase['']:
    # a gain ramp across the train is established using the FIR['']
    # For each phase value various DAC outputs are captured['']
    # The idea of this is to simulate the impact of a phase gradient across the
    # bunch train['']
    [_1, harmonic_number, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    bbbfe_vars = pv_names["frontend"]
    sig = {}
    fir_wf = get_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank0']['FIR']['gainwf']}"
    )
    # put a ramp pattern on the FIR between 0 and 1
    sig["fir_ramp"] = np.linspace(0, 1, harmonic_number)
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank0']['FIR']['gainwf']}",
        sig["fir_ramp"],
    )
    # adjust the phase on the frontend between 0 and 60 in 10 degree steps['']
    starting_phase = get_variable(
        [bbbfe_vars["base"], bbbfe_vars["system_phase"][mbf_axis]]
    )
    print(["Starting phase:, ", starting_phase])
    sig["phase_sweep"] = np.linspace(starting_phase - 60, starting_phase + 60, 12)
    for phase_ind in range(len(sig["phase_sweep"])):
        # capture the DAC output
        set_variable(
            f"{bbbfe_vars['base']}{bbbfe_vars['system_phase'][mbf_axis]}",
            sig["phase_sweep"](phase_ind),
        )
        time.sleep(5)  # HOW LONG?
        sig["delta"][phase_ind, :] = get_variable(
            f"{mbf_names[mbf_axis], mbf_vars['dac']['delta']}"
        )
        sig["max"][phase_ind, :] = get_variable(
            f"{mbf_names[mbf_axis], mbf_vars['dac']['max']}"
        )
        sig["mean"][phase_ind, :] = get_variable(
            f"{mbf_names[mbf_axis], mbf_vars['dac']['mean']}"
        )
        sig["min"][phase_ind, :] = get_variable(
            f"{mbf_names[mbf_axis], mbf_vars['dac']['min']}"
        )
        sig["std"][phase_ind, :] = get_variable(
            f"{mbf_names[mbf_axis], mbf_vars['dac']['std']}"
        )
        time.sleep(5)  # HOW LONG?

    # Put the phase back to the starting phase
    set_variable(
        f"{bbbfe_vars['base']}{bbbfe_vars['system_phase'][mbf_axis]}", starting_phase
    )
    # Remove the ramp from the FIR
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank0']['FIR']['gainwf']}",
        fir_wf,
    )
    return sig


def BBBFE_clock_phase_scan(
    mbf_ax,
    single_bunch_location,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    sweep_start=-180,
    sweep_step=10,
    sweep_end=180,
):
    # Scans one of the clock phase shifts in the bunch by bunch frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #      ax (str): Specifies which axis.
    #      single_bunch_location (int): the location of the single bunch.
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): phase value in degrees to start the sweep.
    #       sweep_step(int):  phase scan step in degrees.
    #       sweep_end(int):   phase value in degreees to stop the sweep.
    #
    #
    # Machine setup: (manual for the time being.)
    # fill some charge in bunch 1 (0['2nC'])
    #
    # Example: BBBFE_clock_phase_scan('x', 400)
    [root_string, _1, pv_names] = mbf_system_config
    detector = pv_names["tails"]["Detector"]
    frontend = pv_names["frontend"]["base"]
    clock_phases = pv_names["frontend"]["clock_phase"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    adc = pv_names["tails"]["adc"]
    # for archival investigations this allows filtering by machine state.
    # but for capture this is not needed so it set to empty.
    filter_conditions = []
    mbf_pv = pv_names["hardware_names"][mbf_ax]
    fe_phase_pv = f"{frontend}{clock_phases[mbf_ax]}"
    # getting general environment data.
    data = machine_environment
    # Add the extra data to the data structure.
    data["base_name"] = f"clock_phase_scan_{mbf_ax}_axis"
    data["original_setting"] = get_variable(fe_phase_pv)
    data["orig_gain"] = get_variable(f"{mbf_pv}{sequencer1['gaindb']}")
    data["mbf_ax"] = mbf_ax
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end

    # set up the sweep
    data["phase"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["phase"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"],
            -data["sweep_step"],
        )
    )
    # prealloacation
    data["side1"] = []
    data["main"] = []
    data["side2"] = []
    data["adc_phase"] = []
    if auto_setup == "yes":
        original_detector_setup = BBBFE_detector_setup(mbf_ax, single_bunch_location)
        setup_operational_mode(mbf_ax, "TuneOnly")

    # moving to starting point in scan
    for pp in range[data["original_setting"] : -sweep_step, sweep_start]:
        set_variable(fe_phase_pv, pp)
        time.sleep(["5"])

    for x in range(len(data["phase"])):
        set_variable(fe_phase_pv, data["phase"][x])
        time.sleep(0["5"])
        data["side1"][x] = max(get_variable(f"{mbf_pv}{detector['det1']['power']}"))
        data["main"][x] = max(get_variable(f"{mbf_pv}{detector['det2']['power']}"))
        data["side2"][x] = max(get_variable(f"{mbf_pv}{detector['det3']['power']}"))
        if mbf_ax.lower() == "s":
            data["adc_phase"][x] = max(get_variable(f"{mbf_pv}{adc['phase']['mean']}"))
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['min']}"))
            data["adc_meanQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['mean']}"))
            data["adc_maxQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['max']}"))
            data["adc_minQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['min']}"))
        else:
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv}{adc['min']}"))

    # move back to the original setting
    for pp in range[data["sweep_start"] : data["sweep_step"], data["original_setting"]]:
        set_variable(fe_phase_pv, pp)
        time.sleep(["5"])

    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")
        BBBFE_detector_restore(mbf_ax, original_detector_setup)
        set_variable([mbf_pv, sequencer1["gaindb"]], data["orig_gain"])

    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## plotting
    if plotting == "yes":
        mbf_frontend_clock_phase_scan_archival_retrieval(
            mbf_ax, [data["time"], data["time"]], filter_conditions
        )


def BBBFE_clock_phase_scan_plotting(data):
    temp = re.findall("[]*_([xys])_axis$", data["base_name"])
    mbf_ax = temp[0]
    graph_name = data["base_name"].replace("_", " ")
    # plotting
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )

    instructions = (
        "The excited bunch signal should be as high as possible "
        "while maximising the signal differences."
    )
    fig.supplt.title(
        f"BBBFE '{graph_name} axis on {data['time'].strftime('%a %d %b %Y, %I:%M%p')}"
    )
    fig.subplt.title(instructions, "FontAngle", "italic", "FontSize", 10)
    plt.xlabel("phase (degrees)")
    plt.semilogy(data["phase"], data["main"], "DisplayName", "Excited bunch")
    plt.semilogy(data["phase"], data["side1"], "DisplayName", "Preceeding bunch")
    plt.semilogy(data["phase"], data["side2"], "DisplayName", "Following bunch")
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("Signal")
    plt.semilogy(
        data["phase"],
        data["main"] - data["side1"],
        "DisplayName",
        "Excited bunch - Preceeding bunch",
    )
    plt.semilogy(
        data["phase"],
        data["main"] - data["side2"],
        "DisplayName",
        "Excited bunch - Following bunch",
    )
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("Signal differences")
    plt.semilogy(data["phase"], data["adc_mean"], "DisplayName", "ADC amplitude")
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("ADC amplitude")
    if mbf_ax == "s":
        plt.semilogy(data["phase"], data["adc_phase"], "DisplayName", "ADC phase")
        add_original_values(mbf_ax, data)
        plt.legend("Location", "Best")
        plt.ylabel("ADC phase")


def add_original_values(mbf_ax, data):
    extents_y = []  # get(gca, 'YLim') #FIXME
    if "original_setting" in data:
        if mbf_ax.lower() == "s" and "original_settingQ" in data:
            plt.plot(
                [data["original_setting"], data["original_setting"]],
                extents_y,
                "r:",
                "DisplayName",
                "Original setting(I)",
                "LineWidth",
                2,
            )
            plt.plot(
                [data["original_settingQ"], data["original_settingQ"]],
                extents_y,
                "c:",
                "DisplayName",
                "Original setting(Q)",
                "LineWidth",
                2,
            )
        else:
            plt.plot(
                [data["original_setting"], data["original_setting"]],
                extents_y,
                "r:",
                "DisplayName",
                "Original setting",
                "LineWidth",
                2,
            )


def BBBFE_detector_restore(mbf_axis, detector_setup):
    mbf_axis = mbf_axis.lower()
    [_2, _1, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    detector = pv_names["tails"]["Detector"]
    # set up the individual tune detectors to run on 1,2,3
    for ms in range(1, 3):
        det_name = f"det{ms}"
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['enable']}",
            detector_setup[det_name]["enable"],
        )
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['scale']}",
            detector_setup[det_name]["scale"],
        )
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['bunch_select']}", "0:935"
        )
        set_variable(f"{mbf_names[mbf_axis]}{detector[det_name]['reset_selection']}", 1)
        set_variable(
            f"{mbf_names[mbf_axis]}{detector[det_name]['bunch_select']}",
            detector_setup[det_name]["bunch_select"][1],
        )
        set_variable(f"{mbf_names[mbf_axis]}{detector[det_name]['set_selection']}", 1)


def BBBFE_detector_setup(mbf_axis, single_bunch_location):
    [_2, _1, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    detector = pv_names["tails"]["Detector"]
    if single_bunch_location == 0:
        prior_bunch = 935
    else:
        prior_bunch = single_bunch_location - 1

    # read the existing detector states
    detector_setup = {}
    for ms in range(3):
        detector_setup[f"det{ms}"]["enable"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["enable"]]
        )
        detector_setup[f"det{ms}"]["scale"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["scale"]]
        )
        detector_setup[f"det{ms}"]["bunch_select"] = get_variable(
            [mbf_names[mbf_axis], detector[""](["det", (ms)])["bunch_select"]]
        )

    # set up the individual tune detectors to run on 1,2,3
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det1']['bunch_select']}", prior_bunch
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det1']['set_selection']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det2']['bunch_select']}",
        (single_bunch_location),
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det2']['set_selection']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['enable']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['scale']}", 0)
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['bunch_select']}", "0:935")
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['reset_selection']}", 1)
    set_variable(
        f"{mbf_names[mbf_axis]}{detector['det3']['bunch_select']}",
        (single_bunch_location + 1),
    )
    set_variable(f"{mbf_names[mbf_axis]}{detector['det3']['set_selection']}", 1)
    # set sweep gain to -18
    set_variable(
        [mbf_names[mbf_axis], pv_names["tails"]["Sequencer"]["seq1"]["gaindb"]], "-18"
    )
    # set detector fixed gain
    return detector_setup


def BBBFE_full_frontend_checkout(single_bunch_location):
    # BBBFE_FULL_FRONTEND_CHECKOUT
    # This assumes that the machine is set up with a single bunch in the machine at
    # the single_bunch_location
    BBBFE_system_phase_scan("x", single_bunch_location)
    BBBFE_system_phase_scan("y", single_bunch_location)
    BBBFE_system_phase_scan("s", single_bunch_location)
    BBBFE_clock_phase_scan("x", single_bunch_location)
    BBBFE_clock_phase_scan("y", single_bunch_location)
    BBBFE_clock_phase_scan("s", single_bunch_location)


def BBBFE_gain_scan(
    mbf_ax,
    single_bunch_location,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    sweep_start=-40,
    sweep_step=5,
    sweep_end=10,
    sweep_speed=2,
):
    # Scans one of the individual axis gains in the
    # bunch by bunch frontend and records the strength of the ADC signal.
    # Restores the original value after the scan.
    #
    # Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): level value to start the sweep.
    #       sweep_step(int):  level step.
    #       sweep_end(int):   level value to stop the sweep.
    #
    # Machine setup
    # machine to nominal conditions
    #
    # Example: BBBFE_gain_scan('x')
    [root_string, _1, pv_names] = mbf_system_config
    adc = pv_names["tails"]["adc"]
    frontend = pv_names["frontend"]["base"]
    fe_gain = pv_names["frontend"]["gain"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    mbf_pv = pv_names["hardware_names"][mbf_ax]
    fe_gain_pv = f"{frontend}{fe_gain[mbf_ax]}"
    # for archival investigations this allows filtering by machine state.
    # but for capture this is not needed so it set to empty.
    filter_conditions = []
    # getting general environment data.
    data = machine_environment
    # Add the extra data to the data structure.
    data["ax_label"] = mbf_ax
    data["base_name"] = ["frontend_gain_scan_", mbf_ax, "_axis"]
    data["orig_gain"] = get_variable([mbf_pv, sequencer1["gaindb"]])
    data["original_setting"] = get_variable(fe_gain_pv)
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed

    # set up the sweep
    data["gain"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["gain"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"],
            -data["sweep_step"],
        )
    )
    # prealloacation
    data["adc_mean"] = []
    data["adc_max"] = []
    data["adc_min"] = []
    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")

    # moving to starting point in scan
    for pp in range[data["original_setting"] : -sweep_step, sweep_start]:
        set_variable(fe_gain_pv, pp)
        time.sleep(["5"])

    # measurement
    for x in range(len(data["gain"])):
        set_variable(fe_gain_pv, data["gain"][x])
        time.sleep(sweep_speed)
        data["adc_mean"][x] = max(get_variable([mbf_pv, adc["mean"]]))
        data["adc_max"][x] = max(get_variable([mbf_pv, adc["max"]]))
        data["adc_min"][x] = max(get_variable([mbf_pv, adc["min"]]))

    # move back to the original setting
    for pp in range[data["sweep_start"] : data["sweep_step"], data["original_setting"]]:
        set_variable(fe_gain_pv, pp)
        time.sleep(["5"])

    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")
        set_variable(f"{mbf_pv}{sequencer1['gaindb']}", data["orig_gain"])

    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## Plotting data
    if plotting == "yes":
        mbf_frontend_gain_scan_archival_retrieval(
            mbf_ax, [data["time"], data["time"]], filter_conditions
        )


def BBBFE_gain_scan_plotting(data):
    graph_name = data["base_name"].replace("_", " ")
    # plotting
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    instructions = (
        "The excited bunch signal should be as high as possible "
        "while maximising the signal differences"
    )
    fig.supplt.title(
        f"BBBFE {graph_name} axis on {data['time'].strftime('%a %d %b %Y, %I:%M%p')}"
    )
    fig.subplt.title(instructions, "FontAngle", "italic", "FontSize", 10)
    fig.xlabel("phase (degrees)")
    plt.semilogy(data["gain"], data["adc_mean"], "DisplayName", "ADC mean")
    plt.semilogy(data["gain"], data["adc_max"], "DisplayName", "ADC max")
    plt.semilogy(data["gain"], data["adc_min"], "DisplayName", "ADC min")
    if "original_setting" in data:
        extents_y = []  # get(gca, "YLim") #FIXME
        plt.plot(
            [data["original_setting"], data["original_setting"]],
            extents_y,
            "r:",
            "DisplayName",
            "Original setting",
            "LineWidth",
            2,
        )

    fig.ylabel("Signal")


def BBBFE_system_phase_scan(
    mbf_ax,
    single_bunch_location,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    sweep_start=-180,
    sweep_step=10,
    sweep_end=180,
    sweep_speed=2,
):
    # Scans one of the individual axis system phase shifts in the
    # bunch by bunch frontend and records the strength of the tune signal['']
    # Restores the original value after the scan['']
    #
    # Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       single_bunch_location(int): location of the target bunch['']
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes['']
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes['']
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive['']
    #       sweep_start(int): phase value in degrees to start the sweep['']
    #       sweep_step(int):  phase scan step in degrees['']
    #       sweep_end(int):   phase value in degreees to stop the sweep['']
    #
    # Machine setup
    # fill some charge in bunch 'single_bunch_location' (0['2nC'])
    #
    # Example: BBBFE_system_phase_scan('x', 400)
    [root_string, _1, pv_names] = mbf_system_config
    detector = pv_names["tails"]["Detector"]
    adc = pv_names["tails"]["adc"]
    frontend = pv_names["frontend"]["base"]
    fe_system_phase = pv_names["frontend"]["system_phase"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]
    mbf_pv = pv_names["hardware_names"][mbf_ax]
    if mbf_ax.lower() == "x" or mbf_ax.lower() == "y":
        fe_phase_pv = f"{pv_names['frontend']['base']}{fe_system_phase[mbf_ax]}"
    else:
        fe_phase_pv = f"{frontend}{fe_system_phase['sI']}"
        fe_phase_pvQ = f"{frontend}{fe_system_phase['sQ']}"

    # for archival investigations this allows filtering by machine state['']
    # but for capture this is not needed so it set to empty['']
    filter_conditions = []
    # getting general environment data['']
    data = machine_environment
    # Add the extra data to the data structure['']
    data["ax_label"] = mbf_ax
    data["base_name"] = f"system_phase_scan_{mbf_ax}_axis"
    data["orig_gain"] = get_variable(f"{mbf_pv}{sequencer1['gaindb']}")
    data["original_setting"] = get_variable(fe_phase_pv)
    if mbf_ax.lower() == "s":
        data["original_settingQ"] = get_variable(fe_phase_pvQ)
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end
    data["sweep_speed"] = sweep_speed

    # set up the sweep
    data["phase"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["phase"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"] - data["sweep_step"],
        )
    )
    # prealloacation
    data["side1"] = []
    data["main"] = []
    data["side2"] = []
    data["adc_phase"] = []
    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")

    original_detector_setup = BBBFE_detector_setup(mbf_ax, single_bunch_location)
    # moving to starting point in scan
    for pp in range(data["original_setting"], sweep_start, -sweep_step):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if mbf_ax.lower() == "s":
        # I and Q must be in quadrature
        for pp in range(data["original_settingQ"], sweep_start, -sweep_step) + 90:
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    # measurement
    for x in range(1, len(data["phase"])):
        set_variable(fe_phase_pv, data["phase"][x])
        if mbf_ax.lower() == "s":
            set_variable(fe_phase_pvQ, data["phase"][x] + 90)

        time.sleep(sweep_speed)
        data["side1"][x] = max(get_variable(f"{mbf_pv}{detector['det1']['power']}"))
        data["main"][x] = max(get_variable(f"{mbf_pv}{detector['det2']['power']}"))
        data["side2"][x] = max(get_variable(f"{mbf_pv}{detector['det3']['power']}"))
        if mbf_ax.lower() == "s":
            data["adc_phase"][x] = max(get_variable(f"{mbf_pv}{adc['phase']['mean']}"))
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv[1:-2]}{adc['min']}"))
            data["adc_meanQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['mean']}"))
            data["adc_maxQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['max']}"))
            data["adc_minQ"][x] = max(get_variable(f"{mbf_pv[1:-3]}Q{adc['min']}"))
        else:
            data["adc_mean"][x] = max(get_variable(f"{mbf_pv}{adc['mean']}"))
            data["adc_max"][x] = max(get_variable(f"{mbf_pv}{adc['max']}"))
            data["adc_min"][x] = max(get_variable(f"{mbf_pv}{adc['min']}"))

    # move back to the original setting
    for pp in range(data["sweep_start"], data["original_setting"], data["sweep_step"]):
        set_variable(fe_phase_pv, pp)
        time.sleep(5)

    if mbf_ax.lower() == "s":
        # move back to the original setting
        for pp in range(
            data["sweep_start"] + 90, data["original_settingQ"], data["sweep_step"]
        ):
            set_variable(fe_phase_pvQ, pp)
            time.sleep(5)

    if auto_setup == "yes":
        setup_operational_mode(mbf_ax, "TuneOnly")
        set_variable(f"{mbf_pv}{sequencer1['gaindb']}", data["orig_gain"])

    BBBFE_detector_restore(mbf_ax, original_detector_setup)
    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## Plotting data
    if plotting == "yes":
        mbf_frontend_system_phase_scan_archival_retrieval(
            mbf_ax, [data["time"], data["time"]], filter_conditions
        )


def BBBFE_system_phase_scan_plotting(data):
    temp = re.findall("[]*_([xys])_axis$", data["base_name"])
    mbf_ax = temp[0]
    graph_name = data["base_name"].replace("_", " ")
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )

    if mbf_ax == "s":
        instructions = (
            "Q should be placed at ADC amplitude minimum (i.e. the zero crossing)."
        )
    else:
        instructions = "The excited bunch signal should be as high as possible "
        "while maximising the signal differences."

    fig.supplt.title(
        [
            "BBBFE ",
            graph_name,
            " axis on ",
            data["time"].strftime("%a %d %b %Y, %I:%M%p"),
        ]
    )
    fig.subplt.title(instructions, "FontAngle", "italic", "FontSize", 10)
    plt.xlabel("phase (degrees)")

    plt.semilogy(data["phase"], data["main"], "DisplayName", "Excited bunch")
    plt.semilogy(data["phase"], data["side1"], "DisplayName", "Preceeding bunch")
    plt.semilogy(data["phase"], data["side2"], "DisplayName", "Following bunch")
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("Signal")

    plt.semilogy(
        data["phase"],
        data["main"] - data["side1"],
        "DisplayName",
        "Excited bunch - Preceeding bunch",
    )
    plt.semilogy(
        data["phase"],
        data["main"] - data["side2"],
        "DisplayName",
        "Excited bunch - Following bunch",
    )
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("Signal differences")

    plt.semilogy(data["phase"], data["adc_min"], "DisplayName", "Min")
    plt.semilogy(data["phase"], data["adc_max"], "DisplayName", "Max")
    plt.semilogy(data["phase"], data["adc_mean"], "DisplayName", "Mean")
    add_original_values(mbf_ax, data)
    plt.legend("Location", "Best")
    plt.ylabel("ADC Amplitude")

    if mbf_ax.lower() == "s":
        plt.semilogy(data["phase"], data["adc_phase"], "DisplayName", "ADC phase")
        add_original_values(mbf_ax, data)
        plt.legend("Location", "Best")
        plt.ylabel("ADC phase")


def DORIS_phase_scan_plotting(data):
    # plotting
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )

    plt.semilogy(data["phase"], data["main_x"], "DisplayName", "Excited bunch")
    plt.semilogy(data["phase"], data["side1_x"], "DisplayName", "Preceeding bunch")
    plt.semilogy(data["phase"], data["side2_x"], "DisplayName", "Following bunch")
    extents_y = []  # get(gca, 'YLim') #FIXME
    if "original_setting" in data:
        plt.plot(
            [data["original_setting"], data["original_setting"]],
            extents_y,
            "r:",
            "DisplayName",
            "Original setting",
            "LineWidth",
            2,
        )

    plt.legend("Location", "Best")
    plt.xlabel("phase (degrees)")
    plt.ylabel("Signal")
    fig.plt.title(
        f"DORIS target phase sweep on {data['time'].strftime('%a %d %b %Y, %I:%M%p')}"
    )


def DORIS_target_phase_scan(
    single_bunch_location,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    sweep_start=-180,
    sweep_step=5,
    sweep_end=180,
):
    # Scans the phase of the DORIS unit upstream of the MBF frontend and
    # records the strength of the tune signal.
    # Restores the original value after the scan.
    #
    # Args:
    #      single_bunch_location (int): the location of the single bunch.
    #
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state. Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved. Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       sweep_start(int): phase value in degrees to start the sweep.
    #       sweep_step(int):  phase scan step in degrees.
    #       sweep_end(int):   phase value in degreees to stop the sweep.
    #
    # Machine setup: (manual for the time being.)
    # fill some charge in bunch 1 (0.2nC)
    #
    # Example: DORIS_target_phase_scan(400)
    [root_string, _1, pv_names] = mbf_system_config
    detector = pv_names["tails"]["Detector"]
    doris_pv = pv_names["doris"]["phase"]
    mbf_pv_x = pv_names["hardware_names"]["x"]
    mbf_pv_y = pv_names["hardware_names"]["y"]
    mbf_pv_s = pv_names["hardware_names"]["s"]
    sequencer1 = pv_names["tails"]["Sequencer"]["seq1"]

    # getting general environment data['']
    data = machine_environment
    # Add the extra data to the data structure['']
    data["base_name"] = "doris_phase_scan"
    data["original_setting"] = get_variable(doris_pv)
    data["orig_gain_x"] = get_variable(f"{mbf_pv_x}{sequencer1['gaindb']}")
    data["orig_gain_y"] = get_variable(f"{mbf_pv_y}{sequencer1['gaindb']}")
    data["orig_gain_s"] = get_variable(f"{mbf_pv_s}{sequencer1['gaindb']}")
    data["single_bunch_location"] = single_bunch_location
    data["auto_setup"] = auto_setup
    data["plotting"] = plotting
    data["additional_save_location"] = additional_save_location
    data["sweep_start"] = sweep_start
    data["sweep_step"] = sweep_step
    data["sweep_end"] = sweep_end

    # set up the sweep
    data["phase"] = range(data["sweep_start"], data["sweep_end"], data["sweep_step"])
    data["phase"].extend(
        range(
            data["sweep_end"] - data["sweep_step"],
            data["sweep_start"],
            -data["sweep_step"],
        )
    )
    # prealloacation
    data["side1_x"] = []
    data["main_x"] = []
    data["side2_x"] = []
    data["side1_y"] = []
    data["main_y"] = []
    data["side2_y"] = []
    if auto_setup == "yes":
        setup_operational_mode("x", "TuneOnly")
        setup_operational_mode("y", "TuneOnly")
        setup_operational_mode("s", "TuneOnly")

    detector_setup_x = BBBFE_detector_setup("x", single_bunch_location)
    detector_setup_y = BBBFE_detector_setup("y", single_bunch_location)
    detector_setup_s = BBBFE_detector_setup("s", single_bunch_location)
    # moving to starting point in scan
    set_variable(doris_pv, -180)
    for dbf in range(1, len(data["phase"])):
        set_variable(doris_pv, data["phase"][dbf])
        time.sleep(2)
        data["side1_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det1']['power']}")
        )
        data["main_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det2']['power']}")
        )
        data["side2_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_x']}{detector['det3']['power']}")
        )
        data["side1_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det1']['power']}")
        )
        data["main_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det2']['power']}")
        )
        data["side2_x"][dbf] = max(
            get_variable(f"{data['mbf_pv_y']}{detector['det3']['power']}")
        )
        print(".")

    # move back to the original setting
    set_variable(doris_pv, data["original_setting"])
    if auto_setup == "yes":
        setup_operational_mode("x", "TuneOnly")
        set_variable(f"{mbf_pv_x}{sequencer1['gaindb']}", data["orig_gain_x"])
        setup_operational_mode("y", "TuneOnly")
        set_variable(f"{mbf_pv_y}{sequencer1['gaindb']}", data["orig_gain_y"])
        setup_operational_mode("s", "TuneOnly")
        set_variable(f"{mbf_pv_s}{sequencer1['gaindb']}", data["orig_gain_s"])

    BBBFE_detector_restore("x", detector_setup_x)
    BBBFE_detector_restore("y", detector_setup_y)
    BBBFE_detector_restore("s", detector_setup_s)
    ## saving the data to a file
    save_to_archive(root_string, data)
    if additional_save_location:
        scipy.savemat(additional_save_location, data)

    ## plotting
    if plotting == "yes":
        DORIS_phase_scan_plotting(data)

    return data


def mbf_frontend_clock_phase_scan_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets. Then plots the results.
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed.
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    # Returns:
    #         leading (numeric matrix):
    #         excited (numeric matrix):
    #         following (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_growdamp_archival_analysis(
    #                                                     data_requested, 'average')
    times = []
    leading = np.array(ndmin=2)
    excited = np.array(ndmin=2)
    following = np.array(ndmin=2)
    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        leading[:, nd] = data_requested[nd]["side1"][:, 1]
        excited[:, nd] = data_requested[nd]["main"][:, 1]
        following[:, nd] = data_requested[nd]["side2"][:, 1]
        param = []
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        leading, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(leading, param, parameter_step)
        )
        excited, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(excited, param, parameter_step)
        )
        [following, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                following, param, parameter_step
            )
        )
    elif analysis_type == "average":
        print(
            "Archive:Frontend:ClockPhase:setting "
            "Ignoring the last two parameters as 'average' is set"
        )
        leading = np.mean(leading, 1, "omitnan")
        excited = np.mean(excited, 1, "omitnan")
        following = np.mean(following, 1, "omitnan")


def mbf_frontend_clock_phase_scan_archival_plotting(
    requested_data, leading, excited, following, times, experimental_setup
):
    # Plots the data processed by mbf_growdamp_archival_analysis.
    # Args:
    #      leading (numeric matrix):
    #      excited (numeric matrix):
    #      following (numeric matrix):
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results
    #                                    of the fit errors.
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude,
    #                                data_phase, times, setup, selections, extents)

    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend clock phase scan"
    mbf_archival_plotting_setup(requested_data, times, experimental_setup)
    x_plt_axis = requested_data[1]["phase"]
    this_year = datetime.datetime.now().year
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Frontend clock phase as a def of {experimental_setup['sweep_parameter']}"
        )
        f"Using a step size of {experimental_setup['parameter_step_size']} in the"
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, leading)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(leading, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("leading bunch")
    plt.xlabel("Phase")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, excited)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(excited, years_input, years_colours, times, x_plt_axis)
        plt.legend("off")

    plt.title({graph_title, "excited bunch"})
    plt.xlabel("Phase")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, following)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(following, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("following bunch")
    plt.xlabel("Phase")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])
    diff1 = excited - leading
    diff2 = excited - following

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, diff1)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(diff1, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("excited - leading")
    plt.xlabel("Phase")
    plt.ylabel("Signal differences")
    ymin = min([min(min(diff1, [], 2)), min(min(diff2, [], 2))])
    ymax = max([max(max(diff1, [], 2)), max(max(diff1, [], 2))])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, diff2)
        plt.legend(graph_labels, "Location", "eastoutside")
    else:
        populate_archive_graph(diff2, years_input, times, x_plt_axis)
        plt.legend("Location", "eastoutside")

    plt.title("excited - following")
    plt.xlabel("Phase")
    plt.ylabel("Signal differences")
    ymin = min([min(min(diff1, [], 2)), min(min(diff2, [], 2))])
    ymax = max([max(max(diff1, [], 2)), max(max(diff1, [], 2))])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    return leading, excited, following, times, experimental_setup


def mbf_frontend_clock_phase_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
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
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                              structures.
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #                  [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"clock_phase_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_clock_phase_scan_plotting(requested_data[1])
    else:
        conditioned_data = mbf_archival_conditional_filtering(requested_data)
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_clock_phase_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_clock_phase_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )

            setup["axis"] = ax
            mbf_frontend_clock_phase_scan_archival_plotting(
                conditioned_data, leading, excited, following, times, setup
            )

    return conditioned_data


def mbf_frontend_gain_scan_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets. Then plots the results.
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed.
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    # Returns:
    #         adc_mean (numeric matrix):
    #         adc_max (numeric matrix):
    #         adc_min (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_growdamp_archival_analysis(
    #                                                     data_requested, 'average')
    times = []
    param = []
    adc_mean = np.array(ndmin=2)
    adc_max = np.array(ndmin=2)
    adc_min = np.array(ndmin=2)

    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        adc_mean[:, nd] = data_requested[nd]["adc_mean"][:, 1]
        adc_max[:, nd] = data_requested[nd]["adc_max"][:, 1]
        adc_min[:, nd] = data_requested[nd]["adc_min"][:, 1]
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print("[]")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        [adc_mean, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(adc_mean, param, parameter_step)
        )
        [adc_max, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(adc_max, param, parameter_step)
        )
        [adc_min, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(adc_min, param, parameter_step)
        )
    elif analysis_type == "average":
        print(
            "Archive:Frontend:Gain:setting "
            "Ignoring the last two parameters as 'average' is set"
        )
        adc_mean = np.mean(adc_mean, 0)
        adc_max = np.mean(adc_max, 0)
        adc_min = np.mean(adc_min, 0)


def mbf_frontend_gain_scan_archival_plotting(
    requested_data, adc_mean, adc_max, adc_min, times, experimental_setup
):
    # Plots the data processed by mbf_growdamp_archival_analysis.
    # Args:
    #      adc_mean (numeric matrix):
    #      adc_max (numeric matrix):
    #      adc_min (numeric matrix):
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    # Example: mbf_frontend_gain_scan_archival_plotting(requested_data, data_magnitude,
    #                            data_phase, times, setup, selections, extents)

    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend gain scan"
    mbf_archival_plotting_setup(requested_data, times, experimental_setup)
    x_plt_axis = requested_data[1]["gain"]
    this_year = datetime.datetime.now().year
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Frontend clock phase as a def of {experimental_setup['sweep_parameter']}"
        )
        f"Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, adc_mean)
    else:
        populate_archive_graph(adc_mean, years_input, years_colours, times, x_plt_axis)
        plt.legend("off")

    plt.title("ADC min")
    plt.xlabel("Gain")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(adc_mean, [], 2)), min(min(adc_max, [], 2)), min(min(adc_min, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(adc_mean, [], 2)), max(max(adc_max, [], 2)), max(max(adc_min, [], 2))]
    )
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, adc_max)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(adc_max, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title({graph_title, "excited bunch"})
    plt.xlabel("Gain")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(adc_mean, [], 2)), min(min(adc_max, [], 2)), min(min(adc_min, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(adc_mean, [], 2)), max(max(adc_max, [], 2)), max(max(adc_min, [], 2))]
    )
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, adc_min)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(adc_min, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("ADC max")
    plt.xlabel("Gain")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(adc_mean, [], 2)), min(min(adc_max, [], 2)), min(min(adc_min, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(adc_mean, [], 2)), max(max(adc_max, [], 2)), max(max(adc_min, [], 2))]
    )
    plt.ylim([ymin, ymax])
    return adc_mean, adc_max, adc_min, times, experimental_setup


def mbf_frontend_gain_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
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
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep.
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged. (only needed if
    #                                    anal_type set to 'parameter sweep')
    #
    #
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures.
    #
    # Example: mbf_frontend_gain_scan_archival_retrieval('x',
    #                          [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"frontend_gain_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_gain_scan_plotting(requested_data[1])
    else:
        conditioned_data = mbf_archival_conditional_filtering(requested_data)
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [adc_mean, adc_max, adc_min, times, setup] = (
                    mbf_frontend_gain_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [adc_mean, adc_max, adc_min, times, setup] = (
                    mbf_frontend_gain_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )

            setup["axis"] = ax
            mbf_frontend_gain_scan_archival_plotting(
                conditioned_data, adc_mean, adc_max, adc_min, times, setup
            )

    return conditioned_data


def mbf_frontend_system_phase_scan_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets. Then plots the results.
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed.
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
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
    # Returns:
    #         leading (numeric matrix):
    #         excited (numeric matrix):
    #         following (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_growdamp_archival_analysis(
    #                                                   data_requested, 'average')
    times = []
    leading = np.array(ndmin=2)
    excited = np.array(ndmin=2)
    following = np.array(ndmin=2)
    param = []
    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        leading[:, nd] = data_requested[nd]["side1"][:, 1]
        excited[:, nd] = data_requested[nd]["main"][:, 1]
        following[:, nd] = data_requested[nd]["side2"][:, 1]
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        leading, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(leading, param, parameter_step)
        )
        excited, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(excited, param, parameter_step)
        )
        following, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                following, param, parameter_step
            )
        )
    elif analysis_type == "average":
        print(
            "Archive:Frontend:SystemPhase:setting "
            "Ignoring the last two parameters as 'average' is set"
        )
        leading = np.mean(leading, 0)
        excited = np.mean(excited, 0)
        following = np.mean(following, 0)
    return leading, excited, following, times, experimental_setup


def mbf_frontend_system_phase_scan_archival_plotting(
    requested_data, leading, excited, following, times, experimental_setup
):
    # Plots the data processed by mbf_growdamp_archival_analysis.
    # Args:
    #      leading (numeric matrix):
    #      excited (numeric matrix):
    #      following (numeric matrix):
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results of
    #                                    the fit errors.
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude,
    #                                data_phase, times, setup, selections, extents)

    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend system phase scan"
    fig = mbf_archival_plotting_setup(requested_data, times, experimental_setup)
    x_plt_axis = requested_data[1]["phase"]
    this_year = datetime.datetime.now().year
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Frontend system phase as a def of {experimental_setup['sweep_parameter']}"
        )
        f"Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    fig.supplt.title(graph_title)
    plt.xlabel("Phase (degrees)")

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, leading)
    else:
        populate_archive_graph(leading, years_input, years_colours, times, x_plt_axis)
        plt.legend("off")

    plt.title("leading bunch")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, excited)
    else:
        populate_archive_graph(excited, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("excited bunch")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, following)
    else:
        populate_archive_graph(following, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("following bunch")
    plt.ylabel("Magnitude")
    ymin = min(
        [min(min(leading, [], 2)), min(min(excited, [], 2)), min(min(following, [], 2))]
    )
    ymin = min(ymin, 0)

    ymax = max(
        [max(max(leading, [], 2)), max(max(excited, [], 2)), max(max(following, [], 2))]
    )
    plt.ylim([ymin, ymax])
    diff1 = excited - leading
    diff2 = excited - following

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, diff1)
        #     plt.legend(graph_labels)
    else:
        populate_archive_graph(diff1, years_input, times, x_plt_axis)
        plt.legend("off")

    plt.title("difference between excited and leading bunches")
    plt.ylabel("Signal differences")
    ymin = min([min(min(diff1, [], 2)), min(min(diff2, [], 2))])
    ymax = max([max(max(diff1, [], 2)), max(max(diff1, [], 2))])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, diff2)
        leg = plt.legend(graph_labels, "Location", "eastoutside")
    else:
        populate_archive_graph(diff2, years_input, times, x_plt_axis)
        leg = plt.legend("Location", "eastoutside")

    leg["Layout"]["Tile"] = "east"
    plt.title("difference between excited and following bunches")
    plt.ylabel("Signal differences")
    ymin = min([min(min(diff1, [], 2)), min(min(diff2, [], 2))])
    ymax = max([max(max(diff1, [], 2)), max(max(diff1, [], 2))])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])

    plt.title("ADC amplitude")
    plt.ylabel("Signal differences")

    plt.title("ADC phase")
    plt.ylabel("Signal differences")


def mbf_frontend_system_phase_scan_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
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
    #       sweep_parameter (str): Parameter to be used. This name must exist
    #                              in the data structure. (only needed if
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
    # Returns:
    #       conditioned_data (cell of structures): The group of requested data
    #                                            structures.
    #
    # Example: mbf_modescan_archival_retrieval('x',
    #            [datetime(2023, 1, 1), datetime("now")])
    selection_name = f"system_phase_scan_{ax}_axis"
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        BBBFE_system_phase_scan_plotting(requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions.
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_system_phase_scan_archival_analysis(
                        conditioned_data, analysis_type="collate"
                    )
                )
            elif analysis_type == "sweep":
                [leading, excited, following, times, setup] = (
                    mbf_frontend_system_phase_scan_archival_analysis(
                        conditioned_data,
                        analysis_type="parameter_sweep",
                        sweep_parameter=sweep_parameter,
                        parameter_step=parameter_step,
                    )
                )
            else:
                raise ValueError(
                    "archivalDatasetRetrieval:InputError "
                    "Please select collate or sweep as the analysis type"
                )

            setup["axis"] = ax
            mbf_frontend_system_phase_scan_archival_plotting(
                conditioned_data, leading, excited, following, times, setup
            )
