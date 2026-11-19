import os
import re

import matplotlib.pyplot as plt
import matplotlib.text as mplt
import numpy as np
from analysis import tune_fit

from Common import (
    construct_datastamped_filename,
    mode_to_frequency,
    tree_gen,
)


def save_graphs(root_string: str, metadata: dict, graph_handles=()):
    """Saves the requested graphs in the given filename in a location
    detemined by the time_value.
    The relavent folder structure will be generated.

      Args:
          root_string:
          metadata: original captured meta data
          graph_handles
    Example: archive_graphs(root_string, data, graph_handles)
    """
    # Generating the required directory structure.
    tree_gen(root_string, metadata["time"])
    # construct filename and add it to the structure
    metadata["filename"] = construct_datastamped_filename(
        metadata["base_name"], metadata["time"]
    )

    for heaq in range(1, len(graph_handles)):
        if ishandle(graph_handles(heaq)):
            graph_save_name = os.path.join(
                root_string,
                (metadata["time"].year),
                f"{metadata['time'].month: 02d}",
                f"{metadata['time'].day: 02d}",
                metadata["filename"],
            )
            plt.savefig(
                graph_handles(heaq), f"{graph_save_name}, _figure_, {heaq}, .png"
            )
            plt.savefig(
                graph_handles(heaq), f"{graph_save_name}, _figure_, {heaq}, .fig"
            )


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


def plotting_growdamp(data: dict, metadata: dict, plot_mode: str = "pos"):
    """Plots the driven growth rates, and the active and pasive damping rates
    # across all modes.
    #
    # Args:
    #       poly_data (3 by 3 matrix): axis 1 is coupling mode.
    #                                  axis 2 is expermental state,
    #                                  excitation, natural damping, active damping).
    #                                  axis 3 is damping time, offset and
    #                                  fractional error.
    #       frequency_shifts (list of floats): The frequency shift of each mode.
    #       metadata (structure): setup information.
    #       axis: 'x', 'y' or 's'
    #       plot_mode: 'pos' or 'neg'[''] Determines if plot modes 0:harmonic_number or
    #       -harmonic_number/2:harmonic_number/2
    #
    # Example: growdamp_plot_summary(poly_data, frequency_shifts, 'passive')
    """
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


def plotting_modescan(data_magnitude, data_phase, modescan: dict):
    """Plots the effectiveness of correction across all modes['']

    Args:
          data_magnitude(vector of floats): averaged signal magnitude over modes['']
          data_phase(vector of floats): averaged signal phase over modes['']
          modescan(structure): captured data

    Example: modescan_plotting(data_magnitude, data_phase, modescan)
    """
    # FIXME
    fig, _1 = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    fig.suptitle(
        f"MBF modescan results {modescan['ax_label']} axis "
        f"{modescan['time'].strftime('%d_%m_%y-%H-%M-%S')}"
        f"Current: {(round(modescan['current']))} mA",
    )
    plt.plot(data_magnitude[1 : modescan["harmonic_number"]])
    plt.xlim([1, modescan["harmonic_number"]])
    fig.title("Amplitude")
    plt.xlabel("Modes")

    plt.plot(data_phase(), "DisplayName", "data", "LineWidth", 2)

    plt.plot(
        range(modescan["harmonic_number"]),
        np.ones(modescan["harmonic_number"]) * -90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        range(modescan["harmonic_number"]),
        np.ones(modescan["harmonic_number"]) * 90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    plt.title("Phase (deg)")
    plt.xlim([1, modescan["harmonic_number"]])
    plt.legend("Location", "northoutside")
    plt.xlabel("Modes")
    [_1, data_mag] = mode_to_frequency(
        modescan["RF"],
        modescan["harmonic_number"],
        modescan["tunes"][""]([modescan["ax_label"], "_tune"])["tune"],
        data_magnitude,
    )
    [x_data, data_phse] = mode_to_frequency(
        modescan["RF"],
        modescan["harmonic_number"],
        modescan["tunes"][""]([modescan["ax_label"], "_tune"])["tune"],
        data_phase,
    )

    plt.plot(x_data * 1e-6, data_mag)
    plt.xlim([0, max(x_data * 1e-6)])
    plt.title("Amplitude")
    plt.xlabel("Frequency (MHz)")

    plt.plot(x_data * 1e-6, data_phse, "DisplayName", "data", "LineWidth", 2)
    # take the mean of an even number of points to make things more robust['']
    grad_start = np.mean(data_phse[1:4])
    grad_end = np.mean(data_phse[-5:-1])
    target_grad = (grad_end - grad_start) / x_data[-1]
    phase_offset = x_data * target_grad
    phase_angle = np.round(phase_offset[-1] * 10) / 10
    delay_time = np.round(phase_offset[-1] / (360 * x_data[-1]) * 1e12)
    velocity_factor = 0.7
    adjustment_length = round(delay_time * 1e-12 * velocity_factor * 3e8 * 1e3)
    plt.plot(
        phase_offset + grad_start,
        "DisplayName",
        [
            "fit ",
            (phase_angle),
            " degrees total, delay = ",
            (delay_time),
            "ps, adjustment length approx ",
            (adjustment_length),
            "mm",
        ],
        "LineWidth",
        2,
    )
    plt.plot(
        x_data * 1e-6,
        np.ones(len(x_data)) * -90,
        ":r",
        "DisplayName",
        "Limits",
        "LineWidth",
        2,
    )
    plt.plot(
        x_data * 1e-6,
        np.ones(len(x_data)) * 90,
        ":r",
        "LineWidth",
        2,
        "HandleVisibility",
        "off",
    )
    plt.title("Phase (deg)")
    plt.xlim([1, max(x_data * 1e-6)])
    plt.legend("Location", "northoutside")
    plt.xlabel("Frequency (MHz)")


def plotting_spectrum(requested_data: list[dict], analysed_data):
    """Plots the data saved and analysed by the earlier mbf_spectrum def s['']:
    # Args:
    #         all_data(structure): analysed data['']
    #
    # Example: spectrum_plotting(data
    """
    if max(max(analysed_data["bunch_f_data"])) == 0:
        print("No data to plot")
        return

    plt.figure("Position", [20, 40, 1200, 800])
    fig, ax = plt.subplot_mosaic(
        [["upper left", "upper right"], ["lower left", "lower right"]],
        figsize=(5.5, 3.5),
        layout="constrained",
    )
    fig.title(
        f"MBF spectrum results {requested_data['ax_label']} axis "
        f"{requested_data['time'].strftime('%a %d %b %Y, %I:%M%p')} "
        f"Current: {round(requested_data['current'])} mA"
    )
    signal_per_bunch = sum(analysed_data["bunch_f_data"], 2)
    frequency_all_bunches = sum(analysed_data["bunch_f_data"], 1)

    plt.imagesc(
        "Xdata",
        analysed_data["bunch_f_scale"][""] * 1e-3,
        "Ydata",
        range(len(analysed_data["bunch_f_bunches"])),
        "Cdata",
        analysed_data["bunch_f_data"],
        [-3, 0] + max(max(analysed_data["bunch_f_data"])),
    )
    plt.colorbar("westoutside")
    set(ax[0], "YAxisLocation", "right")
    set(ax[0], "YDir", "normal")
    set(ax[0], "XTick", [])
    set(ax[0], "YTick", [])
    # plt.title(axis_label)
    # bunches graph
    plt.plot(signal_per_bunch, range(len(analysed_data["bunch_f_bunches"])))
    set(ax[1], "YAxisLocation", "right")
    set(ax[1], "XAxisLocation", "top")
    set(ax[1], "XTick", [])
    plt.ylabel("Bunch number")

    # Frequency graph
    ax[2].plot(analysed_data["bunch_f_scale"] * 1e-3, frequency_all_bunches)
    plt.xlabel("Frequency (KHz)")
    plt.xlim(
        min(analysed_data["bunch_f_scale"]) * 1e-3,
        max(analysed_data["bunch_f_scale"]) * 1e-3,
    )
    plt.ylim(0, max(frequency_all_bunches))
    # Tune graph
    ax[3].plot(analysed_data["bunch_tune_scale"], frequency_all_bunches)
    ax[3].ylim([0, max(frequency_all_bunches)])
    lims = ax[3].ylim
    ax[3].plot(
        [
            requested_data["tunes"]["x_tune"]["tune"],
            requested_data["tunes"]["x_tune"]["tune"],
        ],
        [0, lims[1]],
        ":r",
        "LineWidth",
        2,
        "DisplayName",
        "Horizontal tune",
    )
    ax[3].plot(
        [
            requested_data["tunes"]["y_tune"]["tune"],
            requested_data["tunes"]["y_tune"]["tune"],
        ],
        [0, lims[1]],
        ":c",
        "LineWidth",
        2,
        "DisplayName",
        "Vertical tune",
    )
    ax[3].plot(
        [
            requested_data["tunes"]["s_tune"]["tune"],
            requested_data["tunes"]["s_tune"]["tune"],
        ],
        [0, lims[1]],
        ":g",
        "LineWidth",
        2,
        "DisplayName",
        "Longitudinal tune",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["x_tune"]["tune"],
            -requested_data["tunes"]["x_tune"]["tune"],
        ],
        [0, lims[1]],
        ":r",
        "LineWidth",
        2,
        "DisplayName",
        "Horizontal tune",
        "HandleVisibility",
        "off",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["y_tune"]["tune"],
            -requested_data["tunes"]["y_tune"]["tune"],
        ],
        [0, lims[1]],
        ":c",
        "LineWidth",
        2,
        "DisplayName",
        "Vertical tune",
        "HandleVisibility",
        "off",
    )
    ax[3].plot(
        [
            -requested_data["tunes"]["s_tune"]["tune"],
            -requested_data["tunes"]["s_tune"]["tune"],
        ],
        [0, lims[1]],
        ":g",
        "LineWidth",
        2,
        "DisplayName",
        "Longitudinal tune",
        "HandleVisibility",
        "off",
    )
    plt.xlabel("Tune")


def plotting_bunch_motion(data, selected_bunches, selected_turns):
    x = np.reshape(data["x"], data["num_buckets"], [])
    y = np.reshape(data["y"], data["num_buckets"], [])
    z = np.reshape(data["z"], data["num_buckets"], [])
    bucket_numbers = range(data["num_buckets"])
    turn_numbers = range(x.shape[1])
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(x[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(y[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(z[:, 1:100], 2), 1, len(turn_numbers))
    x = x - x_ref
    y = y - y_ref
    z = z - z_ref
    # Find the location of the largest disturbance.
    # FIXME how do you do this using numpy?
    [minx, minindx] = min(x)
    [maxx, maxindx] = max(x)
    [miny, minindy] = min(y)
    [maxy, maxindy] = max(y)
    [minz, minindz] = min(z)
    [maxz, maxindz] = max(z)
    [_1, loc] = max([abs(minx), maxx, abs(miny), maxy, abs(minz), maxz])
    indexes = [minindx, maxindx, minindy, maxindy, minindz, maxindz]
    index_of_peak = indexes(loc)
    [peak_row, peak_col] = ind2sub(x.shape, index_of_peak)
    turn_of_peak = peak_col
    bucket_of_peak = peak_row - 1
    print(f"Start turn of kick is {turn_of_peak}")
    print(f"Main bucket kicked {bucket_of_peak}")
    fill_pattern = data["fill_pattern2"]

    meanx = np.mean(x, 1)
    meany = np.mean(y, 1)
    meanz = np.mean(z, 1)
    stdx = np.std(x, ddof=1, axes=1)
    stdy = np.std(y, ddof=1, axes=1)
    stdz = np.std(z, ddof=1, axes=1)
    f1 = plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(4, 1)
    plt.suptitle(f1, data["filename"], "Interpreter", "None")
    plt.xlabel("Bunches")
    # ax1 = nexttile
    plt.plot(bucket_numbers, fill_pattern)
    plt.ylabel("Charge")
    # ax2 = nexttile
    plt.plot(
        bucket_numbers,
        meanx,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meanx + stdx, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meanx - stdx, "m", "HandleVisibility", "off")
    plt.title("Horizontal motion")
    plt.ylabel("Motion")
    # ax3 = nexttile
    plt.plot(
        bucket_numbers,
        meany,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meany + stdy, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meany - stdy, "m", "HandleVisibility", "off")
    plt.title("Vertical motion")
    plt.ylabel("Motion")
    # ax4 = nexttile
    plt.plot(
        bucket_numbers,
        meanz,
        "k",
        "LineWidth",
        2,
        "DisplayName",
        "Mean motion over all turns",
    )
    plt.plot(
        bucket_numbers, meanz + stdz, "m", "DisplayName", "Std motion over all turns"
    )
    plt.plot(bucket_numbers, meanz - stdz, "m", "HandleVisibility", "off")
    plt.title("Longitudinal motion")
    plt.ylabel("Motion")

    f2 = plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 3)
    plt.suptitle(f2, data["filename"], "Interpreter", "None")
    plt.xlabel(f2, "Turns")
    plt.imagesc(turn_numbers, bucket_numbers, x)
    plt.title("Horizontal motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    # Sometimes matlab has a delay plotting the previous plot
    # and this breaks everything.
    plt.imagesc(turn_numbers, bucket_numbers, y)
    plt.title("Vertical motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    plt.imagesc(turn_numbers, bucket_numbers, z)
    plt.title("Longitudinal motion")
    plt.ylabel("Bunches")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            x[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.legend("Location", "northoutside", "NumColumns", 2)
    plt.title("Horizontal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            y[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Vertical motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            z[selected_bunches[sje] + 1, :],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Longitudinal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            x[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.legend("Location", "northoutside", "NumColumns", 2)
    plt.title("Horizontal motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            y[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Vertical motion")
    plt.figure(f2)
    for sje in range(len(selected_bunches)):
        plt.plot(
            selected_turns,
            z[selected_bunches[sje] + 1, selected_turns],
            "DisplayName",
            f"Bunch {selected_bunches[sje]}",
        )

    plt.title("Longitudinal motion")
    # FIXME make sure the coeect graph is saved to the correct file.
    plt.savefig(f"{data['filename']}_bunches.png")
    plt.savefig(f"{data['filename']}_turns.png")


def plotting_bunch_motion_spectra(data):
    xt = np.reshape(data["x"], data["num_buckets"], [])
    yt = np.reshape(data["y"], data["num_buckets"], [])
    zt = np.reshape(data["z"], data["num_buckets"], [])
    n_turns = xt.shape[1]
    bucket_numbers = range(data["num_buckets"])
    turn_numbers = range(n_turns)
    T = 1  # turns Sampling period
    Fs = 1 / T  # Sampling frequency
    f_scale = Fs * (range((n_turns / 2) + 1)) / n_turns
    # Normalise each bunch signal to the average of the first 100 turns
    x_ref = np.repmat(np.mean(xt[:, 1:100], 2), 1, len(turn_numbers))
    y_ref = np.repmat(np.mean(yt[:, 1:100], 2), 1, len(turn_numbers))
    z_ref = np.repmat(np.mean(zt[:, 1:100], 2), 1, len(turn_numbers))
    xt = xt - x_ref
    yt = yt - y_ref
    zt = zt - z_ref
    x1 = np.fft(xt, [], 2)
    x1 = abs(x1 / n_turns)
    x = x1[:, 1 : n_turns / 2 + 1]
    x[:, 2:-2] = 2 * x[:, 2:-2]
    y1 = np.fft(yt, [], 2)
    y1 = abs(y1 / n_turns)
    y = y1[:, 1 : n_turns / 2 + 1]
    y[:, 2:-2] = 2 * y[:, 2:-2]
    z1 = np.fft(zt, [], 2)
    z1 = abs(z1 / n_turns)
    z = z1[:, 1 : n_turns / 2 + 1]
    z[:, 2:-2] = 2 * z[:, 2:-2]
    # Find the location of the largest disturbance.
    [maxx, maxindx] = max(x[:])
    peak_row_x, peak_col_x = ind2sub(x.shape, maxindx)
    f_of_peak_x = f_scale(peak_col_x)
    bucket_of_peak_x = peak_row_x - 1
    [maxy, maxindy] = max(y[:])
    peak_row_y, peak_col_y = ind2sub(y.shape, maxindy)
    f_of_peak_y = f_scale(peak_col_y)
    bucket_of_peak_y = peak_row_y - 1
    [maxz, maxindz] = max(z[:])
    peak_row_z, peak_col_z = ind2sub(z.shape, maxindz)
    f_of_peak_z = f_scale(peak_col_z)
    bucket_of_peak_z = peak_row_z - 1
    _1, loc = max([maxx, maxy, maxz])
    ax_labs = {"x", "y", "z"}
    print(f"Axis with most disturbance is {ax_labs[loc]}")
    print(f"Tune of main disturbance in x is {f_of_peak_x}")
    print(f"Bucket of main disturbance in x is {bucket_of_peak_x}")
    print(f"Tune of main disturbance in y is {f_of_peak_y}")
    print(f"Bucket of main disturbance in y is {bucket_of_peak_y}")
    print(f"Tune of main disturbance in z is {f_of_peak_z}")
    print(f"Bucket of main disturbance in z is {bucket_of_peak_z}")
    plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 1)
    plt.title(data["filename"], "Interpreter", "None")
    plt.ylabel("Bunches")
    plt.xlabel("Tune (1/Turns)")
    # ax2 = nexttile
    plt.imagesc(f_scale, bucket_numbers, x)
    plt.title("Horizontal motion")
    # ax3 = nexttile
    plt.imagesc(f_scale, bucket_numbers, y)
    plt.title("Vertical motion")
    # ax4 = nexttile
    plt.imagesc(f_scale, bucket_numbers, z)
    plt.title("Longitudinal motion")
    plt.figure("OuterPosition", [20, 20, 1800, 1000])
    # t = tiledlayout(3, 1)
    plt.title(data["filename"], "Interpreter", "None")
    plt.ylabel("Bunches")
    plt.xlabel("Tune (1/Turns)")
    # ax2 = nexttile
    plt.plot(f_scale, abs(x[bucket_of_peak_x + 1, :]))
    plt.title(["Horizontal motion (bucket ", (bucket_of_peak_x), ")"])
    # ax3 = nexttile
    plt.plot(f_scale, abs(y[bucket_of_peak_y + 1, :]))
    plt.title(["Vertical motion (bucket ", (bucket_of_peak_y), ")"])
    # ax4 = nexttile
    plt.plot(f_scale, abs(z[bucket_of_peak_z + 1, :]))
    plt.title(["Longitudinal motion (bucket ", (bucket_of_peak_z), ")"])


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


def plotting_frontend_gain_scan(data):
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


def plotting_frontend_system_phase_scan(data):
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


def plotting_doris_target_phase_scan(data):
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


def plotting_pll_phase_scan(fll_phase_scan):
    """Plots the results of a FLL phase scan on the
    multi binch feedback system

      Args:
          fll_phase_scan(struct): data captured during the phase scan['']

      Returns:
          f1(plt.figure handle):

    Example: f1 = fll_phase_scan_plotting(fll_phase_scan)
    """
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


def plotting_pll_phase_scan_multi(
    selected_axis, requested_data, scan_type="samples", target_bunch_override=None
):
    """Plots the results of a FLL phase scan on the
    multi bunch feedback system

      Args:
          fll_phase_scan(struct): data captured during the phase scan['']
          scan_type(str): states what the scan variable was
                          'samples', 'charge', 'gain', 'rf'
          target_bunch_override(int): force the target bunch location to be this
                                      value

    Example: fll_phase_scan_plotting_multi(requested_data, varargin)
    """
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


def plotting_tunescan_over_modes(tunescan):
    """Plots the effectiveness of correction across all modes.

    Args:
          tunescan (structure): Captured data from a single experiment.

    Example: mbf_tunescan_plotting(tunescan)
    """
    # reshape the results
    fracttune = tunescan["scale"][1 : tunescan["n_captures"]]
    for n in range(tunescan["data"].shape[1]):
        result = np.reshape(
            abs(tunescan["data"][:, n]),
            tunescan["n_captures"],
            tunescan["harmonic_number"],
        )
        fit_width = []
        fit_height = []
        fit_centre = []
        fit_confidence = []
        for js in range(result.shape[1]):
            [fit_curve, gof2] = tune_fit(fracttune, result[:, js])
            fit_width[js] = fit_curve["a"]
            fit_height[js] = fit_curve["c"] * 2 / np.pi / fit_width[js]
            fit_centre[js] = fit_curve["n"]
            fit_confidence[js] = gof2["sse"]

        # find zoomed in area.
        lower_tune_limit = np.mean(fit_centre) - np.max(fit_width) / 2
        upper_tune_limit = np.mean(fit_centre) + np.max(fit_width) / 2
        # plot the results
        f = plt.figure("Position", [20, 40, 1600, 800])
        fig, _1 = plt.subplot_mosaic(
            [["upper left", "upper right"], ["lower left", "lower right"]],
            figsize=(5.5, 3.5),
            layout="constrained",
        )
        fig.suptitle(
            f"MBF tunescan results {tunescan['ax_label']} axis "
            f"{tunescan['time'].strftime('%a %d %b %Y, %I:%M%p')}"
            f"Current: {round(tunescan['current'])} mA",
        )
        plt.imagesc(range(tunescan["harmonic_number"]), fracttune, result)
        plt.xlabel("mode number")
        plt.ylabel("fractional tune")
        plt.ylabel("magnitude of response")
        plt.imagesc(range(tunescan["harmonic_number"]), fracttune, result)
        plt.ylim(lower_tune_limit, upper_tune_limit)
        plt.xlabel("mode number")
        plt.ylabel("fractional tune")
        plt.ylabel("magnitude of response")
        plt.plot(
            range(tunescan["harmonic_number"]),
            np.max(result, [], 1),
            "DisplayName",
            "Raw data",
            "LineWidth",
            2,
        )
        plt.plot(
            range(tunescan["harmonic_number"]),
            fit_height,
            "m",
            "DisplayName",
            "Fitted data",
        )
        plt.xlabel("mode number")
        plt.ylabel("magnitude of peak")
        plt.plot(
            range(tunescan["harmonic_number"]),
            fit_width,
            "m",
            "DisplayName",
            "Fitted data",
        )
        plt.xlabel("mode number")
        plt.ylabel("width of peak")
        plt.plot(
            range(tunescan["harmonic_number"]),
            fit_confidence,
            "m",
            "DisplayName",
            "Fitted data",
        )
        plt.xlabel("mode number")
        plt.ylabel("error of fit")


def plotting_frontend_clock_phase_scan(data: dict):
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
    fig.supplot.title(
        f"BBBFE '{graph_name} axis on {data['time'].strftime('%a %d %b %Y, %I:%M%p')}"
    )
    fig.subplot.title(instructions, "FontAngle", "italic", "FontSize", 10)
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
