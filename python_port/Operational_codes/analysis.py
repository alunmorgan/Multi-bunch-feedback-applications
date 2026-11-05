import datetime
import re
import time

import matplotlib.pyplot as plt
import numpy as np

from Common import (
    archival_plotting_setup,
    get_variable,
    mean_steps_data_in_stucture,
    movmean,
    set_variable,
    sort_data_in_stucture,
    system_config,
)


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


def growdamp_archival_analysis(
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
    # Example:[dr_passive, dr_active, error_passive, error_active, times, experimental_setup, extents] = growdamp_archival_analysis(data_requested, 'average')

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


def growthrates_archival_analysis(
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
    #          experimental_setup, extents] = growthrates_archival_analysis(
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


def mbf_modescan_analysis(modescan):
    # Analyses the captured modescan data.
    #     Args:
    #         modescan (structure): captured data
    #     Returns:
    #         data_magnitude (vector of floats): averaged signal magnitude over modes.
    #         data_phase (vector of floats): averaged signal phase over modes.
    #
    # Example [data_magnitude, data_phase] = mbf_modescan_analysis(modescan)
    n_repeats = len(modescan["magnitude"])
    data_magnitude_accumulator = np.empty((modescan["harmonic_number"], n_repeats))
    data_phase_accumulator = np.empty((modescan["harmonic_number"], n_repeats))
    for ks in range(n_repeats):
        data_magnitude_accumulator[:, ks] = abs(
            modescan["magnitude"][ks][1, 1 : modescan["harmonic_number"]]
        )
        data_phase_accumulator[:, ks] = modescan["phase"][ks][
            1, 1 : modescan["harmonic_number"]
        ]

    data_magnitude = sum(data_magnitude_accumulator, 2) / n_repeats
    data_phase = sum(data_phase_accumulator, 2) / n_repeats
    data_phase = np.unwrap(data_phase / 180 * np.pi) / np.pi * 180
    data_phase = data_phase - data_phase[1]
    return data_magnitude, data_phase


def modescan_archival_analysis(
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
    #         data_magnitude (numeric matrix):
    #         data_phase (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = growdamp_archival_analysis(
    #                                               data_requested, 'average')
    times = []
    param = []
    data_magnitude = []
    data_phase = []

    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        data_magnitude[nd], data_phase[nd] = mbf_modescan_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        [data_magnitude, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                data_magnitude, param, parameter_step
            )
        )
        [data_phase, experimental_setup["param"]] = (
            mbf_analysis_reorganise_for_parameter_sweep(
                data_phase, param, parameter_step
            )
        )
    elif analysis_type == "average":
        print(
            "Archive:Modescan:setting",
            'Ignoring the last two parameters as "average" is set',
        )
        data_magnitude = np.mean(data_magnitude, 0)
        data_phase = np.mean(data_phase, 0)


def spectra_archival_analysis(
    data_requested,
    analysis_type="collate",
    sweep_parameter="current",
    parameter_step=0.1,
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
    #
    # Returns:
    #         data_magnitude (numeric matrix):
    #         data_phase (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets['']
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis['']
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = growdamp_archival_analysis(
    #                                               data_requested, 'average')
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    # for fnd = len(data_requested):-1:1
    #     nturns_all(fnd) = data_requested[fnd]['n_turns']
    # end #for
    # max_turns = max(nturns_all)
    param = []
    times = []
    spec_data = []
    for nd in range(len(data_requested)):
        times[nd] = datetime(data_requested[nd]["time"])
        spec_data[nd] = mbf_spectrum_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        print(".")

    print("\n")
    # Forcing results to use 3 dimensions to allow accumulation and averaging over
    # experiments['']
    fnames = spec_data[0].keys()
    spec_data_temp = {}
    for sbd in range(len(fnames)):
        spec_data_temp[fnames[sbd]] = np.array(ndmin=3)
        for brs in range(1, len(data_requested)):
            data_size = spec_data[brs][fnames[sbd]].shape
            target_size = spec_data_temp[fnames[sbd]].shape
            spec_data_temp[fnames[sbd]] = padarray(
                spec_data_temp[fnames[sbd]],
                [0, data_size(1) - target_size(2), data_size(2) - target_size(3)],
                None,
                "post",
            )
            spec_data_temp[fnames[sbd]][
                brs, range(data_size[0]), range(data_size[1])
            ] = np.permute(spec_data[brs][fnames[sbd]], [3, 1, 2])

    spec_data = spec_data_temp
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        for sbd in range(1, len(fnames)):
            [spec_data[fnames[sbd]], experimental_setup["param"]] = (
                mbf_analysis_reorganise_for_parameter_sweep(
                    spec_data[fnames[sbd]], param, parameter_step
                )
            )

    elif analysis_type == "average":
        print(
            "Archive:Spectra:setting "
            "Ignoring the last two parameters as 'average' is set"
        )
        for sbd in range(len(fnames)):
            spec_data[fnames[sbd]] = np.mean((fnames[sbd]), 0)


def mbf_spectrum_analysis(input_data):
    # Analysis the raw time data from the mbf system in order to
    # generate a spectrogram of all bunches['']
    #
    # Args:
    #       raw_data (cell array): Multiple sets of time data['']
    #       turns_override(int): Forces the analysis to use a certain number of
    #                            turns in the analysis[''] This is useful for
    #                            comparing different datasets['']
    #                            Time domain data is eihter padded or trimmed
    #                            as needed['']
    # Returns:
    #           data (structure): analysed data['']
    #
    # Example: data = mbf_spectrum_analysis(raw_data, 1)
    if isstruct(input_data["raw_data"]):
        temp = input_data["raw_data"].keys()
        input_data["raw_data"] = input_data["raw_data"][temp[1]]

    # for k=1:raw_data['repeat']
    #     data_length=len(raw_data['raw_data'][k])
    for k in range(input_data["repeat"]):
        # Individual bunch analysis['']
        # turn into matrix bunches x turns
        xx = np.reshape(input_data["raw_data"][k], input_data["harmonic_number"], [])
        # subtract the average position per bunch
        xx = xx - np.repmat(np.mean(xx, 2), 1, input_data["n_turns"])
        motion_only = np.reshape(xx, 1, [])  # stretch out again
        hanning_filter = hanning(len(motion_only))
        motion_only_windowed = motion_only * hanning_filter
        motion_only_windowed_padded = padarray(
            motion_only_windowed,
            [
                0,
                (input_data["harmonic_number"] * input_data["n_turns"])
                - len(motion_only_windowed),
            ],
            0,
            "post",
        )
        motion_only_windowed_padded = np.reshape(
            motion_only_windowed_padded, input_data["harmonic_number"], []
        )
        # find the overall spectrum of the motion
        # with the static position offsets removed.
        xf1 = abs(np.fft(motion_only_windowed_padded, [], 2)) / input_data["n_turns"]
        if k == 1:
            bunch_motion = xx
            bunch_motion_spectrum = xf1
        else:
            bunch_motion_spectrum = bunch_motion_spectrum + xf1  # accumulating
            bunch_motion = bunch_motion + xx  # accumulating

    # Generating the frquency scales
    frev = input_data["RF"] / input_data["harmonic_number"]
    timescale = range(input_data["n_turns"]) / frev  # sec
    timestep = timescale[1] - timescale[0]
    bunch_motion_f_scale = (
        1
        / timestep
        * range(
            -(input_data["n_turns"] / 2) + 1,
            (input_data["n_turns"] / 2) / input_data["n_turns"],
        )
    )  # Hz
    data = {}
    data["bunch_motion"] = bunch_motion
    data["bunch_motion_timescale"] = timescale
    data["bunch_f_data"] = bunch_motion_spectrum
    data["bunch_f_bunches"] = sum(bunch_motion_spectrum ^ 2, 2)
    data["bunch_f"] = sum(bunch_motion_spectrum ^ 2, 1)
    data["bunch_f_scale"] = bunch_motion_f_scale
    data["bunch_tune_scale"] = bunch_motion_f_scale / (
        input_data["RF"] / input_data["harmonic_number"]
    )
    return data


def mbf_bunch_motion_analysis(data):
    x = np.reshape(data["x"], data["num_buckets"], [])
    y = np.reshape(data["y"], data["num_buckets"], [])
    z = np.reshape(data["z"], data["num_buckets"], [])
    turn_numbers = range(x.shape[1])
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(x[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(y[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(z[:, 1:100], 2), 1, len(turn_numbers))
    x = x - x_ref
    y = y - y_ref
    z = z - z_ref
    # Find the location of the largest disturbance['']
    [minx, minindx] = min(x[:])
    [maxx, maxindx] = max(x[:])
    [miny, minindy] = min(y[:])
    [maxy, maxindy] = max(y[:])
    [minz, minindz] = min(z[:])
    [maxz, maxindz] = max(z[:])
    _1, loc = max([abs(minx), maxx, abs(miny), maxy, abs(minz), maxz])
    indexes = [minindx, maxindx, minindy, maxindy, minindz, maxindz]
    index_of_peak = indexes(loc)
    [peak_row, peak_col] = ind2sub(x.shape, index_of_peak)
    output = {}
    output["turn_of_peak"] = peak_col
    output["bucket_of_peak"] = peak_row - 1
    output["mean_bunches_x"] = np.mean(x, 1)
    output["mean_bunches_y"] = np.mean(y, 1)
    output["mean_bunches_z"] = np.mean(z, 1)
    output["std_bunches_x"] = np.std(x, ddof=1, axes=1)
    output["std_bunches_y"] = np.std(y, ddof=1, axes=1)
    output["std_bunches_z"] = np.std(z, ddof=1, axes=1)
    output["mean_turns_x"] = np.mean(x, 0)
    output["mean_turns_y"] = np.mean(y, 0)
    output["mean_turns_z"] = np.mean(z, 0)
    output["std_turns_x"] = np.std(x, ddof=1, axes=0)
    output["std_turns_y"] = np.std(y, ddof=1, axes=0)
    output["std_turns_z"] = np.std(z, ddof=1, axes=0)
    output["x_norm"] = x
    output["y_norm"] = y
    output["z_norm"] = z
    return output


def bunch_motion_archival_analysis(
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
    #         data_magnitude (numeric matrix):
    #         data_phase (numeric matrix):
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = growdamp_archival_analysis(
    #                                                   data_requested, 'average')
    times = []
    param = []
    for nd in range(len(data_requested)):
        times[nd] = datetime.datetime(data_requested[nd]["time"])
        data = mbf_bunch_motion_analysis(data_requested[nd])
        if analysis_type == "parameter_sweep":
            param[nd] = data_requested[nd][sweep_parameter]

        states = data.keys()
        for st in range(len(states)):
            if nd == len(data_requested):
                temp_size = data[states[st]].shape
                dataset[states[st]] = []

            dataset[states[st]][nd, :, :] = data[states[st]]

        print(".")

    print("\n")
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        dataset, experimental_setup["param"] = (
            mbf_analysis_reorganise_for_parameter_sweep(dataset, param, parameter_step)
        )
    elif analysis_type == "average":
        print(
            "Archive:bunch_motion:setting"
            "Ignoring the last two parameters as 'average' is set"
        )
        states = dataset.keys()
        for st in range(len(states)):
            meass = dataset[states[st]].keys()
            for ms in range(len(meass)):
                dataset[states[st]][meass[ms]] = np.mean(
                    dataset[states[st]][meass[ms]], 0
                )


def BBBFE_bunch_phase_variation_simulation(mbf_axis):
    # This def moves the phase between -60 and +60 around the nominal phase['']:
    # a gain ramp across the train is established using the FIR['']
    # For each phase value various DAC outputs are captured['']
    # The idea of this is to simulate the impact of a phase gradient across the
    # bunch train['']
    [_1, harmonic_number, pv_names] = system_config
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


def frontend_clock_phase_scan_archival_analysis(
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
    #          experimental_setup, extents] = growdamp_archival_analysis(
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


def frontend_clock_phase_scan_archival_plotting(
    requested_data, leading, excited, following, times, experimental_setup
):
    # Plots the data processed by growdamp_archival_analysis.
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
    # Example: growdamp_archival_plotting(requested_data, data_magnitude,
    #                                data_phase, times, setup, selections, extents)

    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend clock phase scan"
    archival_plotting_setup(requested_data, times, experimental_setup)
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


def frontend_gain_scan_archival_analysis(
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
    #          experimental_setup, extents] = growdamp_archival_analysis(
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


def frontend_system_phase_scan_archival_analysis(
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
    #          experimental_setup, extents] = growdamp_archival_analysis(
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


def mbf_tunescan_over_modes_archival_analysis(
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
    #         dataset containing
    #         dr_passive (numeric matrix): Passive damping time.
    #                                      (bunches vs datasets)
    #         dr_active (numeric matrix): Passive damping time.
    #                                      (bunches vs datasets)
    #         error_passive (numeric matrix): Error of the fit for the passive
    #                                         damping rate.
    #         error_active (numeric matrix): Error of the fit for the active
    #                                        damping rate.
    #         times (numeric vector): Datetimes of the datasets.
    #         experimental_setup (structure): The setup parameters for the
    #                                         analysis.
    #
    # Example:[dr_passive, dr_active, error_passive, error_active, times,
    #          experimental_setup, extents] = mbf_tunescan_over_modes_archival_analysis(
    #                data_requested, 'average')

    # #condition the data in order to harmonise data changes made over time['']
    # for nd = len(data_requested):-1:1
    #     data_requested[nd] = growdamp_archive_data_conditioning(data_requested[nd])
    # end
    ck = 1
    times = []
    param = []
    for nd in range(1, len(data_requested)):
        if "I_dcct5" in data_requested[nd]:
            data_requested[nd]["current"] = data_requested[nd]["I_dcct5"]

        [data, data_state] = mbf_tunescan_over_modes_analysis(
            data_requested[nd],
            active_override=active_override,
            passive_override=passive_override,
            advanced_fitting=advanced_fitting,
            debug=debug,
        )
        if data_state == 0:
            continue

        times[ck] = datetime(data_requested[nd]["time"])
        if analysis_type == "parameter_sweep":
            param[ck] = data_requested[nd]["sweep_parameter"]

        states = data.keys()
        dataset = []
        for st in range(1, len(states)):
            meass = data[states[st]].keys()
            for ms in range(1, len(meass)):
                dataset[states[st]][meass[ms]][ck, :] = data[states[st]][meass[ms]]

        print(".")
        ck = ck + 1

    # # Removing datasets whose mean error is < error_threshold for the passive section.
    # error_av_p = np.mean(dataset['passive']['error'],2,'omitnan')
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
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step
        if not dataset["passive"]["damping_rate"]:
            print("No data left. Try changing analysis settings[]")
            return
        else:
            [dataset, experimental_setup["param"]] = (
                mbf_analysis_reorganise_for_parameter_sweep(
                    dataset, param, parameter_step
                )
            )

    elif analysis_type == "average":
        print(
            "Archive:Growdamp:setting"
            'Ignoring the last two parameters as "average" is set'
        )
        states = dataset.keys()
        for st in range(len(states)):
            meass = dataset[states[st]].keys()
            for ms in range(len(meass)):
                dataset[states[st]][meass[ms]] = np.mean(
                    dataset[states[st]][meass[ms]], 1, "omitnan"
                )


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
