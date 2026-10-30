import datetime
import time

import matplotlib.pyplot as plt
import numpy as np
import scipy

from Common import (
    fll_phase_scan_plotting,
    get_variable,
    machine_environment,
    mbf_system_config,
    save_to_archive,
    set_variable,
)


def mbf_pll_bank_setup(mbf_axis, pllbunches=400, guardbunches=2):
    # Sets up the banks for FLL operation['']
    #
    #   mbf_axis(str): x, y, or s
    #   pllbunches (float or list of floats): bunches numbers to use for PLL (0-935)
    #                                         (defaults to 400)
    #   guardbunches (int): number of bunches around PLL to also take out
    #                       of sweeper (defaults to 2)
    #
    # example: mbf_fll_bank_setup(name,pllbunches,guardbunches)

    [_1, harmonic_number, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    pllbunches = np.mod(pllbunches, harmonic_number - 1)
    # initialise pll pattern
    pllpattern = False(range(harmonic_number))
    pllpattern[pllbunches] = True
    # now we want to create a pattern with a little more room around the
    # pll bunches[''] It's a little tricky with a general pattern, and the cirular
    # nature the pattern, so I use circshift in a loop
    guardpattern = True(range(harmonic_number))
    for n in range(-guardbunches, guardbunches):
        guardpattern[np.fft.circshift(pllpattern, n)] = False

    # Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps),
    # and in PLL detector.
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank0']['PLL']['enablewf']}",
        pllpattern,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['PLL']['enablewf']}",
        pllpattern,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['target_bunches']}",
        pllpattern,
    )
    # Set sweep (SEQ) and its detector (#1) to NOT operate on these and
    # guard bunches around, ie only on guardpattern.
    # check or add to any previous config and uses logical AND to insert the
    # guardpattern into the existing setup.
    sequencer = get_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['SEQ']['enablewf']}"
    )
    detector = get_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Detector']['det0']['bunch_selection']}"
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Bunch_bank']['bank1']['SEQ']['enablewf']}",
        guardpattern and sequencer,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['Detector']['det0']['bunch_selection']}",
        guardpattern and detector,
    )


def mbf_pll_detector_setup(
    mbf_axis,
    pll_detector_select="ADC no fill",
    adc_reject_count="128 turns",
    pll_detector_scaling="48dB",
    pll_detector_blanking="Blanking",
    pll_detector_dwell=128,
):
    # Sets up the detector for FLL operation['']
    #
    #   mbf_axis (str): x, y, or s. Selects which MBF system to operate on.
    #
    # example: mbf_pll_detector_setup(mbf_axis, varargin)

    [_2, _1, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    # Set up the PLL detector
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['mode']}",
        pll_detector_select,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['adc']['reject_count']}", adc_reject_count
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['scaling']}",
        pll_detector_scaling,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['blanking']}",
        pll_detector_blanking,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}",
        pll_detector_dwell,
    )


def mbf_pll_phase_scan(mbf_axis, scan_range=270, step=1):
    #
    #       Args:
    #           mbf_axis(str): 'x' or 'y'
    #           scan_range(int): phase range in degree to search around the
    #                       current target phase default is 80 degrees
    #           step(int): step in degree, default is 5 degrees
    #       Returns:
    #          fll_phase_scan(struct): structure containing captured data from
    #                                  the MBF plus general operating
    #                                  conditions of the machine
    #
    # Example: fll_phase_scan = mbf_pll_peakfind('x')

    [root_path, _1, pv_names] = mbf_system_config()
    pll_phase_scan = machine_environment()
    pll_phase_scan["ax_label"] = mbf_axis
    pll_phase_scan["base_name"] = f"pll_phase_scan_{pll_phase_scan['ax_label']}_axis"
    name = pv_names["hardware_names"][mbf_axis]
    pll_tails = pv_names["tails"]["pll"]
    pll_phase_scan["scan_step"] = step
    pll_phase_scan["scan_range"] = scan_range
    pll_phase_scan["mbf_fll"]["target_bunches"] = get_variable(
        f"{name}{pll_tails['detector']['target_bunches']}"
    )
    pll_phase_scan["mbf_fll"]["gain"] = get_variable(
        f"{name}{pll_tails['nco']['gain']}"
    )
    pll_phase_scan["mbf_fll"]["target_phase"] = get_variable(
        f"{name}{pll_tails['target_phase']}"
    )
    pll_phase_scan["mbf_fll"]["KI"] = get_variable(f"{name}{pll_tails['i']}")
    pll_phase_scan["mbf_fll"]["KP"] = get_variable(f"{name}{pll_tails['p']}")
    start = get_variable(f"{name}{pll_tails['target_phase']}")
    pll_phase_scan["phase"] = range(start, start + scan_range, step)
    pll_phase_scan["phase"].extend(range(start + scan_range, start - scan_range, -step))
    pll_phase_scan["phase"].extend(range(start - scan_range, start + scan_range, step))
    pll_phase_scan["phase"].extend(range(start + scan_range, start, -step))
    pll_phase_scan["mag"] = []
    pll_phase_scan["iq"] = []
    pll_phase_scan["f"] = []
    for n in range(len(pll_phase_scan["phase"])):
        status = get_variable(f"{name}{pll_tails['status']}")
        if status == "Running":
            # the funny mod is required to get into the right range of -180 to +179
            set_variable(
                f"{name}{pll_tails['target_phase']}",
                np.mod(pll_phase_scan["phase"][n] + 180, 360) - 180,
            )
            # This will depend on the dwell time and PLL config,
            # but works with the default
            time.sleep(2)
            # get magnitude
            pll_phase_scan["mag"][n] = get_variable(
                f"{name}{pll_tails['readback']['magnitude']}"
            )
            # get phase readback
            pll_phase_scan["phase"][n] = get_variable(
                f"{name}{pll_tails['readback']['phase']}"
            )
            pll_phase_scan["iq"][n] = [1, np.i] * get_variable(
                f"{name}{pll_tails['readback']['i']}{name}{pll_tails['readback']['q']}"
            )
            pll_phase_scan["f"][n] = get_variable(
                f"{name}{pll_tails['nco']['frequency']}"
            )
        else:
            set_variable(f"{name}{pll_tails['target_phase']}", start)
            break

    save_to_archive(root_path[1], pll_phase_scan)
    print(f"Data saved to {root_path[1]}{pll_phase_scan['base_name']}")
    fll_phase_scan_plotting(pll_phase_scan)
    if not status == "Running":
        raise ValueError(
            "PLL:stoppedUnexpectedly"
            "PLL stopped during phase sweep, please restart using fll_start"
        )
    return pll_phase_scan


def mbf_pll_start(
    mbf_axis, pllbunches=400, guardbunches=2, pll_nco_gain=-30, target_phase=180
):
    # sets up the frequency locked loop of the MBF system['']
    # and starts['']
    #
    #       mbf_axis (str): x, y, or s[''] Selects which MBF system to operate on['']
    #       pllbunches (float or list of floats): Selects which bunches to have the
    #                                             FLL operational on['']
    #       guardbunches (int): number of bunches around the FLL bunches which have
    #                           feddback and capture disabled['']
    #
    # example: mbf_fll_setup(mbf_axis, pllbunches, guardbunches)

    mbf_pll_bank_setup(mbf_axis, pllbunches=pllbunches, guardbunches=guardbunches)
    mbf_pll_detector_setup(mbf_axis)
    pll_initialisation(
        mbf_axis, pll_target_phase=target_phase, pll_nco_gain=pll_nco_gain
    )


def pll_PI_scan(
    mbf_axis,
    p_vals,
    i_vals,
    save_to_archive="yes",
    additional_save_location=None,
    guardbunches=10,
    pll_monitor_bunches=400,
):
    # This sets up the PLL loop for different P and I settings, then records various
    # statistics in order to assess which setting are most suitable['']

    [root_string, _1, pv_names] = mbf_system_config
    root_string = root_string[1]
    pv_head = pv_names["hardware_names"][mbf_axis]
    pll_tails = pv_names["tails"]["pll"]
    # getting general environment data['']
    pll_data = machine_environment("tunes")
    # Add the axis label to the data structure['']
    pll_data["ax_label"] = mbf_axis
    pll_data["base_name"] = ["PLL_", pll_data["ax_label"], "_PI_scan"]
    n_p = len(p_vals)
    n_i = len(i_vals)
    n_repeats = 20
    pll_data["minwf"] = np.array(ndmin=3)
    pll_data["maxwf"] = np.array(ndmin=3)
    pll_data["meanwf"] = np.array(ndmin=3)
    pll_data["stdwf"] = np.array(ndmin=3)
    pll_data["tunewf"] = np.array(ndmin=3)
    pll_data["offsetwf"] = np.array(ndmin=3)
    pll_data["i_values"] = np.array(ndmin=3)
    pll_data["p_values"] = np.array(ndmin=3)
    pll_data["dwell"] = get_variable(f"{pv_head}{pll_tails['detector']['dwell']}")
    for ser in range(n_p):
        for jfe in range(n_i):
            # initialise loop
            set_variable(f"{pv_head}{pll_tails['i']}", i_vals(jfe))
            set_variable(f"{pv_head}{pll_tails['p']}", p_vals(ser))
            mbf_pll_start(
                mbf_axis, pllbunches=pll_monitor_bunches, guardbunches=guardbunches
            )
            for ewn in range(n_repeats):
                time.sleep(1)
                data = get_variable(
                    f"{pv_head}{pll_tails['nco']['offset_waveform']}"
                    f"P{pv_head}{pll_tails['nco']['mean_offset']}"
                    f"{pv_head}{pll_tails['nco']['std_offset']}"
                    f"{pv_head}{pll_tails['nco']['tune']}"
                    f"{pv_head}{pll_tails['nco']['offset']}"
                )
                wf = data[1, :]
                pll_data["minwf"][ser, jfe, ewn] = min(wf)
                pll_data["maxwf"][ser, jfe, ewn] = max(wf)
                pll_data["meanwf"][ser, jfe, ewn] = data[1, 0]
                pll_data["stdwf"][ser, jfe, ewn] = data[2, 0]
                pll_data["tunewf"][ser, jfe, ewn] = data[3, 0]
                pll_data["offsetwf"][ser, jfe, ewn] = data[4, 0]
                pll_data["i_values"][ser, jfe, ewn] = i_vals[jfe]
                pll_data["p_values"][ser, jfe, ewn] = p_vals[ser]

    ## saving the data to a file
    if mbf_axis == "x" or mbf_axis == "y" or mbf_axis == "s":
        #     only save if not on test system
        if save_to_archive == "yes":
            save_to_archive(root_string, pll_data)

        if additional_save_location:
            scipy.savemat(additional_save_location, "pll_data")

    return pll_data


def pll_initial_setup_values(mbf_axis):
    # Some setup with 'working values'[''] These ought to be read from a
    # config file or be additional arguments in the future['']
    # mbf_axis(str): xys
    [_2, _1, pv_names] = mbf_system_config()
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['mode']}", "ADC no fill"
    )
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['adc']['reject_count']}", "128 turns")
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['scaling']}", "48dB"
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['blanking']}", "Blanking"
    )
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['minumum_magnitude']}", 0)
    if "TMBF" in mbf_names[mbf_axis]:
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", 1000
        )  # safe also for for low charge, sharp resonance
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", 0)
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}", 128
        )
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}", 0.02)
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", -180)
    elif "LMBF" in mbf_names[mbf_axis]:
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", 100
        )  # safe also for for low charge, sharp resonance
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", 0)
        set_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['pll']['detector']['dwell']}", 128
        )
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}", 0.001)
        set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", -5)


def pll_initialisation(
    mbf_axis,
    pll_ki=1000,
    pll_kp=0,
    pll_min_magnitude=0,
    pll_locking_max_offset=0.003,
    pll_tracking_max_offset=0.02,
    pll_nco_gain=-30,
    pll_target_phase=160,
    tune_override=None,
):
    # This is to start the phase locked loop (pll) [also called pll] from
    # scratch. Once the initial lock is found then the settings are changed to
    # improve tracking. if signal is lost this process can be run again.
    # mbf_axis(str): x, y, or s
    [_2, _1, pv_names] = mbf_system_config
    mbf_names = pv_names["hardware_names"]
    mbf_vars = pv_names["tails"]
    ## Checking tune
    # starting frequency is taken from swept tune measurement. Can also
    # be overridden from command line input (but then it will only work if tune
    # feedback has brought the tune to the desired value.)
    if not tune_override:
        # Perform a TUNE sweep, record phase at tune peak and the tune value
        tune_frequency_from_sweep = get_variable(
            f"{mbf_names[mbf_axis]}{mbf_vars['tune']['centre']}"
        )
        if not tune_frequency_from_sweep:
            raise ValueError(
                "pllInitialisation:invalidTuneFitTune fit invalid, cannot start PLL."
            )

    else:
        tune_frequency_from_sweep = tune_override
        print(f"Using tune override of {tune_override}")

    # Disable PLL and turn off the NCO
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['stop']}", 1)
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['enable']}", "Off")
    # Set up the FLL feedback loop
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['i']}", pll_ki)
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['p']}", pll_kp)
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['minumum_magnitude']}",
        pll_min_magnitude,
    )
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['target_phase']}", pll_target_phase
    )
    # Set up the NCO
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['gain']}", pll_nco_gain)
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['set_frequency']}",
        tune_frequency_from_sweep,
    )
    # Limit tune range of the NCO for initial peak finding['']
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}",
        pll_locking_max_offset,
    )
    # Enable the NCO and PLL
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['nco']['enable']}", "On")
    set_variable(f"{mbf_names[mbf_axis]}{mbf_vars['pll']['start']}", 1)
    # Wait until PLL has locked (set lower bound to phase error?)
    t1 = datetime.datetime.now()
    while (
        abs(
            abs(
                get_variable(
                    f"{mbf_names[mbf_axis]}{mbf_vars['pll']['readback']['phase']}"
                )
            )
            - abs(pll_target_phase)
        )
        > 1
    ):  # within one degree of target['']
        lock_time = datetime.datetime.now()
        if lock_time > t1 + 10:  # FIXME
            print("Unable to lock within 10 seconds")
            return

    # Once locked widen the NCO limits to max required for tracking
    set_variable(
        f"{mbf_names[mbf_axis]}{mbf_vars['pll']['maximum_offset']}",
        pll_tracking_max_offset,
    )


def pll_phase_scan_plotting(fll_phase_scan):
    # Plots the results of a FLL phase scan on the
    # multi binch feedback system
    #
    #   Args:
    #       fll_phase_scan(struct): data captured during the phase scan['']
    #
    #   Returns:
    #       f1(plt.figure handle):
    #
    # Example: f1 = fll_phase_scan_plotting(fll_phase_scan)
    [_1, mi] = max(abs(fll_phase_scan["mag"]))
    peak = fll_phase_scan["phase"][mi]
    f1 = plt.figure("Position", [50, 100, 1024, 768])
    plt.subplt.plot(1, 3, 1)
    plt.plot(fll_phase_scan["phase"], fll_phase_scan["mag"], "*")
    plt.plot(
        [peak, peak], [min(fll_phase_scan["mag"]), max(fll_phase_scan["mag"])], ":r"
    )
    plt.xlabel("target phase")
    plt.ylabel("PLL detected magnitude")
    plt.subplt.plot(1, 3, 2)
    plt.plot(fll_phase_scan["phase"], fll_phase_scan["f"], "*")
    plt.xlabel("target phase")
    plt.ylabel("PLL detected frequency")
    f1.title(
        "Phase scan of frequency locked loop"
        f"RF frequency = {fll_phase_scan['RF']}"
        f"Current = {fll_phase_scan['current']}"
    )
    plt.subplt.plot(1, 3, 3)
    plt.plot(fll_phase_scan["iq"], "*")
    plt.xlabel("i")
    plt.ylabel("q")
    return f1


def pll_phase_scan_plotting_multi(
    selected_axis, requested_data, scan_type="samples", target_bunch_override=None
):
    # Plots the results of a FLL phase scan on the
    # multi bunch feedback system
    #
    #   Args:
    #       fll_phase_scan(struct): data captured during the phase scan['']
    #       scan_type(str): states what the scan variable was
    #                       'samples', 'charge', 'gain', 'rf'
    #       target_bunch_override(int): force the target bunch location to be this
    #                                   value
    #
    # Example: fll_phase_scan_plotting_multi(requested_data, varargin)
    xval = []
    for ehs in range(len(requested_data)):
        if scan_type == "samples":
            xval[ehs] = ehs
        elif scan_type == "charge":
            if not target_bunch_override:
                # IF more than one bunch is selected then
                # only the first one is used here.
                target_bunch = np.find(
                    requested_data[ehs]["mbf"][selected_axis]["fll"]["target_bunches"]
                    > 0,
                    1,
                    "first",
                )
            else:
                target_bunch = target_bunch_override

            xval[ehs] = requested_data[ehs]["fill_pattern"][target_bunch] * 1e3
        elif scan_type == "gain":
            selected_axis = requested_data[ehs]["ax_label"]
            xval[ehs] = requested_data[ehs]["mbf"][selected_axis]["fll"]["nco"]["gain"]
        elif scan_type == "rf":
            xval[ehs] = requested_data[ehs]["RF"]

    [xval, sorting] = np.sort(xval)
    # gains = [-30,-24,-18,-12,-6]
    low_mag_limit = 2e-5
    plt.figure("Position", [50, 100, 1900, 768])
    for ehs in range(len(requested_data)):
        temp_data = requested_data[sorting[ehs]]
        data_length = len(temp_data["phase"])
        plt.subplt.plot(2, 4, 1)
        plt.plot(temp_data["phase"], temp_data["mag"], "*")
        plt.xlabel("target phase")
        plt.ylabel("Loop detected magnitude")
        plt.subplt.plot(2, 4, 2)
        # set the phase values where the magnitude is very low to NaN in order to
        # clean up the graphs
        temp_phase = temp_data["phase"]
        temp_phase[temp_data["mag"] < low_mag_limit] = None
        plt.plot(np.rem(temp_data["f"], 1), temp_phase, "*")
        plt.xlabel("Loop detected fractional tune")
        plt.ylabel("target phase")
        plt.title(
            f"Phase scan of frequency locked loop in {requested_data[0]['ax_label']}"
            f" with {scan_type}"
        )
        plt.xlim([0, 1])
        plt.subplt.plot(2, 4, 3)
        plt.plot(np.rem(temp_data["f"], 1), temp_data["mag"], "*")
        plt.xlabel("Loop detected fractional tune")
        plt.ylabel("Loop detected magnitude")
        plt.xlim([0, 1])
        plt.subplt.plot(2, 4, 4)
        plt.plot(requested_data[ehs]["iq"], "*")
        plt.xlabel("i")
        plt.ylabel("q")
        plot_X = np.ones(data_length, 1) * xval(ehs)
        plot_Y = requested_data[ehs]["phase"]
        mag_Z = requested_data[ehs]["mag"]
        f_Z = requested_data[ehs]["f"]
        # set the phase values where the magnitude is very low to NaN in order to
        # clean up the graphs
        plot_Y[mag_Z < low_mag_limit] = None
        plt.subplt.plot(2, 4, 5)
        plt.plot3(plot_X, plot_Y, mag_Z, "*")
        plt.ylabel("target phase")
        plt.xlabel(scan_type)
        plt.zlabel("Loop detected magnitude")
        plt.subplot[2, 4, 6:7]
        plt.plot3(plot_X, np.rem(f_Z, 1), plot_Y, "*", "DisplayName", (xval(ehs)))
        plt.ylabel("Loop detected fractional tune")
        plt.xlabel(scan_type)
        plt.zlabel("target phase")
        plt.ylim([0, 1])

    filename = "~/Phase scan of frequency locked loop in "
    f"{requested_data[1]['ax_label']}_with_{scan_type}_"
    f"{requested_data[1]['time'].strftime('%a %d %b %Y, %I:%M%p')}"
    filename = filename.replace(" ", "_")
    filename = filename.replace(":", "-")
    plt.savefig(f"{filename}.fig")
    plt.savefig(f"{filename}.png")


def plot_pll_data(pll_data):
    plt.figure(1)
    plt.plot(pll_data["maxwf"][1, 1, :], "r", "DisplayName", "max")
    plt.plot(pll_data["minwf"][1, 1, :], "g", "DisplayName", "min")
    plt.plot(pll_data["meanwf"][1, 1, :], "b", "DisplayName", "mean")
    plt.title(["PLL I value = ", (pll_data["i_values"](1, 1, 1))])
    plt.ylabel("Tune offset from setpoint")
    plt.xlabel(["samples (spacing 4096 * ", (pll_data["dwell"]), ")"])
