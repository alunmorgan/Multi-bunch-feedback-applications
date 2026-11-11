import datetime
import re
import time

import numpy as np

from Common import (
    get_variable,
    movmean,
    set_variable,
    system_config,
)


def growdamp_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    active_override: int | None = None,
    passive_override: int | None = None,
    advanced_fitting: bool = 0,
    error_threshold: float = 0.1,
    debug: bool = 0,
) -> dict:
    """Takes the data extracted by growdamp_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.
          active override: The number of turns to analyse.
          passive override: The number of turns to analyse.
          advanced_fitting: use the standard routine or more advanced/experimental
                            0=standard

    Returns:
            dataset containing
                dr_passive: Passive damping time. (bunches vs datasets)
                dr_active: Passive damping time.  (bunches vs datasets)
                error_passive: Error of the fit for the passive damping rate.
                error_active: Error of the fit for the active damping rate.
                times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = growdamp_archival_analysis(data_requested)
    """
    analysis_variables = {}
    analysis_variables["active_override"] = active_override
    analysis_variables["passive_override"] = passive_override
    analysis_variables["advanced_fitting"] = advanced_fitting

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=analysis_variables,
        analysis_function=growdamp_analysis,
        debug=debug,
    )


def growthrates_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    passive_override: int | None = None,
    active_overide: int | None = None,
    advanced_fitting: bool = 0,
    debug: bool = 0,
) -> tuple[list[dict], dict]:
    """Takes the data extracted by mbf_growthrates_archival_retreval and operates
    across all datasets. Then plots the results.

       Args:
        Standard inputs described in the archival_analysis function.
          active override: The number of turns to analyse.
          passive override: The number of turns to analyse.
          advanced_fitting: use the standard routine or more advanced/experimental
                            0=standard

    Returns:
            dataset containing
                dr_passive: Passive damping time. (bunches vs datasets)
                dr_active: Passive damping time.  (bunches vs datasets)
                error_passive: Error of the fit for the passive damping rate.
                error_active: Error of the fit for the active damping rate.
                times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = growthrates_archival_analysis(data_requested)
    """
    analysis_variables = {}
    analysis_variables["passive_override"] = passive_override
    analysis_variables["active_overide"] = active_overide
    analysis_variables["advanced_fitting"] = advanced_fitting

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=analysis_variables,
        analysis_function=growthrates_analysis,
        debug=debug,
    )

    return data, experimental_setup


def modescan_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
) -> tuple[np.array, np.array, list[float], dict]:
    """Takes the data extracted by modescan_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dataset containing
                data_magnitude
                data_phase
                times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = growdamp_archival_analysis(data_requested)
    """
    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=modescan_analysis,
        debug=debug,
    )

    return data, experimental_setup


def spectra_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
) -> tuple[dict, list[float], dict]:
    """Takes the data extracted by spectra_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dataset containing:
                data_magnitude
                data_phase
                times: Datetimes of the sets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = spectra_archival_analysis(data_requested)
    """
    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=mbf_spectrum_analysis,
        debug=debug,
    )

    return data, experimental_setup


def bunch_motion_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
) -> tuple[dict, list[float], dict]:
    """Takes the data extracted by bunch motion_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dataset containing:
                data_magnitude
                data_phase
                times: Datetimes of the sets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = bunch_motion_archival_analysis(data_requested)
    """
    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=mbf_bunch_motion_analysis,
        debug=debug,
    )

    return data, experimental_setup


def frontend_clock_phase_scan_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
):
    """Takes the data extracted by frontend_clock_phase_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dictionary contining:
              leading
              excited
              following
              times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = frontend_clock_phase_scan_archival_analysis(
                                                        data_requested)
    """

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=frontend_clock_phase_scan_analysis,
        debug=debug,
    )

    return data, experimental_setup


def frontend_gain_scan_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
) -> tuple[dict, list[float], dict]:
    """Takes the data extracted by frontend_gain_scan_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dictionary containing:
                adc_mean
                adc_max
                adc_min
                times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example:data, experimental_setup = frontend_gain_scan_archival_analysis(
                                                                    data_requested)
    """

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=frontend_gain_scan_analysis,
        debug=debug,
    )

    return data, experimental_setup


def frontend_system_phase_scan_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    debug: bool = 0,
) -> tuple[dict, list[float], dict]:
    """Takes the data extracted by frontend_system_phase_scan_archival_retreval
    and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.

    Returns:
            dataset containing:
                leading
                excited
                following
                times: Datetimes of the datasets.
            experimental_setup: The setup parameters for the analysis.

    Example: data, experimental_setup = frontend_system_phase_scan_archival_analysis(
                                                      data_requested)
    """

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=None,
        analysis_function=frontend_system_phase_scan_analysis,
        debug=debug,
    )

    return data, experimental_setup


def tunescan_over_modes_archival_analysis(
    data_requested: dict,
    analysis_type: str = "collate",
    sweep_parameter: str = "current",
    parameter_step: float = 0.1,
    active_override: int | None = None,
    passive_override: int | None = None,
    advanced_fitting: bool = 0,
    error_threshold: float = 0.1,
    debug: bool = 0,
) -> tuple[dict, list[float], dict]:
    """Takes the data extracted by tunescan_over_modes_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
        Standard inputs described in the archival_analysis function.
          active override: The number of turns to analyse.
          passive override: The number of turns to analyse.
          advanced_fitting: use the standard routine or more advanced/experimental
                            0=standard
          error_threshold:

    Returns:
            dataset containing
                dr_passive: Passive damping time. (bunches vs datasets)
                dr_active: Passive damping time.  (bunches vs datasets)
                error_passive: Error of the fit for the passive damping rate.
                error_active: Error of the fit for the active damping rate.
                times: Datetimes of the datasets.
            experimental_setup (structure): The setup parameters for the analysis.

    Example: data,experimental_setup = tunescan_over_modes_archival_analysis(
                   data_requested)
    """
    analysis_variables = {}
    analysis_variables["active_override"] = active_override
    analysis_variables["passive_override"] = passive_override
    analysis_variables["advanced_fitting"] = advanced_fitting
    analysis_variables["error_threshold"] = error_threshold

    data, experimental_setup = archival_analysis(
        data_requested=data_requested,
        analysis_type=analysis_type,
        sweep_parameter=sweep_parameter,
        parameter_step=parameter_step,
        additional_variables=analysis_variables,
        analysis_function=tunescan_over_modes_analysis,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis(
    data_requested: dict,
    analysis_type: str,
    sweep_parameter: str,
    parameter_step: float,
    additional_variables: dict | None,
    analysis_function,
    debug: bool,
) -> tuple[dict, dict]:
    """Takes the data extracted by mbf_growdamp_archival_retreval and operates
    across all datasets. Then plots the results.

    Args:
          data_requested: Data to be analysed.
          analysis_type: To select the type of analysis
                          (collate, average, parameter_sweep)
          sweep_parameter: Parameter to be used. This name must exist
                                 in the data structure. (only needed if
                                 anal_type set to 'parameter sweep')
          parameter_step_size: Defines the spacing of the steps in
                                       the parameter sweep.
                                       Multiple data sets which are on the same
                                       step will be averaged. (only needed if
                                       anal_type set to 'parameter sweep')
          additional_variables: extra settings to pass to the analysis function.
          analysis_function: defines which function to use.
          debug: if 1 then outputs additional graphs.

    Returns:
            dataset containing results:
            experimental_setup (structure): The setup parameters for the analysis.

    Example: data, experimental_setup = archival_analysis(
                                                          data_requested, 'average')
    """
    data = []
    experimental_setup = {}
    experimental_setup["anal_type"] = analysis_type
    if analysis_type == "parameter_sweep":
        experimental_setup["sweep_parameter"] = sweep_parameter
        experimental_setup["parameter_step_size"] = parameter_step

    for nd in range(len(data_requested)):
        data[nd]: dict = analysis_function(
            data_requested[nd],
            analysis_variables=additional_variables,
            debug=debug,
        )

        data[nd]["time"] = datetime.datetime(data_requested[nd]["time"])
        if analysis_type == "parameter_sweep":
            experimental_setup["param_vals"][nd] = data_requested[nd][sweep_parameter]

        print(".")

    if analysis_type == "parameter_sweep":
        data_out, experimental_setup = reorganise_for_parameter_sweep(
            data, experimental_setup
        )
    elif analysis_type == "average":
        data_out = average_dict_list(data)
    else:
        data_out = data
    return data_out, experimental_setup


def average_dict_list(data: list[dict]) -> list[dict]:
    data_out = {}
    for name in data[0].keys():
        if type(data[0][name]) is dict:
            new_list = []
            for hw in range(len(data)):
                new_list.append(data[hw][name])
            data_out[name] = average_dict_list(new_list)
        else:
            temp = []
            for ha in range(len(data)):
                temp.append(data[ha][name])
            data_out[name] = np.mean(temp)
    return data_out


def truncate_to_linear(
    x_data_in: list, y_data_in: list, n_tests: int = 100
) -> tuple[list, list]:

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


def find_end_trunction_point(mm: list, n_tests: int) -> int:
    # Truncate the end by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit.
    ind = []
    overall_error = []
    for gra in range(n_tests):
        ind[gra] = np.floor(len(mm)[""] * gra / n_tests)
        y = mm[range(ind[gra])]
        x = range(len(y))
        [p, S] = np.polyfit(x, y, 1)
        [_1, delta] = np.polyval(p, x, S)
        #     The 1/ind is to make the errors at the begining of the decay count for
        #     more than the ones at the end.
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


def find_start_trunction_point(mm: list, n_tests: int) -> int:
    # Truncate the begining by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit. This is to deal with odd effects
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


def get_damping(
    x_data: list[float],
    y_data: list[float],
    override: int,
    length_averaging: int,
    adv_fitting: bool,
    threshold_value: float,
) -> tuple[list[float], float, list[float]]:
    """
    Args:
          data (vector of floats): The data.
          dwell(int): The dwell time set for this data.
          override (int): The number of turns to analyse (if NaN analyse everything)
          length_averaging(int): Determines the strength of the filtering out
                                 of high frequecies in the data.
          advanced_fitting (bool): switches between simple (0)
                                   and advanced fitting (1).
          threshold_value(float): The value considered to be the noise floor.

      Returns:
          s(vector of floats): coefficients of the polynomial fit of the
                               magnitude of data
          delta(float): deviation of the magnitude data to the
                        fit of the magnitude data.
          p(vector of floats): coefficients of the polynomial fit of the
                               phase of data
    """
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


def get_growth(turns: list, data: list) -> tuple[list[float], float, list[float]]:
    mag_fit = np.polyfit(turns, np.log(abs(data)), 1)
    c1 = np.polyval(mag_fit, turns)
    delta = np.mean(abs(c1 - np.log(abs(data))) / c1)
    temp = np.unwrap(np.angle(data)) / (2 * np.pi)
    phase_fit = np.polyfit(turns, temp, 1)
    return mag_fit, delta, phase_fit


def reorganise_for_parameter_sweep(
    dr: list[dict], experimental_setup: dict
) -> tuple[list[dict], dict]:
    """Takes a set of results and a vector of the corresponding
    parameter values (given by param_vals). Sorts them into order
    and averages those data sets which are closer that the parameter step,
    as defined by parameter_step_size

    example: out_dr, experimental_setup = reorganise_for_parameter_sweep(
                                                        dr, experimental_setup)
    """
    param_vals = experimental_setup["param_vals"]
    parameter_step_size = experimental_setup["parameter_step_size"]

    # ensure the ordering
    sorting_index = np.argsort(param_vals)
    param_vals = param_vals[sorting_index]
    dr = dr[sorting_index]

    # Identify sections to average
    out_param = []
    out_dr = []
    for ns in range(param_vals[0], param_vals[-1], parameter_step_size):
        out_param.append(ns)
        acc = 0
        selection = []
        for index, item in enumerate(param_vals):
            if item >= ns and item < ns + parameter_step_size:
                selection[acc] = index
                acc += 1
        temp = average_dict_list(dr[selection])
        out_dr.append(temp[0])

    experimental_setup["param_vals"] = out_param
    return out_dr, experimental_setup


def growdamp_advanced_fitting(
    x_data: list[float],
    y_data: list[float],
    length_averaging: int,
    threshold_value: float,
) -> tuple[list[float, float, list[float]]]:
    """Fits to an exponential decay.

    Args:
          x_data (vector of floats): The turns.
          y_data (vector of floats): The data.
          length_averaging (int): number of points for the box car average to work
                                  with.
          threshold_value (float): The data value defined as the noise floor.

      Returns:
          s(vector of floats): coefficients of the polynomial fit of the
                               magnitude of data
          delta(float): deviation of the magnitude data to the
                        fit of the magnitude data.
          p(vector of floats): coefficients of the polynomial fit of the
                               phase of data
    """
    # Truncate data at the point the decay hits the noise floor.
    noise_floor_intercept_pd = [
        index for (index, item) in enumerate(abs(y_data)) if item <= threshold_value
    ]
    if noise_floor_intercept_pd:
        y_data[noise_floor_intercept_pd:-1] = []
        x_data[noise_floor_intercept_pd:-1] = []

    # Smooth the data
    if len(y_data) > length_averaging * 8:
        mm = movmean(y_data, length_averaging)

    # take the log of the data as we expect an exponential decay. meaning that the
    # log(data) should be linear
    mag = np.log(abs(mm))
    # Get an initial starting value.
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
    # compare linear fits to the data.
    vals = np.linspace(p_initial(1), p_initial(1) - 2e-7, n_tests)
    # sweep the gradient[''] Large changes in sample length indicate that a large
    # fraction of the line has moved from below the line to above it.
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

    _1, I = np.min(np.diff(sample_length))
    if I != 1:
        I = I - 1

    s = [vals(I), mag(dm_loc + 1)]
    c = np.polyval(s, x_data)
    delta = np.mean(abs(c - mag))
    temp = np.unwrap(np.angle(mm)) / (2 * np.pi)
    p = np.polyfit(x_data, temp, 1)
    return s, delta, p


def growdamp_analysis(
    exp_data: dict,
    active_override: int | None = None,
    passive_override: int | None = None,
    advanced_fitting: bool = 0,
    length_averaging: int = 20,
    debug: bool = 0,
    debug_modes: list[int] = range(harmonic_number),
    keep_debug_graphs: bool = 0,
) -> tuple[dict, int]:
    """takes the data from mbf growdamp capture and fits it with a series of
    linear fits to get the damping times for each mode.

      Args:
          exp_data (structure): Contains the systems setup and the data
                                captured.
          active_override (int|NaN): Sets the number of turns to analyse.
          passive_override (int|NaN): Sets the number of turns to analyse.
          advanced_fitting (bool): switches between simple (0)
                                   and advanced fitting (1).
          length_averaging(int): Determines the strength of the filtering out
                                 of high frequecies in the data.
          debug(int): if 1 then outputs graphs of individual modes to allow
                                       selection of appropriate overrides.
          debug_modes(list of ints): the modes to output the debug graphs for.
          keep_debug_graphs(bool): selects if the debug graphs are overwritten (0) or
                                   kept (1).

      Returns:
          output_data (struct): data is structured as [stage][mesurement]
                                  measurements are: damping time, offset,
                                  error relative to fit, frequency shift.
                                  all measurements are a vector the length of the
                                  number of modes.

    Example: output_data = tmbf_growdamp_analysis(exp_data)
    """
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


def mbf_growdamp_basic_fitting(
    x_data: list, y_data: list, length_averaging: int, threshold_value: float
) -> tuple[list[float, float, list[float]]]:
    # Fits to an exponential decay.
    #
    # Args:
    #       x_data (vector of floats): The turns.
    #       y_data (vector of floats): The data.all
    #       length_averaging (int): number of points for the box car average to work
    #                               with.
    #       threshold_value (float): The data value defined as the noise floor.
    #
    #   Returns:
    #       s(vector of floats): coefficients of the polynomial fit of the
    #                            magnitude of data
    #       delta(float): deviation of the magnitude data to the
    #                     fit of the magnitude data.
    #       p(vector of floats): coefficients of the polynomial fit of the
    #                            phase of data
    # Smooth the data
    if len(y_data) > length_averaging * 8:
        y_data = movmean(y_data, length_averaging)

    # Truncate data at the point the decay hits the noise floor.
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


def growthrates_analysis(data_requested: dict) -> dict:
    data = {}
    data["dr_growth"] = np.fft.fftshift(s_poly_data[:, 1, 1])
    data["dr_active"] = np.fft.fftshift(-s_poly_data[:, 2, 1])
    data["error_growth"] = -s_poly_data[:, 1, 3]
    data["error_active"] = -s_poly_data[:, 2, 3]
    return data


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


def modescan_analysis(modescan: dict) -> tuple[list[float], list[float]]:
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


def mbf_spectrum_analysis(input_data: dict) -> dict:
    # Analysis the raw time data from the mbf system in order to
    # generate a spectrogram of all bunches.
    #
    # Args:
    #       input_data (dict): Multiple sets of time data along with metatdata.
    #
    # Returns:
    #           data (structure): analysed data.
    #
    # Example: data = mbf_spectrum_analysis(input_data)

    for k in range(input_data["repeat"]):
        # Individual bunch analysis.
        # turn into matrix bunches x turns
        xx = np.reshape(input_data["raw_data"][k], input_data["harmonic_number"], [])
        # subtract the average position per bunch
        xx = xx - np.repmat(np.mean(xx, 2), 1, input_data["n_turns"])
        motion_only = np.reshape(xx, 1, [])  # stretch out again
        hanning_filter = np.hanning(len(motion_only))
        motion_only_windowed = motion_only * hanning_filter
        motion_only_windowed_padded = np.pad(
            motion_only_windowed,
            (0, 0),
            (
                0,
                (input_data["harmonic_number"] * input_data["n_turns"])
                - len(motion_only_windowed),
            ),
            constant_values=np.nan,
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

    # Forcing results to use 3 dimensions to allow accumulation and averaging over
    # experiments.
    fnames = data[0].keys()
    spec_data_temp = {}
    for sbd in range(len(fnames)):
        spec_data_temp[fnames[sbd]] = np.array(ndmin=3)
        for brs in range(1, len(data)):
            data_size = data[brs][fnames[sbd]].shape
            target_size = spec_data_temp[fnames[sbd]].shape
            spec_data_temp[fnames[sbd]] = np.pad(
                spec_data_temp[fnames[sbd]],
                (0, 0),
                (0, data_size[0] - target_size[1]),
                (0, data_size[1] - target_size[2]),
                constant_values=np.nan,
            )
            spec_data_temp[fnames[sbd]][
                brs, range(data_size[0]), range(data_size[1])
            ] = np.permute(data[brs][fnames[sbd]], [2, 0, 1])

    data = spec_data_temp

    return data


def mbf_bunch_motion_analysis(data: dict) -> dict:
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


def BBBFE_bunch_phase_variation_simulation(mbf_axis: str) -> dict:
    # This def moves the phase between -60 and +60 around the nominal phase.:
    # a gain ramp across the train is established using the FIR.
    # For each phase value various DAC outputs are captured.
    # The idea of this is to simulate the impact of a phase gradient across the
    # bunch train.
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


def frontend_clock_phase_scan_analysis(data_requested: dict) -> dict:
    data = {}
    data["leading"] = data_requested["side1"]
    data["excited"] = data_requested["main"]
    data["following"] = data_requested["side2"]
    return data


def frontend_gain_scan_analysis(data_requested):
    return data_requested


def frontend_system_phase_scan_analysis(data_requested):
    data = {}
    data["leading"] = data_requested["side1"][:, 1]
    data["excited"] = data_requested["main"][:, 1]
    data["following"] = data_requested["side2"][:, 1]
    return data


def tune_fit(tune_scale: list[float], tune_trace: list[float]):
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
