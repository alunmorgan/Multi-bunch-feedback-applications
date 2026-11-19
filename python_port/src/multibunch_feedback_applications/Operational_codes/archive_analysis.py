import datetime

import numpy as np
from analysis import (
    analysis_bunch_motion,
    analysis_frontend_clock_phase_scan,
    analysis_frontend_gain_scan,
    analysis_frontend_system_phase_scan,
    analysis_growdamp,
    analysis_growthrates,
    analysis_modescan,
    analysis_spectrum,
    analysis_tunescan_over_modes,
)


def archival_analysis_growdamp(
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
        analysis_function=analysis_growdamp,
        debug=debug,
    )


def archival_analysis_growthrates(
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
        analysis_function=analysis_growthrates,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_modescan(
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
        analysis_function=analysis_modescan,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_spectrum(
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
        analysis_function=analysis_spectrum,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_bunch_motion(
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
        analysis_function=analysis_bunch_motion,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_frontend_clock_phase_scan(
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
        analysis_function=analysis_frontend_clock_phase_scan,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_frontend_gain_scan(
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
        analysis_function=analysis_frontend_gain_scan,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_frontend_system_phase_scan(
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
        analysis_function=analysis_frontend_system_phase_scan,
        debug=debug,
    )

    return data, experimental_setup


def archival_analysis_tunescan_over_modes(
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
        analysis_function=analysis_tunescan_over_modes,
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
