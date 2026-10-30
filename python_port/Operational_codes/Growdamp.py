import datetime
import re
import time

import matplotlib.pyplot as plt
import matplotlib.text as mplt
import numpy as np
import scipy

from Common import (
    get_operational_mode,
    get_variable,
    machine_environment,
    mbf_archival_conditional_filtering,
    mbf_archival_dataset_retrieval,
    mbf_archival_plotting_setup,
    mbf_fll_setup,
    mbf_growthrates_analysis,
    mbf_system_config,
    mean_steps_data_in_stucture,
    mode_to_frequency,
    movmean,
    save_to_archive,
    set_variable,
    setup_operational_mode,
    sort_data_in_stucture,
)

# FIXME
# def drive_damp_analysis_longitudinal_expfit(name):
# # Exponential fit def for drive-damp measurements:
#     # Last edit: 28['09']['2023'] (G['Rehm'], A['Matveenko'])
#     n_cycles = 400
#     aa = np.reshape(abs(name['iq']), name['dampcapture'], n_cycles)
#     time = range(name['dampcapture']) * name['dampdwell'] / 1.249e6 # s
#     # fit parameters are amplitude - p(1), damping - p(2), and "zero"-point offset - p(3)
#     f = @(p, time) (p(1) ['']* exp(-p(2) ['']* time) + p(3))
#     # further "optimisation" of opts can make the fit faster
#     opts = optimset('MaxFunEvals', 50000, 'MaxIter', 10000)
#     for m  in range( 1, n_cycles):
#         OLS = @(p) np.sum((f(p, time) - aa(:,m))^2) # sum of squares of model-measurement
#         res0 = [aa(1,m); 150; aa(300,m)] # guess-values
#         p[m,1:3] = fminsearch(OLS, res0, opts)
#         #[p[m,1:2],stemp]=polyfit(t,log(aa(:,m)),1)
#         # stemp is a structure, but we only want to keep the regression coefficient
#         # so let's extract that and save in s
#         #s(m)=stemp['normr']
#         #p[m,1:3]=B(:)

#     name['p'] = p
#     #name['s'] = s
#     name['aa'] = aa
#     return name


def get_damping(
    x_data, y_data, override, length_averaging, adv_fitting, threshold_value
):
    #
    # Args:
    #       data (vector of floats): The data.
    #       dwell(int): The dwell time set for this data.
    #       override (int): The number of turns to analyse (if NaN analyse everything)
    #       length_averaging(int): Determines the strength of the filtering out
    #                              of high frequecies in the data.
    #       advanced_fitting (bool): switches between simple (0)
    #                                and advanced fitting (1).
    #       threshold_value(float): The value considered to be the noise floor.
    #
    #   Returns:
    #       s(vector of floats): coefficients of the polynomial fit of the
    #                            magnitude of data
    #       delta(float): deviation of the magnitude data to the
    #                     fit of the magnitude data.
    #       p(vector of floats): coefficients of the polynomial fit of the
    #                            phase of data
    if override and override < len(y_data):
        y_data = y_data[1:override]

    if len(y_data) < 3:
        s = [None, None]
        delta = None
        p = None
    else:
        if adv_fitting == 0:
            [s, delta, p] = mbf_growdamp_basic_fitting(
                x_data, y_data, length_averaging, threshold_value
            )
        else:
            [s, delta, p] = mbf_growdamp_advanced_fitting(
                x_data, y_data, length_averaging, threshold_value
            )

    return s, delta, p


def get_growth(turns, data):
    mag_fit = np.polyfit(turns, np.log(abs(data)), 1)
    c1 = np.polyval(mag_fit, turns)
    delta = np.mean(abs(c1 - np.log(abs(data))) / c1)
    temp = np.unwrap(np.angle(data)) / (2 * np.pi)
    phase_fit = np.polyfit(turns, temp, 1)
    return mag_fit, delta, phase_fit


def get_stage_details(exp_data):
    if "seq1_capture_state" in exp_data:
        stage_names = []
        for n in range(len(exp_data["states"])):
            if "Discard" in exp_data[f"seq{n}_capture_state"]:
                stage_names[n] = "spacer"
            else:
                if "On" in exp_data[f"seq{n}_enable"]:
                    stage_names[n] = "growth"
                else:
                    if "Bank 2" in exp_data[f"seq{n}_bank_select"]:
                        stage_names[n] = "active"
                    else:
                        stage_names[n] = "passive"
        ck = 1
        # change the ordering so that the first stage in time is at index 1['']
        # works out which samples in the time series correspond to each stage['']
        end_of_stage = []
        recorded_stage_names = []
        samples_of_stage = []
        turns_of_stage = []

        for jjse in range(len(stage_names)):
            if "spacer" not in stage_names[jjse]:
                recorded_stage_names[ck] = stage_names[jjse]
                length_of_stage = exp_data["states"][jjse]["duration"]
                dwell_of_stage = exp_data["states"][jjse]["dwell"]
                if ck == 1:
                    end_of_stage[ck] = length_of_stage
                    samples_of_stage[ck] = range(end_of_stage[ck])
                    turns_of_stage[ck] = len(samples_of_stage[ck]) / dwell_of_stage
                else:
                    end_of_stage[ck] = end_of_stage[ck - 1] + length_of_stage
                    samples_of_stage[ck] = range(
                        (end_of_stage[ck - 1] + 1), end_of_stage[ck]
                    )
                    turns_of_stage[ck] = len(samples_of_stage[ck]) / dwell_of_stage

                ck = ck + 1
    else:
        # Old dataset use implict order in structure to order stages['']
        test = exp_data.keys()
        names = test["_turns" in test]
        names = names["spacer" not in names]
        turns_of_stage = np.zeros(len(names)).tolist()
        samples_of_stage = []
        recorded_stage_names = []
        for nrs in range(len(names)):
            turns_of_stage[nrs] = exp_data[names[nrs]]

        turns_of_stage = turns_of_stage.reverse()
        for nrs in range(len(names)):
            samples_of_stage[nrs] = range(
                np.sum(turns_of_stage[1 : nrs - 1]) + 1, np.sum(turns_of_stage[1:nrs])
            )

        for hs in range(len(names)):
            recorded_stage_names[hs] = names[hs].replace("_turns", "")

        recorded_stage_names = recorded_stage_names.reverse()
    return recorded_stage_names, samples_of_stage, turns_of_stage


def growdamp_all(
    mbf_axis,
    auto_setup="yes",
    plotting="yes",
    additional_save_location=None,
    excitation_setting="yes",
    excitation_location="tune",
    excitation_manual=0,
    pll_tracking="no",
    pll_bunches=400,
    pll_guard_bunches=10,
    bunches_monitored=np.ones(harmonic_number),
    capture_full_bunch_motion="no",
):
    # Top level def to run the growdamp measurements on the:
    # selected plane
    #   Args:
    #       mbf_axis(str): 'x','y', or 's'
    #       auto_setup(str): sets whether the setup scripts will be used to put the
    #                        system into a particular state[''] Default is yes.
    #       plotting(str): set whether the data is plotted as well as saved[''] Default
    #                      is yes.
    #       additional_save_location(str): fully defined filename to save the
    #                                      captured data to in addition to the
    #                                      main archive.
    #       excitation(str): sets whether the measurement uses an excitation to
    #                        drive a resonance or if the measurement just uses the natural beam coupling.
    #                        Defaults to 'yes'
    #       excitation_location(str): The location of the excitation in tune space.
    #                                 The default value is 'tune'.
    #       excitation_manual(float): if excitation_location is set to 'manual' then
    #                                 this defines the location of the excitation
    #                                 in tune space.
    #       pll_tracking (str): Sets if the excitation frequency follows the tune
    #                           jitter. Default is no
    #       pll_bunches (float): bunches the pll is active on.
    #       pll_guard_bunches (float): the number of bunches surrounding the pll
    #                                  bunches for which feedback is switched off.
    #       bunch_monitor(list(int)): This determines which bunches are monitored
    #                                 during the measurement. Defaults to and array
    #                                 of ones which means all bunches.
    #       capture_full_bunch_motion(str): Captures the centroid motion for the
    #                                       duration of the measuremnt.
    #                                       Defaults to no as this is a lot of data.
    # Example: growdamp_all('x')
    [root_string, harmonic_number, pv_names] = mbf_system_config
    pv_head = pv_names["hardware_names"][mbf_axis]
    # for archival investigations this allows filtering by machine state.
    # but for capture this is not needed so it set to empty.
    filter_conditions = []
    ## Constructing the different states for the sequencer. These will be arranged
    # in various configurations depending on the experiment requested.
    #
    # bank = 1 is Feedback off
    # bank = 2 is Feedback on
    #       tune_offset (float): Tune fraction to offset from the peak.
    #       dwell (int): number of turns at each point.
    #       durations (struct): number of points for each stage.
    if mbf_axis.lower() == "x" or mbf_axis.lower() == "y":
        growth = {}
        excitation = {}
        passive = {}
        active = {}
        spacer = {}
        # Passive Growth
        growth["duration"] = 2500
        growth["dwell"] = 1
        growth["capture"] = "Capture"
        growth["excitation"] = "Off"
        growth["excitation_level"] = "-48dB"
        growth["bank"] = 1
        # Excitation
        excitation["duration"] = 750
        excitation["dwell"] = 1
        excitation["capture"] = "Capture"
        excitation["excitation"] = "On"
        excitation["excitation_level"] = "-18dB"
        excitation["bank"] = 1
        # Passive decay (assuming no instability)
        passive["duration"] = 1500
        passive["dwell"] = 1
        passive["capture"] = "Capture"
        passive["excitation"] = "Off"
        passive["excitation_level"] = "-48dB"
        passive["bank"] = 1
        # Feedback active
        active["duration"] = 1500
        active["dwell"] = 1
        active["capture"] = "Capture"
        active["excitation"] = "Off"
        active["excitation_level"] = "-48dB"
        active["bank"] = 2
        # Feedback active but no capture
        spacer["duration"] = 4000
        spacer["dwell"] = 1
        spacer["capture"] = "Discard"
        spacer["excitation"] = "Off"
        spacer["excitation_level"] = "-48dB"
        spacer["bank"] = 2
        tune_offset = 0
    elif mbf_axis.lower() == "s":
        growth["duration"] = 10
        growth["dwell"] = 480
        growth["capture"] = "Capture"
        growth["excitation"] = "Off"
        growth["excitation_level"] = "-48dB"
        growth["bank"] = 1
        # Excitation
        excitation["duration"] = 10
        excitation["dwell"] = 480
        excitation["capture"] = "Capture"
        excitation["excitation"] = "On"
        excitation["excitation_level"] = "-18dB"
        excitation["bank"] = 1
        # Passive decay (assuming no instability)
        passive["duration"] = 10
        passive["dwell"] = 480
        passive["capture"] = "Capture"
        passive["excitation"] = "Off"
        passive["excitation_level"] = "-48dB"
        passive["bank"] = 1
        # Feedback active
        active["duration"] = 50
        active["dwell"] = 480
        active["capture"] = "Capture"
        active["excitation"] = "Off"
        active["excitation_level"] = "-48dB"
        active["bank"] = 2
        # Feedback active but no capture
        spacer["duration"] = 100
        spacer["dwell"] = 480
        spacer["capture"] = "Discard"
        spacer["excitation"] = "Off"
        spacer["excitation_level"] = "-48dB"
        spacer["bank"] = 2
        tune_offset = 0

    # getting general environment data.
    growdamp = machine_environment()
    ## Setting up the growdamp experiments.
    states = []
    state_names = []
    if excitation_setting == "no":
        states[2] = growth
        states[1] = active
        state_names[2] = "growth"
        state_names[1] = "active"
    else:
        states[6] = excitation
        states[5] = passive
        states[4] = spacer
        states[3] = excitation
        states[2] = active
        states[1] = spacer
        state_names[6] = "excitation"
        state_names[5] = "passive"
        state_names[4] = "spacer"
        state_names[3] = "excitation"
        state_names[2] = "active"
        state_names[1] = "spacer"
        if "lower_sideband" in excitation_location:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["lower_sideband"] + tune_offset
            )
        elif "upper_sideband" in excitation_location:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["upper_sideband"] + tune_offset
            )
        elif "manual" in excitation_location:
            excitation_tune = excitation_manual
        else:
            excitation_tune = (
                growdamp["tunes"][f"{mbf_axis}_tune"]["tune"] + tune_offset
            )

    # Add the extra data to the data structure['']
    growdamp["ax_label"] = mbf_axis
    growdamp["base_name"] = ["Growdamp_", mbf_axis, "_axis"]
    growdamp["harmonic_number"] = harmonic_number
    growdamp["excitation_tune"] = excitation_tune
    growdamp["states"] = states
    growdamp["state_names"] = state_names
    temp = get_variable[[pv_head, ":FIR:GAIN_S"]]
    growdamp["fir_gain"] = temp[1]
    growdamp["auto_setup"] = auto_setup
    growdamp["plotting"] = plotting
    growdamp["additional_save_location"] = additional_save_location
    growdamp["excitation_setting"] = excitation_setting
    growdamp["excitation_location"] = excitation_location
    growdamp["excitation_manual"] = excitation_manual
    growdamp["pll_tracking="] = pll_tracking
    growdamp["pll_bunches"] = pll_bunches
    growdamp["pll_guard_bunches"] = pll_guard_bunches
    growdamp["bunches_monitored"] = bunches_monitored
    growdamp["capture_full_bunch_motion"] = capture_full_bunch_motion

    if auto_setup == "yes":
        # putting the system into a known state['']
        setup_operational_mode(mbf_axis, "Feedback")
        # Setting the FIR gain to its original value['']
        set_variable[[pv_head, ":FIR:GAIN_S"], growdamp["fir_gain"]]

    growdamp["mbf_state"] = get_operational_mode(mbf_axis)
    # Setup the MBF ready for the measurement['']
    mbf_growdamp_setup(growdamp, pv_names)
    # Capturing data['']
    captured_data = mbf_growdamp_capture(growdamp, pv_names)
    # adding to output data structure['']
    data_fields = captured_data.keys()
    for je in range(1, len(data_fields)):
        growdamp[data_fields[je]] = captured_data[data_fields[je]]

    if auto_setup == "yes":
        setup_operational_mode(mbf_axis, "Feedback")
        # Setting the FIR gain to its original value['']
        set_variable[[pv_head, ":FIR:GAIN_S"], growdamp["fir_gain"]]
    else:
        reestablish_tune_measurement(mbf_axis)

    ## saving the data to a file
    save_to_archive(root_string, growdamp)
    if additional_save_location:
        scipy.savemat(additional_save_location, growdamp)

    ## Plotting data
    if plotting == "yes":
        mbf_growdamp_archival_retrieval(
            mbf_axis, [growdamp["time"], growdamp["time"]], filter_conditions
        )


def growdamp_archive_calculate_extents(input_data):
    extents = {}
    for ke in range(len(input_data)):
        data_field_names = input_data[ke].keys()
        for haw in range(1, len(data_field_names)):
            if ~data_field_names[haw] in extents:
                # initialisation
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][1] = input_data[ke][
                        data_field_names[haw]
                    ]
                    extents[data_field_names[haw]][2] = input_data[ke][
                        data_field_names[haw]
                    ]
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][1] = input_data[ke][
                            data_field_names[haw]
                        ]
                        extents[data_field_names[haw]][2] = input_data[ke][
                            data_field_names[haw]
                        ]
            else:
                if data_field_names[haw] == "time":
                    extents[data_field_names[haw]][1] = max(
                        [
                            extents[data_field_names[haw]][1],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                    extents[data_field_names[haw]][2] = min(
                        [
                            extents[data_field_names[haw]][2],
                            input_data[ke][data_field_names[haw]],
                        ]
                    )
                elif isnumeric(input_data[ke][data_field_names[haw]]):
                    if len(input_data[ke][data_field_names[haw]]) == 1:
                        extents[data_field_names[haw]][1] = max(
                            [
                                extents[data_field_names[haw]][1],
                                input_data[ke][data_field_names[haw]],
                            ]
                        )
                        extents[data_field_names[haw]][2] = min(
                            [
                                extents[data_field_names[haw]][2],
                                input_data[ke][data_field_names[haw]],
                            ]
                        )
    return extents


def growdamp_archive_data_conditioning(data_slice):
    field_nms = data_slice.keys()
    conditioned_data = {}
    for kef in range(1, len(field_nms)):
        # This section is to deal with variations in data naming
        # and structuring over the years['']
        if field_nms[kef] == "I_bpm":
            conditioned_data["current"] = data_slice["I_bpm"]
        elif field_nms[kef] == "fill":
            conditioned_data["fill_pattern"] = data_slice["fill"]
        elif field_nms[kef] == "id":
            conditioned_data["wiggler_field_I12"] = data_slice["id"]["i12field"]
            conditioned_data["wiggler_field_I15"] = data_slice["id"]["i15field"]
        elif field_nms[kef] == "life":
            conditioned_data["beam_lifetime"] = data_slice["life"]["bpm"]["life300sec"]
        elif field_nms[kef] == "RFread":
            conditioned_data["cavity1_voltage"] = data_slice["RFread"]
            conditioned_data["cavity2_voltage"] = data_slice["RFread"]
        else:
            conditioned_data[field_nms[kef]] = data_slice[field_nms[kef]]
    return conditioned_data


# FIXME
# def make_debug_graphs(nq, ksew, turns, stage_data, graph_title, keep_graphs):
#     if nq == 1:
#         h = gobjects(n_modes, 1)

#     if find(debug_modes == nq, 1):
#         debug_turns = turns - turns[0]
#         length_average = 20
#         [debug_s_basic, delta_passive_s_basic, _1] = get_damping(
#             debug_turns, stage_data, None, length_average, 0, threshold_value
#         )
#         debug_fit_basic = np.polyval(debug_s_basic, passive_turns)
#         [debug_s_advanced, delta_passive_s_advanced, _1] = get_damping(
#             debug_turns, stage_data, None, length_average, 1, threshold_value
#         )
#         debug_fit_advanced = np.polyval(debug_s_advanced, debug_turns)
#         if ksew == 1:
#             h[nq] = figure("Position", [20, 40, 800, 800])
#             t = tiledlayout(nstages, 1, "TileSpacing", "Compact")
#             fig.suptitle(t, graph_title, "Interpreter", "None")
#             plt.xlabel(t, "Turns")
#             plt.ylabel(t, "Signal (a[])")

#         ax[ksew] = nexttile
#         fig.suptitle([stage_name, "(Index ", (nq), ")"])
#         plt.plot(debug_turns, stage_data, "DisplayName", "Data")
#         plt.plot(
#             debug_turns,
#             np.exp(debug_fit_basic),
#             "r",
#             "DisplayName",
#             f"Basic fit: length av = {length_average}"
#             f"Fit error = {round(delta_passive_s_basic * 1e3) / 1e3}",
#             "LineWidth",
#             2,
#         )
#         plt.plot(
#             passive_turns,
#             np.exp(debug_fit_advanced),
#             ":r",
#             "DisplayName",
#             f"Advanced fit: length av = {length_average}"
#             f" Fit error = '{round(delta_passive_s_advanced * 1e3) / 1e3}",
#             "LineWidth",
#             2,
#         )
#         legend
#         if ksew == nstages:
#             linkaxes(ax, "x")
#             if keep_graphs == 0:
#                 close(h(nq))


def mbf_analysis_reorganise_for_parameter_sweep(dr, param, parameter_step_size):
    # Takes a set of results and a vector of the corresponding
    # parameter values (given by param)[''] Sorts them into order
    # and averages those data sets which are closer that the parameter step,
    # as defined by parameter_step_size
    #
    # example: [out_dr, out_param] = mbf_analysis_reorganise_for_parameter_sweep(dr, [5,6,7], 20)
    # ensure the ordering
    [param, I] = np.sort(param)
    section_indicies = []
    acc = 1
    for ns in range(param[0], parameter_step_size, param[-1]):
        ind = [
            index
            for (index, item) in enumerate(param)
            if item >= ns and item < ns + parameter_step_size
        ]
        if not ind:
            continue

        section_indicies[ind] = acc
        acc = acc + 1

    out_param = np.zeros(acc - 1)
    for ess in range(acc):
        out_param[ess] = (
            round((np.median(param[section_indicies == ess])) / parameter_step_size)
            * parameter_step_size
        )

    dr = sort_data_in_stucture(dr, I, 1)
    # Take the mean of all the data sets within one parameter step['']
    out_dr = mean_steps_data_in_stucture(dr, section_indicies, acc)
    return out_dr, out_param


def mbf_growdamp_advanced_fitting(x_data, y_data, length_averaging, threshold_value):
    # Fits to an exponential decay['']
    #
    # Args:
    #       x_data (vector of floats): The turns['']
    #       y_data (vector of floats): The data['']
    #       length_averaging (int): number of points for the box car average to work
    #                               with['']
    #       threshold_value (float): The data value defined as the noise floor['']
    #
    #   Returns:
    #       s(vector of floats): coefficients of the polynomial fit of the
    #                            magnitude of data
    #       delta(float): deviation of the magnitude data to the
    #                     fit of the magnitude data['']
    #       p(vector of floats): coefficients of the polynomial fit of the
    #                            phase of data
    # Truncate data at the point the decay hits the noise floor['']
    noise_floor_intercept_pd = [
        index for (index, item) in enumerate(abs(y_data)) if item <= threshold_value
    ]
    if noise_floor_intercept_pd:
        y_data[noise_floor_intercept_pd:-1] = []
        x_data[noise_floor_intercept_pd:-1] = []

    # Smooth the data
    if len(y_data) > length_averaging * 8:
        mm = movmean(y_data, length_averaging)

    # take the log of the data as we expect an exponential decay[''] meaning that the
    # log(data) should be linear
    mag = np.log(abs(mm))
    # Get an initial starting value['']
    p_initial = np.polyfit(x_data, mag, 1)
    # initial_fit_line = polyval(p_initial, 1:len(mm))
    if p_initial(1) < 0:
        # damping
        # find the max so as to allow any initial rise in the data to be
        # removed['']
        [_1, dm_loc] = max(mag)
        #     dm_loc = 2 * dm_loc
    else:
        # growth
        dm_loc = 0

    x_ax = range(len(mag)) - dm_loc
    n_tests = 200
    # compare linear fits to the data['']
    vals = np.linspace(p_initial(1), p_initial(1) - 2e-7, n_tests)
    # sweep the gradient[''] Large changes in sample length indicate that a large
    # fraction of the line has moved from below the line to above it['']
    sample_length = []
    for gra in range(n_tests):
        y = vals(gra) * x_ax + mag(dm_loc + 1)
        weighted_error = (
            mag[dm_loc + 1 : -1] - y
        )  # ['']* linspace(len(mm)-1 - dm_loc, 0 , length(mm)-dm_loc)
        weighted_error[weighted_error > 0] = 0
        [_1, min_loc] = np.min(weighted_error)
        sample_length_temp = [
            index
            for (index, item) in enumerate(weighted_error[min_loc:-1])
            if item == 0
        ]
        if not sample_length_temp:
            sample_length[gra] = len(x_ax)
        else:
            sample_length[gra] = sample_length_temp + min_loc - 1

        if sample_length(gra) < 3:
            break

    [_1, I] = np.min(np.diff(sample_length))
    if I != 1:
        I = I - 1

    s = [vals(I), mag(dm_loc + 1)]
    c = np.polyval(s, x_data)
    delta = np.mean(abs(c - mag))
    temp = np.unwrap(np.angle(mm)) / (2 * np.pi)
    p = np.polyfit(x_data, temp, 1)
    return s, delta, p


def mbf_growdamp_analysis(
    exp_data,
    active_override=None,
    passive_override=None,
    advanced_fitting=0,
    length_averaging=20,
    debug=0,
    debug_modes=range(harmonic_number),
    keep_debug_graphs=0,
):
    # takes the data from mbf growdamp capture and fits it with a series of
    # linear fits to get the damping times for each mode['']
    #
    #   Args:
    #       exp_data (structure): Contains the systems setup and the data
    #                             captured['']
    #       active_override (int|NaN): Sets the number of turns to analyse['']
    #       passive_override (int|NaN): Sets the number of turns to analyse['']
    #       advanced_fitting (bool): switches between simple (0)
    #                                and advanced fitting (1)['']
    #       length_averaging(int): Determines the strength of the filtering out
    #                              of high frequecies in the data['']
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection of appropriate overrides['']
    #       debug_modes(list of ints): the modes to output the debug graphs for['']
    #       keep_debug_graphs(bool): selects if the debug graphs are overwritten (0) or
    #                                kept (1)['']
    #
    #   Returns:
    #       output_data (struct): data is structured as [stage][''][mesurement]
    #                               measurements are: damping time, offset,
    #                               error relative to fit, frequency shift['']
    #                               all measurements are a vector the length of the
    #                               number of modes['']
    #
    # Example: output_data = tmbf_growdamp_analysis(exp_data)
    harmonic_number = len(exp_data["fill_pattern"])
    output_state = 1
    if "gddata" in exp_data and "data" not in exp_data:
        exp_data["data"] = exp_data["gddata"]

    if "data" not in exp_data:
        return

    # Sometimes there is a problem with data transfer[''] By truncating the data
    # length to a multiple of the harmonic number the analysis can proceed['']
    exp_data["data"] = exp_data["data"][
        1 : -np.rem(len(exp_data["data"]), harmonic_number)
    ]
    exp_data["data"] = exp_data["data"][
        1 : -np.rem(len(exp_data["data"]), harmonic_number)
    ]
    exp_data["data"] = np.reshape(exp_data["data"], [], harmonic_number)
    n_modes = exp_data["data"].shape[0]
    # Find the name of each stage['']
    [recorded_stage_names, samples_of_stage, turns_of_stage] = get_stage_details(
        exp_data
    )
    # conditioning names to conform to current scheme['']
    recorded_stage_names = recorded_stage_names.replace("excitation", "growth")
    recorded_stage_names = re.sub("act$", "active", recorded_stage_names)
    recorded_stage_names = re.sub("nat$", "passive", recorded_stage_names)
    # growth_mag_fit = zeros(n_modes, 2)
    # growth_delta = zeros(n_modes, 1)
    # growth_phase_fit = zeros(n_modes, 2)
    # active_mag_fit = zeros(n_modes, 2)
    # active_delta = zeros(n_modes, 1)
    # active_phase_fit = zeros(n_modes, 2)
    # passive_mag_fit = zeros(n_modes, 2)
    # passive_delta = zeros(n_modes, 1)
    # passive_phase_fit = zeros(n_modes, 2)
    # The 'noise' floor['']
    threshold_value_part = np.array(ndmin=2)
    for ksew in range(1, len(recorded_stage_names)):
        threshold_value_part[ksew, :] = np.min(
            exp_data["data"][:, samples_of_stage[ksew]], [], 2
        )

    threshold_value = np.min(threshold_value_part)
    if debug == 1:
        pass
        # In a separate loop otherwise all the checks really slow the code down.
        # FIXME
        # for nq in range(1, n_modes):
        #     for ksew in range(1, len(recorded_stage_names)):
        #         make_debug_graphs(
        #             nq,
        #             ksew,
        #             turns_of_stage[ksew],
        #             stage_data,
        #             exp_data["filename"],
        #             keep_debug_graphs,
        #         )

    # Extracting inputs into separate variables as it really kills code performance
    # to keep indexing into the structures['']
    output_data = {}
    for nq in range(n_modes):
        growth_ck = 1
        active_ck = 1
        passive_ck = 1
        for ksew in range(1, len(recorded_stage_names)):
            single_data = exp_data["data"](nq, samples_of_stage[ksew])
            if "growth" in recorded_stage_names[ksew]:
                # Growth
                [growth_mag_fit, growth_delta, growth_phase_fit] = get_growth(
                    range(turns_of_stage[ksew]), single_data
                )
                output_data[f"{recorded_stage_names[ksew]}{growth_ck}"]["damping_rate"][
                    nq
                ] = growth_mag_fit[0]
                output_data[f"{recorded_stage_names[ksew]}{growth_ck}"]["offset"][
                    nq
                ] = growth_mag_fit[1]
                output_data[f"{recorded_stage_names[ksew]}{growth_ck}"]["error"][nq] = (
                    growth_delta
                )
                output_data[f"{recorded_stage_names[ksew]}{growth_ck}"][
                    "frequency_shift"
                ][nq] = growth_phase_fit[0]
                growth_ck = growth_ck + 1
            elif "active" in recorded_stage_names[ksew]:
                # Active damping
                [active_mag_fit, active_delta, active_phase_fit] = get_damping(
                    range(turns_of_stage[ksew]),
                    single_data,
                    active_override,
                    length_averaging,
                    advanced_fitting,
                    threshold_value[nq],
                )
                output_data[f"{recorded_stage_names[ksew]}{active_ck}"]["damping_rate"][
                    nq
                ] = active_mag_fit[0]
                output_data[f"{recorded_stage_names[ksew]}{active_ck}"]["offset"][
                    nq
                ] = active_mag_fit[1]
                output_data[f"{recorded_stage_names[ksew]}{active_ck}"]["error"][nq] = (
                    active_delta
                )
                output_data[f"{recorded_stage_names[ksew]}{active_ck}"][
                    "frequency_shift"
                ][nq] = active_phase_fit[0]
                active_ck = active_ck + 1
            elif "passive" in recorded_stage_names[ksew]:
                # Passive damping
                [passive_mag_fit, passive_delta, passive_phase_fit] = get_damping(
                    range(turns_of_stage[ksew]),
                    single_data,
                    passive_override,
                    length_averaging,
                    advanced_fitting,
                    threshold_value[nq],
                )
                output_data[f"{recorded_stage_names[ksew]}{passive_ck}"][
                    "damping_rate"
                ][nq] = passive_mag_fit[0]
                output_data[f"{recorded_stage_names[ksew]}{passive_ck}"]["offset"][
                    nq
                ] = passive_mag_fit[1]
                output_data[f"{recorded_stage_names[ksew]}{passive_ck}"]["error"][
                    nq
                ] = passive_delta
                output_data[f"{recorded_stage_names[ksew]}{passive_ck}"][
                    "frequency_shift"
                ][nq] = passive_phase_fit[0]
                passive_ck = passive_ck + 1

    return output_data, output_state


def mbf_growdamp_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    active_override=None,
    passive_override=None,
    advanced_fitting=0,
    error_threshold=0.1,
    debug=0,
):
    # Takes the data extracted by mbf_growdamp_archival_retreval and operates
    # across all datasets[''] Then plots the results['']
    #
    # Args:
    #       data_requested (cell array of structures) : Data to be analysed['']
    #       analysis_type (str): To select the type of analysis
    #                       (collate, average, parameter_sweep)
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
    #                              anal_type set to 'parameter sweep')
    #       parameter_step_size (float): Defines the spacing of the steps in
    #                                    the parameter sweep['']
    #                                    Multiple data sets which are on the same
    #                                    step will be averaged[''] (only needed if
    #                                    anal_type set to 'parameter sweep')
    #       overrides (list of ints): Two values setting the number of turns to
    #                                    analyse (passive, active)
    #       debug(int): if 1 then outputs graphs of individual modes to allow
    #                                    selection nof appropriate overrides['']
    #
    # Returns:
    #         dataset containing
    #         dr_passive (numeric matrix): Passive damping time['']
    #                                      (bunches vs datasets)
    #         dr_active (numeric matrix): Passive damping time['']
    #                                      (bunches vs datasets)
    #         error_passive (numeric matrix): Error of the fit for the passive
    #                                         damping rate['']
    #         error_active (numeric matrix): Error of the fit for the active
    #                                        damping rate['']
    #         times (numeric vector): Datetimes of the datasets['']
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis['']
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = mbf_growdamp_archival_analysis(data_requested, 'average')

    # #condition the data in order to harmonise data changes made over time['']
    # for nd = len(data_requested):-1:1
    #     data_requested[nd] = growdamp_archive_data_conditioning(data_requested[nd])
    # end
    ck = 1
    times = []
    param_vals = np.zeros(len(data_requested))
    for nd in range(len(data_requested)):
        if "I_dcct5" in data_requested[nd]:
            data_requested[nd]["current"] = data_requested[nd]["I_dcct5"]

        [data, data_state] = mbf_growdamp_analysis(
            data_requested[nd],
            active_override=active_override,
            passive_override=passive_override,
            advanced_fitting=advanced_fitting,
            debug=debug,
        )
        if data_state == 0:
            continue

        times[ck] = datetime.datetime(data_requested[nd]["time"])
        if analysis_type == "parameter_sweep":
            param_vals[ck] = data_requested[nd][sweep_parameter]

        states = data.keys()
        dataset = {}
        for st in range(1, len(states)):
            meass = data[states[st]].keys()
            for ms in range(len(meass)):
                dataset[states[st]][meass[ms]][ck, :] = data[states[st]][meass[ms]]

        print(".")
        ck = ck + 1

    # # Removing datasets whose mean error is < error_threshold for the passive section['']
    # error_av_p = mean(dataset['passive']['error'],2,'omitnan')
    # wanted = find(abs(error_av_p) < p['Results']['error_threshold'])
    # states = fieldnames(dataset)
    #     for st = 1:len(states)
    #         meass = fieldnames(dataset[states[st]])
    #         for ms = 1:len(meass)
    #             dataset[states[st]][meass[ms]] = dataset[states[st]][meass[ms]][wanted,:]
    #         end #for
    #     end #for
    # times = times(wanted)
    # if strcmp(p['Results']['analysis_type'], 'parameter_sweep')
    #     param = param(wanted)
    # end #if
    experimental_setup = {}

    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        f_names = dataset.keys()
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        if not dataset[f_names[1]]["damping_rate"]:
            print("No data left. Try changing analysis settings.")
            return
        else:
            [dataset, experimental_setup["param"]] = (
                mbf_analysis_reorganise_for_parameter_sweep(
                    dataset, param_vals, parameter_step
                )
            )

    elif analysis_type == "average":
        print(
            'Archive:Growdamp:setting Ignoring the last two parameters as "average" is set'
        )
        states = dataset.keys()
        for st in range(len(states)):
            meass = dataset[states[st]].keys()
            for ms in range(len(meass)):
                dataset[states[st]][meass[ms]] = np.mean(dataset[states[st]][meass[ms]])


def mbf_growdamp_archival_plotting(requested_data, dataset, times, experimental_setup):
    # Plots the data processed by mbf_growdamp_archival_analysis['']
    # Args:
    #       dataset (struct): containing
    #      dr_passive (numeric matrix): Passive damping rate['']
    #                                   (bunches vs datasets)
    #      dr_active (numeric matrix): Active damping rate['']
    #                                   (bunches vs datasets)
    #      error_passive (numeric matrix): Error of the fit for the passive
    #                                      damping rate['']
    #      error_active (numeric matrix): Error of the fit for the active
    #                                     damping rate['']
    #      times (numeric vector): Datetimes of the datasets['']
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis['']
    #      plot_error_graphs (anything): if present the code will plot the results
    #                                    of the fit errors['']
    #
    # Example: mbf_growdamp_archival_plotting(requested_data, dataset, error_active,
    #                                           times, setup, selections, extents)
    # Only do something if there is data to do something with['']
    if not times:
        return

    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = "Damping rates for different modes as a def of "
        f"{experimental_setup['sweep_parameter']}"
        f"'Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
    else:
        graph_title = "Damping rates for different modes"

    mbf_archival_plotting_setup(requested_data, times, experimental_setup)
    [_2, harmonic_number, _1] = mbf_system_config
    x_plt_axis = range(harmonic_number)
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
    f_names = dataset.keys()

    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    fig.suptitle(graph_title)
    fig.xlabel("Mode")
    cks = 1
    for jse in f_names:
        if experimental_setup["anal_type"] == "parameter_sweep":
            graph_labels = []
            for hw in range(1, len(experimental_setup["param"])):
                graph_labels[hw] = experimental_setup["param"](hw)

            plt.plot(
                x_plt_axis,
                dataset[jse]["damping_rate"],
                "LineWidth",
                2,
            )
            plt.legend(graph_labels)
        else:
            populate_graph(
                dataset[jse]["damping_rate"],
                years_input,
                years_colours,
                times,
                x_plt_axis,
            )

        plt.plot(
            [x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off"
        )
        plt.ylabel([jse, " rates (1/turns)"])
        if cks == 2:
            leg = plt.legend("show")
            leg["Layout"]["Tile"] = "east"
        else:
            plt.legend("off")

        ymin = min(min(dataset[f_names[jse]]["damping_rate"], [], 2))
        ymin = min(ymin, 0)

        ymax = max(max(dataset[f_names[jse]]["damping_rate"], [], 2))
        ymax = ymax + ymax / 10
        ymax = max(ymax, 0)

        plt.ylim([ymin, ymax])
        plt.xlim([min(x_plt_axis), max(x_plt_axis)])
        cks += 1

    # add labels if it is a parameter sweep['']
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"])):
            labels[tb] = experimental_setup["param"](tb)

        plt.legend(labels)

    if experimental_setup["anal_type"] == "parameter_sweep":
        fig, _1 = plt.subplot_mosaic(
            [["upper left", "upper right"], ["lower left", "lower right"]],
            figsize=(5.5, 3.5),
            layout="constrained",
        )
        fig.suptitle(
            f"Damping rates vs {experimental_setup['sweep_parameter']} in the "
            f"{experimental_setup['axis']} axis",
        )
        plt.xlabel(experimental_setup["sweep_parameter"])
        for jse in f_names:
            plt.plot(experimental_setup["param"], dataset[f_names[jse]]["damping_rate"])
            plt.ylabel([f_names[jse], " rates (1/turns)"])
            plt.plot(
                experimental_setup["param"][0],
                experimental_setup["param"][-1],
                [0, 0],
                "r:",
                "HandleVisibility",
                "off",
            )

        if experimental_setup["sweep_parameter"] == "current":
            fig, _1 = plt.subplot_mosaic(
                [["upper left", "upper right"], ["lower left", "lower right"]],
                figsize=(5.5, 3.5),
                layout="constrained",
            )
            fig.suptitle("Extrapolated data")
            plt.xlabel(experimental_setup["sweep_parameter"])
            x1 = range(300)
            for jse in f_names:
                passive_mode_rate = np.zeros(len(dataset[jse]["damping_rate"]))
                for ks in range(1, len(dataset[jse]["damping_rate"])):
                    P = np.polyfit(
                        experimental_setup["param"],
                        dataset[jse]["damping_rate"][:, ks],
                        1,
                    )
                    passive_mode_rate[ks] = P[0]
                    P_start = [
                        index
                        for (index, item) in enumerate(x1)
                        if item < min(experimental_setup["param"])
                    ]
                    P_points = np.polyval(P, x1)
                    # Find the first time after the lowest current that the
                    # extrapolation goes negative.
                    P_loc = [
                        index
                        for (index, item) in enumerate(np.sign(P_points[P_start:-1]))
                        if item == -1
                    ]
                    if P_loc:
                        plt.plot(
                            x1,
                            P_points,
                            "DisplayName",
                            f"Mode {x_plt_axis(ks)}: {x1(P_loc)} mA",
                            "LineWidth",
                            2,
                        )
                        plt.plot(
                            experimental_setup["param"],
                            dataset[jse]["damping_rate"][:, ks],
                            "ko",
                            "HandleVisibility",
                            "off",
                        )

                plt.xlabel(experimental_setup["sweep_parameter"])
                plt.ylabel([jse, " rates (1/turns)"])
                #         plt.legend('Location', 'eastoutside')
                plt.legend("off")
                plt.plot([x1[0], x1[-1]], [0, 0], "r:", "HandleVisibility", "off")


def populate_graph(input_data, years_input, times, x_plt_axis):
    if not input_data:
        return
    years = []
    states = []
    cols = []

    y_max = max(max(input_data))
    y_min = min(min(input_data))
    for esr in range(years_input.shape[0]):
        years[esr] = years_input[esr][0]
        states[esr] = 0
        cols[esr] = years_input[esr][1]

    year_list = times.year
    if len(np.unique(year_list)) < 2:
        for ner in range(input_data.shape[0]):
            sample_time = times[ner].strftime("%a %d %b %Y, %I:%M%p")
            plt.plot(
                x_plt_axis,
                input_data[ner, :],
                "DisplayName",
                sample_time,
                "LineWidth",
                2,
            )

    else:
        for ner in range(input_data.shape[0]):
            years_ind = [
                index for (index, item) in enumerate(year_list[ner]) if item == years
            ]
            if states(years_ind) == 0:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "DisplayName",
                    (year_list(ner)),
                    "LineWidth",
                    2,
                )
                states[years_ind] = 1
            else:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "HandleVisibility",
                    "off",
                    "LineWidth",
                    2,
                )

    plt.xlim([x_plt_axis[0], x_plt_axis[-1]])
    plt.ylim([y_min, y_max])
    plt.legend("show")


def mbf_growdamp_archival_retrieval(
    ax,
    date_range,
    filter_conditions,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    active_override=None,
    passive_override=None,
    advanced_fitting=0,
    debug=0,
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
    #       analysis_type(str): determines the type of analysis to run 'collate' or
    #                           'sweep', the default is 'collate'.
    #       sweep_parameter (str): Parameter to be used[''] This name must exist
    #                              in the data structure[''] (only needed if
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
    # Example: mbf_growdamp_archival_retrieval('x',
    #          [datetime(2023, 1, 1), datetime("now")])
    selection_name = ["Growdamp_", ax, "_axis"]
    requested_data = mbf_archival_dataset_retrieval(
        selection_name,
        date_range,
        bypass_index=bypass_index,
        metadata_only=metadata_only,
    )
    if len(requested_data) == 1:
        [dataset, _2, _1] = mbf_growdamp_archival_analysis(
            requested_data,
            analysis_type="collate",
            active_override=active_override,
            passive_override=passive_override,
            advanced_fitting=advanced_fitting,
            debug=debug,
        )
        mbf_growdamp_plot_summary(dataset, requested_data[1])
    else:
        # Only keeping datasets that satify the requested machine conditions['']
        conditioned_data = mbf_archival_conditional_filtering(
            requested_data, filter_conditions
        )
        if not conditioned_data:
            print("No data meeting the requirements")
        else:
            if analysis_type == "collate":
                [dataset, times, setup] = mbf_growdamp_archival_analysis(
                    conditioned_data,
                    analysis_type="collate",
                    active_override=active_override,
                    passive_override=passive_override,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            elif analysis_type == "sweep":
                [dataset, times, setup] = mbf_growdamp_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                    active_override=active_override,
                    passive_override=passive_override,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )

            setup["axis"] = ax
            mbf_growdamp_archival_plotting(conditioned_data, dataset, times, setup)

    return dataset, times, setup


def mbf_growdamp_basic_fitting(x_data, y_data, length_averaging, threshold_value):
    # Fits to an exponential decay['']
    #
    # Args:
    #       x_data (vector of floats): The turns['']
    #       y_data (vector of floats): The data['']
    #       length_averaging (int): number of points for the box car average to work
    #                               with['']
    #       threshold_value (float): The data value defined as the noise floor['']
    #
    #   Returns:
    #       s(vector of floats): coefficients of the polynomial fit of the
    #                            magnitude of data
    #       delta(float): deviation of the magnitude data to the
    #                     fit of the magnitude data['']
    #       p(vector of floats): coefficients of the polynomial fit of the
    #                            phase of data
    # Smooth the data
    if len(y_data) > length_averaging * 8:
        y_data = movmean(y_data, length_averaging)

    # Truncate data at the point the decay hits the noise floor['']
    noise_floor_intercept_pd = [
        index for (index, item) in enumerate(abs(y_data)) if item <= threshold_value
    ]
    if noise_floor_intercept_pd:
        y_data[noise_floor_intercept_pd:-1] = []
        x_data[noise_floor_intercept_pd:-1] = []

    # Take the log and fit a linear to it
    mag = np.log(abs(y_data))
    s = np.polyfit(x_data, mag, 1)
    c = np.polyval(s, x_data)
    # Construct an error metric['']
    delta = np.mean(abs(c - mag))
    temp = np.unwrap(np.angle(y_data)) / (2 * np.pi)
    p = np.polyfit(x_data, temp, 1)
    return s, delta, p


def mbf_growdamp_capture(input_settings, pv_names):
    # Gathers data on the machine environment['']
    # Runs a growdamp experiment on an already setup system['']
    # Saves the resultant data['']
    #
    #   Args:
    #       input_settings(struct): contains all the setup information['']
    #       pv_names(struct): contains the locations of all the machine parameters['']
    #
    # example data = mbf_growdamp_capture(input_settings, pv_names)
    growdamp = {}
    mbf_axis = input_settings["mbf_axis"]
    capture_full_bunch_motion = input_settings["capture_full_bunch_motion"]
    pv_head = pv_names["hardware_names"][mbf_axis]
    pv_head_mem = pv_names["hardware_names"]["mem"][mbf_axis]
    triggers = pv_names["tails"]["triggers"]
    Sequencer = pv_names["tails"]["Sequencer"]
    FIR = pv_names["tails"]["FIR"]
    # Getting feedback gain
    growdamp["FIR_gain"] = [pv_head, FIR["gain"]]
    start_state = get_variable([pv_head, Sequencer["start_state"]])
    # getting the state of the sequencer['']
    exp_state_names = []
    for n in range(start_state):
        entries = Sequencer[f"seq{n}"].keys()
        for en in range(len(entries)):
            growdamp[f"seq{n}_{entries[en]}"] = get_variable(
                f"{pv_head}{Sequencer[f'seq{n}'][entries[en]]}"
            )

    growdamp["exp_state_names"] = exp_state_names
    ## Preparing system for data capture
    set_variable(f"{pv_head_mem}{triggers['MEM']['disarm']}", 1)
    time.sleep(0.5)  # Letting the hardware sort itself out['']
    # Arm the memory so that it cycles[''] This means that all the status PV are
    # updated[''] Otherwise the code will say the memory is not ready as the status is
    # stale['']
    set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
    time.sleep(2)  # Letting the hardware sort itself out['']
    temp1 = get_variable(f"{pv_head_mem}{pv_names['tails']['TRG']['memory_status']}")
    if temp1 != "Idle":
        set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
    else:
        print("Memory is not ready trying again")
        time.sleep(5)  # Letting the hardware sort itself out['']
        temp1 = get_variable(
            f"{pv_head_mem}{pv_names['tails']['TRG']['memory_status']}"
        )
        if temp1 != "Idle":
            set_variable(f"{pv_head_mem}{triggers['MEM']['arm']}", 1)
        else:
            raise ValueError("growdamp:memoryNotReady Memory is not ready please rerun")

    # Disarm, so that the current settings will be picked up upon arming['']
    set_variable(f"{pv_head}{triggers['SEQ']['disarm']}", 1)
    ## Trigger the measurement
    if mbf_axis.lower() == "x" or mbf_axis.lower() == "s":
        chan = 0
    elif mbf_axis.lower() == "y":
        chan = 1

    if mbf_axis.lower() == "s":
        mem_lock = 180
    else:
        mem_lock = 30

    # Arm
    set_variable(f"{pv_head}{triggers['SEQ']['arm']}", 1)
    # Trigger
    set_variable(f"{pv_head_mem}{triggers['soft']}", 1)
    # download the data
    [growdamp["data"], growdamp["data_freq"], _1] = mbf_read_det(
        pv_head_mem, "axis", chan, "lock", mem_lock
    )
    ## Capturing full bunch motion data
    if capture_full_bunch_motion.lower() == "yes":
        turn_count = 1250[""] * 400
        turn_offset = 0
        growdamp["bunch_motion"] = mbf_read_mem(
            pv_head_mem, turn_count, "offset", turn_offset, "channel", 0, "lock", 60
        )
    return growdamp


def mbf_growdamp_plot_summary(data, metadata, plot_mode="pos"):
    # Plots the driven growth rates, and the active and pasive damping rates
    # across all modes['']
    #
    # Args:
    #       poly_data (3 by 3 matrix): axis 1 is coupling mode['']
    #                                  axis 2 is expermental state,
    #                                  excitation, natural damping, active damping)['']
    #                                  axis 3 is damping time, offset and
    #                                  fractional error['']
    #       frequency_shifts (list of floats): The frequency shift of each mode['']
    #       metadata (structure): setup information['']
    #       axis: 'x', 'y' or 's'
    #       plot_mode: 'pos' or 'neg'[''] Determines if plot modes 0:harmonic_number or
    #       -harmonic_number/2:harmonic_number/2
    #
    # Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts, 'passive')

    # Getting the desired system setup parameters['']
    stages = data.keys()
    harmonic_number = len(data[stages[1]]["damping_rate"])
    ## Adjust the horizontal axis setup
    if plot_mode.lower() == "pos":
        x_plt_axis = range(harmonic_number)
        labelX = "Mode"
        for nse in range(len(stages)):
            data["modes"][stages[nse]] = data[stages[nse]]

    elif plot_mode.lower() == "neg":
        x_plt_axis = range(harmonic_number) - harmonic_number / 2
        labelX = "Mode"
        for nse in range(1, len(stages)):
            data["modes"][stages[nse]] = np.fft.circshift(
                data[stages[nse]], -harmonic_number / 2, 1
            )

    ## Calculate the relative frequency shifts between stages['']
    ck = 1
    freq_diff_names = []
    freq_diffs = np.array(ndmin=2)
    for wnf in range(1, len(stages)):
        for ntd in range(1, len(stages)):
            if wnf != ntd:
                freq_diffs[ck, :] = (
                    data["modes"][stages[wnf]]["frequency_shift"]
                    - data["modes"][stages[ntd]]["frequency_shift"]
                )
                freq_diff_names[ck] = [stages[wnf], " - ", stages[ntd]]
                ck = ck + 1

    # Convert to frequencies
    info_tag = ""
    for nse in range(len(stages)):
        measurements = data[stages[nse]].keys()
        for bes in range(len(measurements)):
            if metadata["ax_label"].lower() == "s" and "tunes" not in metadata:
                metadata["tunes"]["s_tune"]["tune"] = 0.004
                info_tag = "assumed tune 0.004"

            [x_plt_axis_f, data["f"][stages[nse]][measurements[bes]]] = (
                mode_to_frequency(
                    metadata["RF"],
                    harmonic_number,
                    metadata["tunes"][""]([metadata["ax_label"], "_tune"])["tune"],
                    data[stages[nse]][measurements[bes]],
                )
            )

    x_plt_axis_f = x_plt_axis_f * 1e-6
    labelX_f = "Frequency (MHz)"
    ## Plotting
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    mplt.annotation(
        "textbox",
        [
            0.4,
            0.9,
            0.2,
            0.2,
        ],
        "FitBoxToText",
        "on",
        "LineStyle",
        "none",
        "HorizontalAlignment",
        "center",
        "String",
        f"MBF growdamp results {metadata['ax_label']} axis "
        f"{metadata['time'].strftime('%a %d %b %Y, %I:%M%p')}"
        f"Current: {(round(metadata['current']))} mA"
        f"More -ve damping rates means more damping. "
        f"Active should always be below passive.",
    )
    mplt.annotation(
        "textbox",
        [0.02, 0.9, 0.2, 0.2],
        "Color",
        "red",
        "String",
        info_tag,
        "FitBoxToText",
        "on",
    )
    # plt.xlabel(t, labelX)
    for ns in range(len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["error"],
                "DisplayName",
                stages[ns],
            )

    fig.ylabel("Error")
    fig.xlim([x_plt_axis(1), x_plt_axis[-1]])
    for ns in range(len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["damping_rate"],
                "DisplayName",
                stages[ns],
            )

    plt.ylabel("Damping rates (1/turns)")
    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    for ns in range(len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["frequency_shift"],
                "DisplayName",
                stages[ns],
            )

    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    plt.ylabel("Difference from excitation tune")
    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    plt.xlabel(labelX)
    for ns in range(len(stages)):
        if "growth" in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["error"],
                "DisplayName",
                stages[ns],
            )

    plt.ylabel("Error")
    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    for ns in range(1, len(stages)):
        if "growth" in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["damping_rate"],
                "DisplayName",
                stages[ns],
            )

    plt.ylabel("Growth rates (1/turns)")
    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    for ns in range(1, len(stages)):
        if "growth" in stages[ns]:
            plt.plot(
                x_plt_axis,
                data["modes"][stages[ns]]["frequency_shift"],
                "DisplayName",
                stages[ns],
            )

    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    plt.ylabel("Difference from excitation tune")
    plt.xlim([x_plt_axis(1), x_plt_axis[-1]])
    plt.xlabel(labelX)
    for ns in range(1, len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis_f, data["f"][stages[ns]]["error"], "DisplayName", stages[ns]
            )

    plt.ylabel("Error")
    plt.xlim([x_plt_axis_f(1), x_plt_axis_f[-1]])
    for ns in range(1, len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis_f,
                data["f"][stages[ns]]["damping_rate"],
                "DisplayName",
                stages[ns],
            )

    plt.ylabel("Damping rates (1/turns)")
    plt.xlim([x_plt_axis_f(1), x_plt_axis_f[-1]])
    for ns in range(1, len(stages)):
        if "growth" not in stages[ns]:
            plt.plot(
                x_plt_axis_f,
                data["f"][stages[ns]]["frequency_shift"],
                "DisplayName",
                stages[ns],
            )

    plt.ylabel("Difference from excitation tune")
    plt.xlim([x_plt_axis_f(1), x_plt_axis_f[-1]])
    plt.xlabel(labelX_f)


def mbf_growdamp_setup(input_settings, pv_names):
    # Sets up the MBF system to be ready for a growdamp measurement['']
    #
    #   Args:
    #       input_settings(struct): contains all the setup information['']
    #       pv_names(struct): contains the locations of all the machine parameters['']
    #
    # example: mbf_growdamp_setup(input_settings, pv_names, trigger_inputs)
    mbf_tools()
    pll_setup = {}
    mbf_axis = input_settings["mbf_axis"]
    harmonic_number = input_settings["harmonic_number"]
    states = input_settings["states"]
    excitation_tune = input_settings["excitation_tune"]
    bunch_monitor = input_settings["bunches_monitored"]
    pll_setup["pll_tracking"] = input_settings["pll_tracking"]
    pll_setup["pll_bunches"] = input_settings["pll_bunches"]
    pll_setup["pll_guard_bunches"] = input_settings["pll_guard_bunches"]
    pv_head = pv_names["hardware_names"][mbf_axis]
    pv_head_mem = pv_names["hardware_names"]["mem"][mbf_axis]
    trigger_inputs = pv_names["trigger_inputs"]
    triggers = pv_names["tails"]["triggers"]
    memory = pv_names["tails"]["MEM"]
    Sequencer = pv_names["tails"]["Sequencer"]
    Detector = pv_names["tails"]["Detector"]
    Bunch_bank = pv_names["tails"]["Bunch_bank"]
    NCO2 = pv_names["tails"]["NCO2"]
    ## Set up triggering
    # set up the appropriate triggering
    # Stop triggering first, otherwise there's a good chance the first thing
    # we'll do is loose the beam as we change things['']
    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(f"{pv_head}{triggers[trigger]['enable_status']}", "Ignore")

    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        set_variable(f"{pv_head}{triggers['MEM'][trigger]['enable_status']}", "Ignore")
        set_variable(f"{pv_head}{triggers['MEM'][trigger]['blanking_status']}", "All")

    # Set the trigger to one shot
    set_variable(f"{pv_head}{triggers['SEQ']['mode']}", "One Shot")
    set_variable(f"{pv_head_mem}{triggers['MEM']['mode']}", "One Shot")
    # Set the triggering to Soft only
    set_variable(f"{pv_head}{triggers['SOFT']['enable_status']}", "Enable")
    set_variable(f"{pv_head_mem}{triggers['MEM']['SOFT']['enable_status']}", "Enable")
    #  set up the memory buffer to capture ADC data.
    set_variable(f"{pv_head_mem}{memory['channel_select']}", "ADC0/ADC1")
    # Delay to make sure the currently set up sweeps have finished.
    time.sleep(1)  # TODO look for system to be in bank 0.
    ## Set up banks
    # bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #               7=sweep+NCO+FIR)
    # bunch bank 2 (the feedback)
    mbf_set_bank(mbf_axis, 2, 1)  # FIR
    # bunch bank 1 (the excitation)
    mbf_set_bank(mbf_axis, 1, 4)  # Sweep
    # bunch bank 0 (the resting condition)
    mbf_set_bank(mbf_axis, 0, 1)  # FIR
    ## Set up states
    # (ax, state, tune, bank, gain, enable, duration, dwell, capture)
    for st in range(1, len(states)):
        mbf_set_state(mbf_axis, st, excitation_tune, states[st])

    # start state
    set_variable(f"{pv_head}{Sequencer['start_state']}", len(states))
    # steady state bank
    set_variable(f"{pv_head}{Sequencer['steady_state_bank']}", "Bank 0")
    ## set the super sequencer to scan all modes.
    set_variable(
        f"{pv_head}{pv_names['tails']['Super_sequencer_count']}", harmonic_number
    )
    ## set up PLL
    if pll_setup["pll_tracking"] == "yes":
        mbf_fll_setup("x", pll_setup["pll_bunches"], pll_setup["pll_guard_bunches"])
        set_variable(f"{pv_head}{NCO2['PLL_follow']}", "Follow")
        set_variable(f"{pv_head}{NCO2['gaindb']}", -30)
        fillx = get_variable(f"{pv_head}{Bunch_bank['bank1']['SEQ_enablewf']}")
        set_variable(f"{pv_head}{Bunch_bank['bank0']['NCO2_enablewf']}", fillx)
        set_variable(f"{pv_head}{Bunch_bank['bank1']['NCO2_enablewf']}", fillx)
        set_variable(f"{pv_head}{NCO2['enable']}", "On")

    ## Set up the detector.
    # Set the detector input to FIR
    set_variable(f"{pv_head}{Detector['source']}", "FIR")
    # Enable only detector 0
    for n_det in range(3):
        l_det = ["det", (n_det)]
        set_variable(f"{pv_head}{Detector[l_det]['enable']}", "Disabled")

    set_variable(f"{pv_head}{Detector['det0']['enable']}", "Enabled")
    # Set which bunches detector 0 records.
    set_variable(f"{pv_head}{Detector['det0']['bunch_selection']}", bunch_monitor)


def mbf_growthrates_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    overrides=(None, None),
    advanced_fitting=0,
    debug=0,
):
    # Takes the data extracted by mbf_growthrates_archival_retreval and operates
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
    #         dr_growth (numeric matrix): Growth rate.
    #                                      (bunches vs datasets)
    #         dr_active (numeric matrix): Passive damping rate.
    #                                      (bunches vs datasets)
    #         error_growth (numeric matrix): Error of the fit for the growth rate.
    #         error_active (numeric matrix): Error of the fit for the active
    #                                        damping rate.
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_growth, dr_active, error_growth, error_active, times,
    #          experimental_setup, extents] = mbf_growthrates_archival_analysis(
    #                                                      data_requested, 'average')

    times = []
    param = []
    dr_growth = np.array(ndmin=2)
    dr_active = np.array(ndmin=2)
    error_growth = np.array(ndmin=2)
    error_active = np.array(ndmin=2)
    experimental_setup = {}
    for nd in range(len(data_requested)):
        [s_poly_data, _1] = mbf_growthrates_analysis(
            data_requested[nd],
            override=overrides,
            advanced_fitting=advanced_fitting,
            debug=debug,
        )
        times[nd] = datetime(data_requested[nd]["time"])
        dr_growth[nd, :] = np.fft.fftshift(s_poly_data[:, 1, 1])
        dr_active[nd, :] = np.fft.fftshift(-s_poly_data[:, 2, 1])
        error_growth[nd, :] = -s_poly_data[:, 1, 3]
        error_active[nd, :] = -s_poly_data[:, 2, 3]
        if "I_dcct5" in data_requested[nd]:
            data_requested[nd]["current"] = data_requested[nd]["I_dcct5"]

        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        if not dr_growth:
            print("No data left[] Try changing analysis settings[]")
            return
        else:
            [dr_growth, experimental_setup["param"]] = (
                mbf_analysis_reorganise_for_parameter_sweep(
                    dr_growth, param, parameter_step
                )
            )
            [dr_active, _1] = mbf_analysis_reorganise_for_parameter_sweep(
                dr_active, param, parameter_step
            )
            [error_growth, _1] = mbf_analysis_reorganise_for_parameter_sweep(
                error_growth, param, parameter_step
            )
            [error_active, _1] = mbf_analysis_reorganise_for_parameter_sweep(
                error_active, param, parameter_step
            )

    elif analysis_type == "average":
        print(
            'Archive:Growthrates:setting Ignoring the last two parameters as "average" '
            "is set"
        )
        dr_growth = np.mean(dr_growth)
        dr_active = np.mean(dr_active)
        error_growth = np.mean(error_growth)  # is it OK to just average the errors?
        error_active = np.mean(error_active)

    return dr_growth, dr_active, error_growth, error_active, times, experimental_setup


def mbf_growthrates_archival_plotting(
    requested_data,
    dr_growth,
    dr_active,
    error_growth,
    error_active,
    times,
    experimental_setup,
):
    # Plots the data processed by mbf_growthrates_archival_analysis.
    # Args:
    #      dr_growth (numeric matrix): Growth rate.
    #                                   (bunches vs datasets)
    #      dr_active (numeric matrix): Passive damping rate.
    #                                   (bunches vs datasets)
    #      error_passive (numeric matrix): Error of the fit for the growth rate.
    #      error_active (numeric matrix): Error of the fit for the active
    #                                     damping rate.
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results of
    #                                    the fit errors.
    #
    # Example: mbf_growdamp_archival_plotting(dr_growth, dr_active, error_growth,
    # error_active, times, setup, selections, extents)
    # Only do something if there is data to do something with.
    if not times:
        return

    [_2, harmonic_number, _1] = mbf_system_config
    x_plt_axis = range(harmonic_number) - harmonic_number / 2
    this_year = datetime.datetime.now().year
    ranges_to_printlay = {"RF", "time", "current"}
    years_input = [
        this_year - 5,
        this_year - 4,
        this_year - 3,
        this_year - 2,
        this_year - 1,
        this_year,
    ]
    years_colours = ["r", "b", "k", "g", "c", "m"]
    graph_text = f"Analysis type: {experimental_setup['anal_type']}"
    graph_title = "Damping rates for different modes"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = "Damping rates for different modes as a def of "
        f"{experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(1, len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"](hw)

    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    mplt.annotation(
        "textbox",
        [0, 1, -0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, dr_growth, "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(dr_growth, years_input, years_colours, times, x_plt_axis)

    plt.plot([x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off")
    fig.suptitle(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Growth rates (1/turns)")
    ymin = min(min(dr_growth, [], 2))
    ymin = min(ymin, 0)

    ymax = max(max(dr_growth, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, dr_active, "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(dr_active, years_input, times, x_plt_axis)

    plt.plot([x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off")
    # fig.suptitle(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Active damping rates (1/turns)")
    ymin = min(min(dr_active, [], 2))
    ymin = min(ymin, 0)

    ymax = max(max(dr_active, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    ck = 1
    for hrd in range(len(ranges_to_printlay)):
        if ranges_to_printlay[hrd] == "time":
            continue
        else:
            plt.xlabel("Time")
            fig.suptitle(ranges_to_printlay[hrd])
            data_temp = []
            for hse in range(1, len(times)):
                data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

            plt.plot[times, data_temp, "o:"]
            plt.ylabel(ranges_to_printlay[hrd])
            ck = ck + 1

    for hkw in range(len(requested_data)):
        plt.plot(range(harmonic_number), requested_data[hkw]["fill_pattern"], "b")

    plt.ylim(bottom=0)
    plt.xlim((1, harmonic_number))
    fig.suptitle("Fill pattern variation")
    plt.ylabel("Charge (nC)")
    # add labels if it is a parameter sweep['']
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"])):
            labels[tb] = experimental_setup["param"][tb]

        plt.legend(labels)

    if experimental_setup["anal_type"] == "parameter_sweep":
        fig, _1 = plt.subplot_mosaic(
            [["upper left", "upper right"], ["lower left", "lower right"]],
            figsize=(5.5, 3.5),
            layout="constrained",
        )
        plt.plot(experimental_setup["param"], dr_growth)
        plt.xlabel(experimental_setup["sweep_parameter"])
        plt.ylabel("Growth rates (1/turns)")
        plt.plot(
            [experimental_setup["param"][0], experimental_setup["param"][-1]],
            [0, 0],
            "r:",
            "HandleVisibility",
            "off",
        )

        plt.plot(experimental_setup["param"], dr_active)
        plt.xlabel(experimental_setup["sweep_parameter"])
        plt.ylabel("Active damping rates (1/turns)")
        fig.suptitle(
            [
                "Damping rates vs ",
                experimental_setup["sweep_parameter"],
                " in the ",
                experimental_setup["axis"],
                " axis",
            ]
        )
        plt.plot(
            [experimental_setup["param"][0], experimental_setup["param"][-1]],
            [0, 0],
            "r:",
            "HandleVisibility",
            "off",
        )
        if experimental_setup["sweep_parameter"] == "current":
            x1 = range(300)
            for ks in range(len(dr_growth)):
                P = np.polyfit(experimental_setup["param"], dr_growth[:, ks], 1)
                P_start = [
                    index
                    for (index, item) in enumerate(x1)
                    if item < min(experimental_setup["param"])
                ]
                P_points = np.polyval(P, x1)
                # Find the first time after the lowest current that the extrapolation
                # goes negative.
                P_loc = [
                    index
                    for (index, item) in enumerate(np.sign(P_points[P_start:-1]))
                    if item == -1
                ]
                plt.plot(
                    x1,
                    P_points,
                    "DisplayName",
                    f"Mode {x_plt_axis[ks]}: {x1(P_loc)} mA",
                    "LineWidth",
                    2,
                )
                plt.plot(
                    experimental_setup["param"],
                    dr_growth[:, ks],
                    "ko",
                    "HandleVisibility",
                    "off",
                )

            plt.xlabel(experimental_setup["sweep_parameter"])
            plt.ylabel("Growth rates (1/turns)")
            fig.suptitle("Extrapolated data")
            plt.legend("Location", "eastoutside")
            plt.plot([x1[0], x1[-1]], [0, 0], "r:", "HandleVisibility", "off")
            for ks in range(len(dr_active)):
                P = np.polyfit(experimental_setup["param"], dr_active[:, ks], 1)
                P_start = [
                    index
                    for (index, item) in enumerate(x1)
                    if item < min(experimental_setup["param"])
                ]
                P_points = np.polyval(P, x1)
                P_loc = [
                    index
                    for (index, item) in enumerate(np.sign(P_points[P_start:-1]))
                    if item == -1
                ]
            plt.plot(
                x1,
                np.polyval(P, x1),
                "DisplayName",
                f"Mode {x_plt_axis[ks]}: {x1(P_loc)} mA",
                "LineWidth",
                2,
            )
            plt.plot(
                experimental_setup["param"],
                dr_active[:, ks],
                "ko",
                "HandleVisibility",
                "off",
            )

            plt.xlabel(experimental_setup["sweep_parameter"])
            plt.ylabel("Active damping rates (1/turns)")
            fig.suptitle("Extrapolated data")
            plt.legend("Location", "eastoutside")
            plt.plot([x1[0], x1[-1]], [0, 0], "r:", "HandleVisibility", "off")

    # FIXME
    # if nargin == 9:
    #     figure
    #     ax3 = subplt.plot(2,1,1)
    #     populate_graph(error_growth, years_input, times, x_plt_axis)
    #     fig.suptitle('Growth rate errors')
    #     plt.xlabel('Mode')
    #     plt.ylabel('Growth rate errors')
    #     ax4 = subplt.plot(2,1,2)
    #     populate_graph(error_active, years_input, times, x_plt_axis)
    #     fig.suptitle('Active damping rate errors')
    #     plt.xlabel('Mode')
    #     plt.ylabel('Active damping rate errors')
    #     linkaxes([ax3,ax4],'x')


def mbf_growthrates_archival_retrieval(
    ax,
    date_range,
    bypass_index="no",
    metadata_only="no",
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
    overrides=(None, None),
    advanced_fitting=0,
    current_range=(2, 150),
    debug=0,
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
    #       analysis_type(str): determines the type of analysis to run 'collate' or
    #                           'sweep', the default is 'collate'.
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
    # Example: mbf_growdamp_archival_retrieval('x',
    #         [datetime(2023, 1, 1), datetime("now")])
    if ax.lower() == "x":
        filter_name = "Growthrates_x_axis"
    elif ax.lower() == "y":
        filter_name = "Growthrates_y_axis"
    elif ax.lower() == "s":
        filter_name = "Growthrates_s_axis"
    else:
        raise ValueError(
            "MBF:Archive:InputError mbf_archival_dataset_retrieval: "
            "No valid axis given (should be x, y or s)"
        )

    requested_data = mbf_archival_dataset_retrieval(
        filter_name, date_range, bypass_index=bypass_index, metadata_only=metadata_only
    )
    # Only keeping datasets that satify the requested machine conditions['']
    conditioned_data = mbf_archival_conditional_filtering(
        requested_data, current_range=current_range
    )
    if not conditioned_data:
        print("No data meeting the requirements")
    else:
        if analysis_type == "collate":
            [dr_growth, dr_active, error_growth, error_active, times, setup] = (
                mbf_growthrates_archival_analysis(
                    conditioned_data,
                    analysis_type="collate",
                    overrides=overrides,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            )
        elif analysis_type == "sweep":
            [dr_growth, dr_active, error_growth, error_active, times, setup] = (
                mbf_growthrates_archival_analysis(
                    conditioned_data,
                    analysis_type="parameter_sweep",
                    sweep_parameter=sweep_parameter,
                    parameter_step=parameter_step,
                    overrides=overrides,
                    advanced_fitting=advanced_fitting,
                    debug=debug,
                )
            )
        else:
            raise ValueError(
                "MBF:Archive:InputError Please select collate or sweep "
                "as the analysis type"
            )

        setup["axis"] = ax
        mbf_growthrates_archival_plotting(
            conditioned_data,
            dr_growth,
            dr_active,
            error_growth,
            error_active,
            times,
            setup,
        )
        return conditioned_data


def mbf_set_bank(ax, bank, out_type):
    # Setup an individual bank in an individual MBF system['']
    #
    #
    # Args:
    #       ax (str)          : 'x', 'y', or 's' axis
    #       bank (int)        : The bunch bank number['']
    #       out_type (int)    : Determines which combination of filters and
    #                           excitation is required (0=off 1=FIR 2=NCO
    #                           3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #                           7=sweep+NCO+FIR)
    #
    # Example:  mbf_set_bank(ax, bank, out_type)
    [_1, harmonic_number, pv_names] = mbf_system_config
    BB = pv_names["tails"]["Bunch_bank"][f"bank{bank}"]
    pv_head = [pv_names["hardware_names"][ax]]
    # bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO
    #               7=sweep+NCO+FIR)
    if out_type == 0:
        # all off
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 1:
        # FIR only
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 2:
        # NCO only
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 3:
        # NCO + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 4:
        # sweep only
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 5:
        # sweep + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO1']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 6:
        # sweep + NCO
        set_variable(f"{pv_head}{BB['FIR']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['SEQ']['set_disable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)
    elif out_type == 7:
        # sweep + NCO + FIR
        set_variable(f"{pv_head}{BB['FIR']['gainwf']}", np.ones(1, harmonic_number) * 1)
        set_variable(f"{pv_head}{BB['FIR']['set_enable']}", 1)
        set_variable(
            f"{pv_head}{BB['NCO1']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['NCO1']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['NCO2']['set_disable']}", 1)
        set_variable(
            f"{pv_head}{BB['SEQ']['gainswf']}", np.ones(1, harmonic_number) * 1
        )
        set_variable(f"{pv_head}{BB['SEQ']['set_enable']}", 1)
        set_variable(f"{pv_head}{BB['PLL']['set_disable']}", 1)

    # select which FIR filter to use
    set_variable(f"{pv_head}{BB['FIR']['selectwf']}", np.ones(1, harmonic_number) * 0)


def mbf_set_state(ax, state, tune, setup_data):
    # Setup an individual state in the super sequencer['']
    #
    # Args:
    #       ax (str)      : 'x', 'y', or 's' axis
    #       state (int)   : state number in the sequencer['']
    #       tune (float)  : Tune of the machine['']
    #       setup_data (struct): containing
    #           bank (int)    : The bunch bank used for this state['']
    #           gain (str)    : the excitation level['']
    #           duration (int): the number of turns the state is active['']
    #           dwell (int)   : Dwell time (turns)['']
    #           capture (str) : 'Capture' or 'Discard' depending onn if you want to
    #                            keep the data or not
    #
    # Example: mbf_set_state(ax, state, tune, setup_data)
    [_2, _1, pv_names] = mbf_system_config()
    system_axis = pv_names["hardware_names"][ax]
    seq = pv_names["tails"]["Sequencer"][f"seq{state}"]
    set_variable(f"{system_axis}{seq['start_frequency']}", tune)
    set_variable(f"{system_axis}{['step_frequency']}", 0)
    set_variable(f"{system_axis}{['turns']}", setup_data["duration"])
    set_variable(f"{system_axis}{['holdoff']}", 0)
    set_variable(f"{system_axis}{['dwell']}", setup_data["dwell"])
    set_variable(f"{system_axis}{['bank_select']}", ["Bank ", (setup_data["bank"])])
    set_variable(f"{system_axis}{['capture_state']}", setup_data["capture"])
    set_variable(f"{system_axis}{['windowing_state']}", "Disabled")
    set_variable(f"{system_axis}{['gain']}", setup_data["excitation_level"])
    set_variable(f"{system_axis}{['blanking_state']}", "Off")
    set_variable(f"{system_axis}{['enable']}", setup_data["excitation"])


def reestablish_tune_measurement(mbf_axis):
    # sets up the tune measurement by setting bank1 and sequencer state one as
    # required['']
    #   Args:
    #       mbf_axis(str): 'x','y', or 's'
    # Example: reestablish_tune_measurement('x')
    [_1, harmonic_number, pv_names] = mbf_system_config
    if mbf_axis.lower() == "x":
        sweep_start = 80.139
        sweep_end = 80.239
        tune_gain = -54
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["x"]
    elif mbf_axis.lower() == "y":
        sweep_start = 80.227
        sweep_end = 80.327
        tune_gain = -54
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["y"]
    elif mbf_axis.lower() == "s":
        sweep_start = 80.00320
        sweep_end = 80.00520
        tune_gain = -18
        tune_dwell = 100
        tune_count = 4096
        base = pv_names["hardware_names"]["s"]
    else:
        raise ValueError("MBF:InputError Please set required axis to x, y, or s")

    # setting up sequencer state 1 to be the tune sweep['']
    set_variable(f"{base}{pv_names['tails']['Super_sequencer']['count']}", 1)
    set_variable(f"{base}{pv_names['tails']['Sequencer']['start_state']}", 1)
    tune_sequencer = pv_names["tails"]["Sequencer"]["seq1"]
    set_variable(f"{base}{tune_sequencer['start_frequency']}", sweep_start)
    set_variable(f"{base}{tune_sequencer['end_frequency']}", sweep_end)
    set_variable(f"{base}{tune_sequencer['gaindb']}", tune_gain)
    set_variable(f"{base}{tune_sequencer['turns']}", tune_count)
    set_variable(f"{base}{tune_sequencer['dwell']}", tune_dwell)
    set_variable(f"{base}{tune_sequencer['bank_select']}", {"Bank 1"})
    set_variable(f"{base}{tune_sequencer['tune_pll_following']}", {"Ignore"})
    set_variable(f"{base}{tune_sequencer['enable']}", "On")
    set_variable(f"{base}{tune_sequencer['holdoff_state']}", 0)
    set_variable(f"{base}{tune_sequencer['holdoff']}", 0)
    set_variable(f"{base}{tune_sequencer['blanking_state']}", {"Blanking"})
    set_variable(f"{base}{tune_sequencer['windowing_state']}", {"Windowed"})
    set_variable(f"{base}{tune_sequencer['capture_state']}", {"Capture"})
    tune_bank = pv_names["tails"]["Bunch_bank"]["bank1"]
    # Setting bank 1 to use both the FIR and the sequencer but nothing else['']
    set_variable(f"{base}{tune_bank['FIR']['enablewf']}", np.ones(1, harmonic_number))
    set_variable(f"{base}{tune_bank['NCO1']['enablewf']}", np.zeros(1, harmonic_number))
    set_variable(f"{base}{tune_bank['NCO2']['enablewf']}", np.zeros(1, harmonic_number))
    set_variable(f"{base}{tune_bank['SEQ']['enablewf']}", np.ones(1, harmonic_number))
    set_variable(
        f"{base}{pv_names['tails']['Bunch_bank']['bank1']['PLL']['enablewf']}",
        np.zeros(1, harmonic_number),
    )
    # triggering
    set_variable(f"{base}{pv_names['tails']['triggers']['mode']}", "Rearm")
    set_variable(
        f"{base}{pv_names['tails']['triggers']['EXT']['enable_status']}", "Enable"
    )
    set_variable(f"{base}{pv_names['tails']['triggers']['SEQ']['arm']}", 1)


def truncate_to_linear(x_data_in, y_data_in, n_tests=100):

    # take the log of the data as we expect an exponential decay. meaning that the
    # log(data) should be linear
    mm = np.log(abs(y_data_in))
    truncation_point_end = find_end_trunction_point(mm, n_tests)
    if truncation_point_end < 10:  # if too close to start
        y_data_out = y_data_in
        x_data_out = x_data_in
        return

    truncation_point_start = find_start_trunction_point(
        mm[1:truncation_point_end], n_tests
    )
    if truncation_point_start > truncation_point_end - 10:  # if too close to end.
        y_data_out = y_data_in[1:truncation_point_end]
        x_data_out = x_data_in[1:truncation_point_end]
        return

    truncation_point_end = find_end_trunction_point(
        mm[truncation_point_start:-1], n_tests
    )
    if truncation_point_end < truncation_point_start + 10:  # iff too close together.
        y_data_out = y_data_in
        x_data_out = x_data_in
        return

    y_data_out = y_data_in[
        truncation_point_start : truncation_point_end + truncation_point_start - 1
    ]
    x_data_out = x_data_in[
        truncation_point_start : truncation_point_end + truncation_point_start - 1
    ]

    return x_data_out, y_data_out


def find_end_trunction_point(mm, n_tests):
    # Truncate the end by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit['']
    ind = []
    overall_error = []
    for gra in range(n_tests):
        ind[gra] = np.floor(len(mm)[""] * gra / n_tests)
        y = mm[range(ind[gra])]
        x = range(len(y))
        [p, S] = np.polyfit(x, y, 1)
        [_1, delta] = np.polyval(p, x, S)
        #     The 1/ind is to make the errors at the begining of the decay count for
        #     more than the ones at the end['']
        overall_error[gra] = np.mean(abs(delta) * 1 / ind[gra])
        if ind[gra] < 100:
            ind = ind[gra:-1]
            overall_error = overall_error[gra:-1]
            break

    # figure(2)
    # plt.plot(ind, overall_error)
    # fig.suptitle('End truncation')
    [_1, x_of_min] = min(overall_error)
    truncation_point_end = ind(x_of_min)

    return truncation_point_end


def find_start_trunction_point(mm, n_tests):
    # Truncate the begining by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit[''] This is to deal with odd effects
    # which sometimes happen at the beginning (due to delays in the sysytem?)
    ind = []
    overall_error = []
    for gra in range(1, n_tests):
        ind[gra] = []
        if ind[gra] >= len(mm) - 5:
            break

        y = mm[ind[gra] : -1]
        x = range(len(y))
        [p, S] = np.polyfit(x, y, 1)
        [_1, delta] = np.polyval(p, x, S)
        overall_error[gra] = np.mean(abs(delta) * ind[gra]) / len(delta)

    # figure(3)
    # plt.plot(ind[1:-1-1], overall_error)
    # fig.suptitle('Start truncation')
    [_1, x_of_min] = np.min(overall_error)
    truncation_point_start = ind[x_of_min]

    return truncation_point_start


def unpack_old_growdamp_sweeps(requested_data):
    ck = 1
    unpacked_data = []
    for sh in range(1, len(requested_data)):
        if not iscell(requested_data[sh]["data"]):
            unpacked_data[ck] = requested_data[sh]
            ck = ck + 1
        else:
            for naw in range(1, len(requested_data[sh]["data"])):
                unpacked_data[ck] = requested_data[sh]
                unpacked_data[ck] = rmfield(unpacked_data[ck], "data")
                unpacked_data[ck]["data"] = requested_data[sh]["data"][naw]
                unpacked_data[ck] = rmfield(unpacked_data[ck], "data_freq")
                unpacked_data[ck]["data_freq"] = requested_data[sh]["data_freq"][naw]
                if "tune" in unpacked_data and iscell(unpacked_data["tune"]):
                    unpacked_data[ck] = rmfield(unpacked_data[ck], "tune")
                    unpacked_data[ck]["tune"] = requested_data[sh]["tune"][naw]
                ck = ck + 1
    unpacked_data = unpacked_data[1 : ck - 1]
