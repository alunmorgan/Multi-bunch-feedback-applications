import matplotlib.pyplot as plt # type: ignore
import numpy # type: ignore


def mbfGrowdampPlotSummary(poly_data, frequency_shifts):
    """Plots the driven growth rates, and the active and pasive damping rates
    across all modes.

    Args:
        poly_data list of lists: axis 1 is coupling mode.
                                    axis 2 is expermental state,
                                    excitation, natural damping, active damping).
                                    axis 3 is damping time, offset and
                                    fractional error.
        frequency_shifts (list of floats): The frequency shift of each mode.

    Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts)
    """

    # Getting the desired system setup parameters.
    harmonic_number = len(frequency_shifts)

    x_plt_axis = range(harmonic_number - 1) - harmonic_number / 2
    passive_data = -poly_data[1][0]
    active_data = -poly_data[2][0]

    passive_errors = not numpy.isnan(passive_data)
    active_errors = not numpy.isnan(active_data)

    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    ax1.plot(
        x_plt_axis,
        numpy.roll(passive_data, -harmonic_number / 2, 1),
        "b",
        label="Passive",
    )
    ax1.plot(
        x_plt_axis,
        numpy.roll(active_data, -harmonic_number / 2, 1),
        "g",
        label="Active",
    )
    ax1.plot(x_plt_axis, numpy.zeros(len(x_plt_axis), 1), "r:")
    ax1.plot(x_plt_axis, numpy.roll(passive_errors, -harmonic_number / 2, 1), "c*")
    ax1.plot(x_plt_axis, numpy.roll(active_errors, -harmonic_number / 2, 1), "m*")
    ax1.set_xlim(x_plt_axis[0], x_plt_axis[-1])
    ax1.set_title("Damping rates for different modes")
    ax1.set_xlabel("Mode")
    ax1.set_ylabel("Damping rates (1/turns)")
    ax1.legend()

    ax2 = fig.add_subplot(212, share=ax1)
    ax2.plot(x_plt_axis, numpy.roll(frequency_shifts, -harmonic_number / 2, 1))
    ax2.set_xlim(x_plt_axis[0], x_plt_axis[-1])
    ax2.set_title("Tune shift from excitation")
    ax2.set_xlabel("Mode")
    ax2.set_ylabel("Difference from excitation tune")
