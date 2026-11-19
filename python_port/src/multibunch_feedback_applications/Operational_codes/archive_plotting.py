import datetime

import matplotlib.pyplot as plt
import matplotlib.text as mplt
import numpy as np
from plotting import populate_graph

from Common import reconfigure_to_lists, system_config


def populate_archive_graph(input_data, years_input, times, x_plt_axis):
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

    year_list = times.year()
    if len(np.unique(year_list)) < 2:
        for ner in range(1, input_data.shape[0]):
            sample_time = times[ner].strftime("%a %d %b %Y, %I:%M%p")
            plt.plot(x_plt_axis, input_data[ner, :], "DisplayName", sample_time)

    else:
        for ner in range(1, input_data.shape[0]):
            years_ind = np.find(year_list(ner) == years)
            if states(years_ind) == 0:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "DisplayName",
                    (years[years_ind]),
                )
                states[years_ind] = 1
            else:
                plt.plot(
                    x_plt_axis,
                    input_data[ner, :],
                    cols[years_ind],
                    "HandleVisibility",
                    "off",
                )

    plt.xlim(min(x_plt_axis), max(x_plt_axis))
    plt.ylim(y_min, y_max)
    plt.legend("show")


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


def archival_plotting_growdamp(
    requested_data: list[dict],
    dataset: dict,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by growdamp_archival_analysis.
    # Args:
    #       dataset (struct): containing
    #      dr_passive (numeric matrix): Passive damping rate.
    #                                   (bunches vs datasets)
    #      dr_active (numeric matrix): Active damping rate.
    #                                   (bunches vs datasets)
    #      error_passive (numeric matrix): Error of the fit for the passive
    #                                      damping rate.
    #      error_active (numeric matrix): Error of the fit for the active
    #                                     damping rate.
    #      times (numeric vector): Datetimes of the datasets.
    #      experimental_setup (structure): The setup parameters for the
    #                                      analysis.
    #      plot_error_graphs (anything): if present the code will plot the results
    #                                    of the fit errors.
    #
    # Example: growdamp_archival_plotting(requested_data, dataset, error_active,
    #                                           times, setup, selections, extents)
    """
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

    archival_plotting_setup(requested_data, times, experimental_setup)
    [_2, harmonic_number, _1] = system_config
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


def archival_plotting_growthrates(
    requested_data: list[dict],
    dr_growth,
    dr_active,
    error_growth,
    error_active,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by growthrates_archival_analysis.
    Args:
         dr_growth (numeric matrix): Growth rate.
                                      (bunches vs datasets)
         dr_active (numeric matrix): Passive damping rate.
                                      (bunches vs datasets)
         error_passive (numeric matrix): Error of the fit for the growth rate.
         error_active (numeric matrix): Error of the fit for the active
                                        damping rate.
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results of
                                       the fit errors.

    Example: growdamp_archival_plotting(dr_growth, dr_active, error_growth,
    error_active, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with.
    if not times:
        return

    [_2, harmonic_number, _1] = system_config
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


def archival_plotting_modescan(
    requested_data: list[dict],
    data_magnitude,
    data_phase,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by modescan_archival_analysis.
    Args:
         data_magnitude (numeric matrix):
         data_phase (numeric matrix):
         times (numeric vector): Datetimes of the datasets['']
         experimental_setup (structure): The setup parameters for the
                                         analysis['']

    Example: growdamp_archival_plotting(requested_data, data_magnitude,
                                   data_phase, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with['']
    if not times:
        return

    graph_title = "Modescan"
    fig = archival_plotting_setup(requested_data, times, experimental_setup)
    harmonic_number = requested_data[1]["harmonic_number"]
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
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = f"Modescan as a def of {experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']} in the "
        f"{experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(1, len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    # FIXME

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, data_magnitude)
        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            data_magnitude, years_input, years_colours, times, x_plt_axis
        )

    fig.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Magnitude")
    ymin = min(min(data_magnitude, [], 2))
    ymin = min(ymin, 0)

    ymax = max(max(data_magnitude, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    plt.xlim([x_plt_axis[1], x_plt_axis[-1]])

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, data_phase)
        plt.legend(graph_labels)
    else:
        populate_archive_graph(data_phase, years_input, times, x_plt_axis)

    plt.plot(
        x_plt_axis,
        np.ones(len(x_plt_axis)) * 90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        x_plt_axis,
        np.ones(len(x_plt_axis)) * -90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    fig.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Phase")
    ymin = min([min(min(data_phase, [], 2)), -90])
    ymax = max([max(max(data_phase, [], 2)), 90])
    ymax = ymax + ymax / 10
    plt.ylim([ymin, ymax])
    plt.xlim([x_plt_axis[1], x_plt_axis[-1]])


def archival_plotting_spectrum(
    requested_data: list[dict], spec_data, times: list[float], experimental_setup: dict
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
         data_magnitude (numeric matrix):
         data_phase (numeric matrix):
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results of
                                       the fit errors.

    Example: growdamp_archival_plotting(requested_data, data_magnitude,
                                    data_phase, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Spectra"
    archival_plotting_setup(requested_data, times, experimental_setup)
    harmonic_number = requested_data[1]["harmonic_number"]
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
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = f"{experimental_setup['axis']} axis {graph_title} as a def of "
        f"{experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']}"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    if experimental_setup["anal_type"] == "parameter_sweep":
        scale_length = spec_data["bunch_tune_scale"].shape[1]
        for nfd in range(spec_data["bunch_tune_scale"].shape[0]):
            plot_data_tune = np.mean(spec_data["bunch_f_data"][nfd, :, :], 2)
            plt.plot(
                spec_data["bunch_tune_scale"][nfd, scale_length / 2 + 1 : -1],
                plot_data_tune[scale_length / 2 + 1 : -1],
            )

        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            spec_data["bunch_f"],
            years_input,
            years_colours,
            times,
            spec_data["bunch_tune_scale"][1, :, :],
        )

    plt.title(graph_title)
    plt.xlabel("Tune")
    plt.ylabel("Magnitude")

    if experimental_setup["anal_type"] == "parameter_sweep":
        for nfd in range(spec_data["bunch_f_scale"].shape[0]):
            plot_data_f = np.mean(spec_data["bunch_f_data"][nfd, :, :], 2)
            plt.plot(
                spec_data["bunch_f_scale"][nfd, scale_length / 2 + 1 : -1] * 1e-3,
                plot_data_f[scale_length / 2 + 1 : -1],
            )

        plt.legend(graph_labels)
    else:
        populate_archive_graph(
            spec_data["bunch_f"],
            years_input,
            times,
            spec_data["bunch_f_scale"][1, :, :],
        )

    plt.xlabel("Frequency (kHz)")
    plt.ylabel("Magnitude (Power)")

    bunches = spec_data["bunch_f_data"].shape[1]
    if experimental_setup["anal_type"] == "parameter_sweep":
        plot_data_2d = sum(spec_data["bunch_f_data"][:, :, :], 1)
        plt.imagesc(
            spec_data["bunch_f_scale"][1, scale_length / 2 + 1 : -1] * 1e-3,
            range(bunches),
            plot_data_2d[:, scale_length / 2 + 1 : -1],
        )  # TEMP FIXME
        plt.ylabel("Bunches")
        plt.xlabel("Frequency (kHz)")
    else:
        populate_archive_graph(
            spec_data["bunch_f_bunches"], years_input, times, x_plt_axis
        )
        plt.ylabel("Average position deviation from the mean")
        plt.xlabel("Bunch")

    plt.plt.figure("Position", [50, 50, 1400, 800])
    plt.title("Spectra of all measurements")
    plt.xlabel("Tune")
    for jw in range(spec_data["bunch_f_data"].shape[0]):
        plot_data = abs(spec_data["bunch_f_data"][jw, :, :])
        plt.imagesc(spec_data["bunch_tune_scale"][jw, :, :], x_plt_axis, plot_data)
        plt.colorbar
        plt.title(requested_data[jw]["time"].strftime("%a %d %b %Y, %I:%M%p"))


def archival_plotting_bunch_motion(
    requested_data: list[dict], dataset, times: list[float], experimental_setup: dict
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
          dataset (struct): containing
         dr_passive (numeric matrix): Passive damping rate.
                                      (bunches vs datasets)
         dr_active (numeric matrix): Passive damping rate.
                                      (bunches vs datasets)
         error_passive (numeric matrix): Error of the fit for the passive
                                         damping rate.
         error_active (numeric matrix): Error of the fit for the active
                                        damping rate.
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results of
                                       the fit errors.

    Example: growdamp_archival_plotting(dr_passive, dr_active, error_passive,
                                   error_active, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with['']
    if not times:
        return

    [_3, harmonic_number, _2, _1] = system_config
    this_year = datetime.datetime.now().year
    for jshe in range(1, len(requested_data)):
        requested_data[jshe]["turn_of_peak"] = dataset["turn_of_peak"](jshe)
        requested_data[jshe]["bucket_of_peak"] = dataset["bucket_of_peak"](jshe)

    ranges_to_printlay = {"RF", "current", "turn_of_peak", "bucket_of_peak"}
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
    graph_title = "Average bunch motion"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Average bunch motion as a def of {experimental_setup['sweep_parameter']}"
            f"Using a step size of {experimental_setup['parameter_step_size']}"
            f" in the {experimental_setup['axis']} axis"
        )
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

    plt.figure("Position", [50, 50, 1800, 800])
    plt.annotation(
        "textbox",
        [0, 1 - 0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    plt.axes("OuterPosition", [0.18, 0.66, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_x"], years_input, times, 1:harmonic_number]

    plt.title(graph_title)
    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in x")
    plt.axes("OuterPosition", [0.18, 0.33, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_y"], years_input, times, 1:harmonic_number]

    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in y")
    plt.axes("OuterPosition", [0.18, 0, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_bunches_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph[dataset["mean_bunches_z"], years_input, times, 1:harmonic_number]

    plt.xlabel("Bunches")
    plt.ylabel("Mean centroid motion in s")

    graph_title = "Average turn motion"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = (
            f"Average turn motion as a def of {experimental_setup['sweep_parameter']}"
        )
        f"Using a step size of {experimental_setup['parameter_step_size']} "
        f"in the {experimental_setup['axis']} axis"

    plt.axes("OuterPosition", [0.52, 0.66, 0.5, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_x"],
            years_input,
            times,
            range(len(dataset["mean_turns_x"])),
        )

    plt.title(graph_title)
    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in x")
    plt.legend("Location", "eastOutside")
    plt.axes("OuterPosition", [0.52, 0.33, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_y"],
            years_input,
            years_colours,
            times,
            range(len(dataset["mean_turns_y"])),
        )

    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in y")
    plt.axes("OuterPosition", [0.52, 0, 0.4, 0.3])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(experimental_setup["param"], dataset["mean_turns_x"], "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(
            dataset["mean_turns_z"],
            years_input,
            years_colours,
            times,
            range(len(dataset["mean_turns_z"])),
        )

    plt.xlabel("Turns")
    plt.ylabel("Mean centroid motion in s")

    ck = 0
    n_graphs = len(ranges_to_printlay)
    for hrd in range(1, n_graphs):
        plt.axes(
            "OuterPosition", [0.01, 0.3 + ck * 0.6 / n_graphs, 0.2, 0.6 / n_graphs]
        )
        plt.xlabel("Time")
        plt.title(ranges_to_printlay[hrd])
        data_temp = []
        for hse in range(1, len(times)):
            data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

        plt.plot(times, data_temp, "o:")
        plt.ylabel(ranges_to_printlay[hrd])

        ck = ck + 1

    axfp = plt.axes("OuterPosition", [0.01, 0, 0.2, 0.3])
    for hkw in range(len(requested_data)):
        plt.plot(range(harmonic_number), requested_data[hkw]["fill_pattern"], "b")

    plt.ylim(0)
    plt.xlim(1, harmonic_number)
    set(axfp, "XTick", [])
    plt.title("Fill pattern variation")
    plt.ylabel("Charge (nC)")
    # add labels if it is a parameter sweep['']
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"])):
            labels[tb] = experimental_setup["param"][tb]

        plt.legend(labels)


def archival_plotting_frontend_gain_scan(
    requested_data: list[dict],
    adc_mean,
    adc_max,
    adc_min,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
         adc_mean (numeric matrix):
         adc_max (numeric matrix):
         adc_min (numeric matrix):
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
    Example: frontend_gain_scan_archival_plotting(requested_data, data_magnitude,
                               data_phase, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend gain scan"
    archival_plotting_setup(requested_data, times, experimental_setup)
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


def archival_plotting_frontend_system_phase_scan(
    requested_data: list[dict],
    leading,
    excited,
    following,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
         leading (numeric matrix):
         excited (numeric matrix):
         following (numeric matrix):
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results of
                                       the fit errors.

    Example: growdamp_archival_plotting(requested_data, data_magnitude,
                                   data_phase, times, setup, selections, extents)
    """
    # Only do something if there is data to do something with.
    if not times:
        return

    graph_title = "Frontend system phase scan"
    fig = archival_plotting_setup(requested_data, times, experimental_setup)
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


def archival_plotting_tunescan_over_modes(
    requested_data, dataset, times, experimental_setup
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
          dataset (struct): containing
         dr_passive (numeric matrix): Passive damping rate.
                                      (bunches vs datasets)
         dr_active (numeric matrix): Active damping rate.
                                      (bunches vs datasets)
         error_passive (numeric matrix): Error of the fit for the passive
                                         damping rate.
         error_active (numeric matrix): Error of the fit for the active
                                        damping rate.
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results
                                       of the fit errors.

    Example: growdamp_archival_plotting(requested_data, dataset, error_active,
                                            times, setup, selections, extents)
    """
    # Only do something if there is data to do something with['']
    if not times:
        return

    [_3, harmonic_number, _2, _1] = system_config
    x_plt_axis = range(harmonic_number)
    # dataset =sort_data_in_stucture[dataset, [936:-1:469, 1:468], 2]
    dr_passive = dataset["passive"]["damping_rate"]
    dr_active = dataset["active"]["damping_rate"]
    error_passive = dataset["passive"]["error"]
    error_active = dataset["active"]["error"]
    ranges_to_printlay = {"RF", "time", "current"}
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
    graph_text = f"Analysis type: {experimental_setup['anal_type']}"
    graph_title = "Damping rates for different modes"
    plt.figure("Position", [50, 50, 1400, 800])
    plt.annotation(
        "textbox",
        [0, 1 - 0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    plt.axes("OuterPosition", [0.14, 0.67, 0.93, 0.32])
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_title = "Damping rates for different modes as a "
        f"def of {experimental_setup['sweep_parameter']}"
        f"Using a step size of {experimental_setup['parameter_step_size']}"
        f"in the {experimental_setup['axis']} axis"
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"][hw]

        plt.plot(x_plt_axis, dr_passive, "LineWidth", 2)
        plt.legend(graph_labels)
    else:
        populate_graph(dr_passive, years_input, years_colours, times, x_plt_axis)

    plt.plot([x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off")
    plt.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Passive damping rates (1/turns)")
    plt.legend("Location", "eastoutside")
    ymin = np.min(np.min(dr_passive, [], 2))
    if ymin > 0:
        ymin = 0

    ymax = np.max(np.max(dr_passive, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim(ymin, ymax)
    plt.xlim([np.min(x_plt_axis), np.max(x_plt_axis)])

    plt.axes("OuterPosition", [0.14, 0.34, 0.8, 0.32])
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, dr_active, "LineWidth", 2)
        #     plt.legend(graph_labels)
    else:
        populate_graph(dr_active, years_input, times, x_plt_axis)

    plt.legend("off")
    plt.plot([x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off")
    # plt.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("Active damping rates (1/turns)")
    ymin = np.min(np.min(dr_active, [], 2))
    if ymin > 0:
        ymin = 0

    ymax = np.max(np.max(dr_active, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim(ymin, ymax)
    plt.xlim(np.min(x_plt_axis), np.max(x_plt_axis))

    plt.axes("OuterPosition", [0.14, 0, 0.8, 0.32])
    effectiveness = dr_active - dr_passive
    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.plot(x_plt_axis, effectiveness, "LineWidth", 2)
        #     plt.legend(graph_labels)
    else:
        populate_graph(effectiveness, years_input, years_colours, times, x_plt_axis)

    plt.legend("off")
    plt.plot([x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off")
    # plt.title(graph_title)
    plt.xlabel("Mode")
    plt.ylabel("System effectiveness (1/turns)")
    ymin = np.min(np.min(effectiveness, [], 2))
    if ymin > 0:
        ymin = 0

    ymax = np.max(np.max(effectiveness, [], 2))
    ymax = ymax + ymax / 10
    plt.ylim(ymin, ymax)
    plt.xlim(np.min(x_plt_axis), np.max(x_plt_axis))

    ck = 1
    for hrd in range(1, len(ranges_to_printlay)):
        if ranges_to_printlay[hrd] == "time":
            continue
        else:
            plt.axes("OuterPosition", [0.01, ck / 3, 0.2, 0.3])
            plt.xlabel("Time")
            plt.title(ranges_to_printlay[hrd])
            data_temp = []
            for hse in range(1, len(times)):
                data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

            plt.plot(times, data_temp, "o:")
            plt.ylabel(ranges_to_printlay[hrd])
            ck = ck + 1

    axfp = plt.axes("OuterPosition", [0.01, 0, 0.2, 0.3])
    for hkw in range(1, len(requested_data)):
        plt.plot(range(harmonic_number), requested_data[hkw]["fill_pattern"], "b")

    plt.ylim(bottom=0)
    plt.xlim(1, harmonic_number)
    set(axfp, "XTick", [])
    plt.title("Fill pattern variation")
    plt.ylabel("Charge (nC)")
    # add labels if it is a parameter sweep['']
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"])):
            labels[tb] = experimental_setup["param"](tb)

        plt.legend(labels)
        plt.legend("Location", "eastoutside")

    if experimental_setup["anal_type"] == "parameter_sweep":
        plt.figure("Position", [50, 50, 1400, 800])
        if experimental_setup["sweep_parameter"] == "current":
            plt.axes("OuterPosition", [0, 0, 0.32, 0.5])
        else:
            plt.axes("OuterPosition", [0, 0, 1, 0.5])

        plt.plot(experimental_setup["param"], dr_passive)
        plt.xlabel(experimental_setup["sweep_parameter"])
        plt.ylabel("Passive damping rates (1/turns)")
        plt.plot(
            [experimental_setup["param"][0], experimental_setup["param"][-1]],
            [0, 0],
            "r:",
            "HandleVisibility",
            "off",
        )
        if experimental_setup["sweep_parameter"] == "current":
            plt.axes("OuterPosition", [0, 0.5, 0.32, 0.5])
        else:
            plt.axes("OuterPosition", [0, 0.5, 1, 0.5])

        plt.plot(experimental_setup["param"], dr_active)
        plt.xlabel(experimental_setup["sweep_parameter"])
        plt.ylabel("Active damping rates (1/turns)")
        plt.title(
            f"Damping rates vs {experimental_setup['sweep_parameter']}"
            f"in the {experimental_setup['axis']} axis"
        )
        plt.plot(
            [experimental_setup["param"][0], experimental_setup["param"][-1]],
            [0, 0],
            "r:",
            "HandleVisibility",
            "off",
        )
        if experimental_setup["sweep_parameter"] == "current":
            x1 = range(301)
            plt.axes("OuterPosition", [0.33, 0, 0.32, 0.5])
            passive_mode_rate = []
            for ks in range(1, len(dr_passive)):
                P = np.polyfit(experimental_setup["param"], dr_passive[:, ks], 1)
                passive_mode_rate[ks] = P[0]
                P_start = np.find(x1 < np.min(experimental_setup["param"]), 1, "last")
                P_points = np.polyval(P, x1)
                # Find the first time after the lowest current that the
                # extrapolation goes negative.
                P_loc = np.find(np.sign(P_points[P_start:-1]) == -1, 1, "first")
                if P_loc:
                    plt.plot(
                        x1,
                        P_points,
                        "DisplayName",
                        ["Mode ", (x_plt_axis(ks)), ": ", x1(P_loc), "mA"],
                        "LineWidth",
                        2,
                    )
                    plt.plot(
                        experimental_setup["param"],
                        dr_passive[:, ks],
                        "ko",
                        "HandleVisibility",
                        "off",
                    )

            plt.xlabel(experimental_setup["sweep_parameter"])
            plt.ylabel("Passive damping rates (1/turns)")
            plt.title("Extrapolated data")
            #         plt.legend('Location', 'eastoutside')
            plt.legend("off")
            plt.plot([x1[0], x1[-1]], [0, 0], "r:", "HandleVisibility", "off")
            plt.axes("OuterPosition", [0.67, 0, 0.32, 0.5])
            plt.plot(x_plt_axis, passive_mode_rate)
            plt.plot(
                [x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off"
            )
            plt.xlabel("Modes")
            plt.ylabel("Passive damping rates change with current (1/turns/current)")
            plt.xlim([np.min(x_plt_axis), np.max(x_plt_axis)])
            plt.axes("OuterPosition", [0.33, 0.5, 0.32, 0.5])
            active_mode_rate = []
            for ks in range(len(dr_active)):
                P = np.polyfit(experimental_setup["param"], dr_active[:, ks], 1)
                active_mode_rate[ks] = P[0]
                P_start = np.find(x1 < np.min(experimental_setup["param"]), 1, "last")
                P_points = np.polyval(P, x1)
                P_loc = np.find(np.sign(P_points[P_start:-1]) == -1, 1, "first")
                if P_loc:
                    plt.plot(
                        x1,
                        np.polyval(P, x1),
                        "DisplayName",
                        ["Mode ", (x_plt_axis(ks)), ": ", x1(P_loc), "mA"],
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
            plt.title("Extrapolated data")
            #         plt.legend('Location', 'eastoutside')
            plt.legend("off")
            plt.plot([x1[0], x1[-1]], [0, 0], "r:", "HandleVisibility", "off")
            plt.axes("OuterPosition", [0.67, 0.5, 0.32, 0.5])
            plt.plot(x_plt_axis, active_mode_rate)
            plt.plot(
                [x_plt_axis[0], x_plt_axis[-1]], [0, 0], "r:", "HandleVisibility", "off"
            )
            plt.xlabel("Modes")
            plt.ylabel("Active damping rates change with current (1/turns/current)")
            plt.xlim([np.min(x_plt_axis), np.max(x_plt_axis)])

    # if nargin == 9:
    #     figure
    #     ax3 = subplt.plot(2, 1, 1)
    #     populate_graph(error_passive, years_input, times, x_plt_axis)
    #     plt.title("Passive damping rate errors")
    #     plt.xlabel("Mode")
    #     plt.ylabel("Passive damping rate errors")
    #     ax4 = subplt.plot(2, 1, 2)
    #     populate_graph(error_active, years_input, times, x_plt_axis)
    #     plt.title("Active damping rate errors")
    #     plt.xlabel("Mode")
    #     plt.ylabel("Active damping rate errors")


def archival_plotting_frontend_clock_phase_scan(
    requested_data: list[dict],
    leading,
    excited,
    following,
    times: list[float],
    experimental_setup: dict,
):
    """Plots the data processed by growdamp_archival_analysis.
    Args:
         leading (numeric matrix):
         excited (numeric matrix):
         following (numeric matrix):
         times (numeric vector): Datetimes of the datasets.
         experimental_setup (structure): The setup parameters for the
                                         analysis.
         plot_error_graphs (anything): if present the code will plot the results
                                       of the fit errors.

    Example: growdamp_archival_plotting(requested_data, data_magnitude,
                                   data_phase, times, setup, selections, extents)
    """
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


def archival_plotting_setup(
    requested_data: list[dict], experimental_setup: dict
) -> None:
    """Plots the common data for all measurments.
    Args:
         requested_data: data and metatdata.
         experimental_setup: The setup parameters for the analysis.

    Example: archival_plotting_setup(requested_data, experimental_setup)
    """
    data_lists = reconfigure_to_lists(requested_data)
    [_3, harmonic_number, _2, _1] = system_config
    ranges_to_printlay = {"RF", "time", "current"}
    graph_text = f"Analysis type: {experimental_setup}[{anal_type}]"
    if experimental_setup["anal_type"] == "parameter_sweep":
        graph_labels = []
        for hw in range(len(experimental_setup["param"])):
            graph_labels[hw] = experimental_setup["param"](hw)

    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    plt.annotation(
        "textbox",
        [0, 1, -0.3, 0.3, 0.3],
        "String",
        graph_text,
        "FitBoxToText",
        "on",
        "Interpreter",
        "none",
    )
    # Plot the RF variation from the setpoint['']
    for hse in range(len(requested_data)):
        requested_data[hse]["RF"] = requested_data[hse]["RF"] - 4.99684e8

    ck = 1
    for hrd in range(1, len(ranges_to_printlay)):
        if ranges_to_printlay[hrd] == "RF":
            graph_label = "RF variation (Hz)"
        elif ranges_to_printlay[hrd] == "current":
            graph_label = "Current (mA)"
        else:
            graph_label = ranges_to_printlay[hrd]

        if ranges_to_printlay[hrd] in requested_data[1]:
            if ranges_to_printlay[hrd] == "time":
                continue
            else:
                plt.xlabel("Time")
                plt.title(ranges_to_printlay[hrd])
                data_temp = []
                for hse in range(len(requested_data)):
                    data_temp[hse] = requested_data[hse][ranges_to_printlay[hrd]]

                plt.plot[data_lists["times"], data_temp, "o:"]
                plt.datetick("x", "dd-mmm-yy")
                plt.ylabel(graph_label)
                if ranges_to_printlay[hrd] == "RF":
                    plt.title("reference 499.684MHz")

                ck = ck + 1

    if "fill_pattern" in requested_data[1]:
        for hkw in range(1, len(requested_data)):
            plt.plot[1:harmonic_number, requested_data[hkw]["fill_pattern"], "b"]

        plt.ylim(bottom=0)
        plt.xlim(1, harmonic_number)
        set(axfp, "XTick", [])
        plt.title("Fill pattern variation")
        plt.ylabel("Charge (nC)")

    # add labels if it is a parameter sweep.
    if experimental_setup["anal_type"] == "parameter_sweep":
        labels = []
        for tb in range(len(experimental_setup["param"], -1, 1)):
            labels.append(experimental_setup["param"][tb])

        plt.legend(labels)

    return fig
