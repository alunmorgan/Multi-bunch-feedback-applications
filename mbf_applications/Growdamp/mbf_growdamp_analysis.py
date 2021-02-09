import numpy  # type: ignore

from mbf_applications.Growdamp.mbf_growdamp_advanced_fitting import (
    mbfGrowdampAdvancedFitting,
)
from mbf_applications.Growdamp.mbf_growdamp_basic_fitting import mbfGrowdampBasicFitting
from mbf_applications.Growdamp.truncate_to_linear import truncateToLinear


def mbfGrowdampAnalysis(
    exp_data, passive_override=None, active_override=None, len_averaging=None
):
    """takes the data from mbf growdamp capture and fits it with a series of
    linear fits to get the damping times for each mode.

    Args:
        exp_data (structure): Contains the systems setup and the data
                                captured.
        overrides (list of ints): Two values setting the number of turns to
                                    analyse (passive, active)
    Returns:
        poly_data (3 by 3 matrix): axis 1 is coupling mode.
                                    axis 2 is expermental state,
                                    excitation, natural damping, active damping).
                                    axis 3 is damping time, offset and
                                    fractional error.
        frequency_shifts (list of floats): The frequency shift of each mode.

    Example: poly_data, frequency_shifts = tmbf_growdamp_analysis(exp_data)
    """

    harmonic_number = len(exp_data["fill_pattern"])
    data = numpy.array()
    # Sometimes there is a problem with data transfer. By truncating the data
    # length to a multiple of the harmonic number the analysis can proceed.
    cycles, stub = numpy.divmod(len(exp_data["data"]), harmonic_number)
    data = exp_data["data"][1:-stub]
    data = exp_data["data"][1:-stub]
    data.reshape(cycles, harmonic_number)
    n_modes = data.shape[1]
    # Preallocation
    # poly_data = NaN(harmonic_number, 3, 3)
    # frequency_shifts = NaN(harmonic_number, 1)

    # Find the idicies for the end of each period.
    end_of_growth = exp_data["growth_turns"]
    end_of_passive = end_of_growth + exp_data["nat_turns"]
    end_of_active = end_of_passive + exp_data["act_turns"]

    if data.shape[0] < end_of_active:
        print("".join(("No valid data for ", exp_data["filename"])))
        return [], []

    if "growth_dwell" in exp_data:
        growth_dwell = exp_data["growth_dwell"]
    else:
        growth_dwell = None

    if "nat_dwell" in exp_data:
        nat_dwell = exp_data["nat_dwell"]
    else:
        nat_dwell = None

    if "act_dwell" in exp_data:
        act_dwell = exp_data["act_dwell"]
    else:
        act_dwell = None

    s1_acum = []
    s2_acum = []
    s3_acum = []
    delta1_acum = []
    delta2_acum = []
    delta3_acum = []
    p2_acum = []
    for nq in range(n_modes):
        # split up the data into growth, passive damping and active damping.
        data_mode = data[nq, :]
        # growth
        x1 = range(end_of_growth)
        g_data = data_mode[x1]
        s1 = numpy.polynomial.Polynomial.fit(x1, numpy.log(abs(g_data)), 1)
        c1 = numpy.polyval(s1, x1)
        delta1 = numpy.mean(abs(c1 - numpy.log(abs(g_data))) / c1)

        # passive damping
        x2 = end_of_growth + range(end_of_passive)
        pd_data = data_mode[x2]
        if passive_override is not None:
            if passive_override < len(pd_data):
                pd_data = pd_data[0:passive_override]
        else:
            pd_data = truncateToLinear(pd_data, len_averaging)

        if len(pd_data) < 3:
            s2 = [None, None]
            delta2 = None
            p2 = None
        else:
            if len_averaging is None:
                s2, delta2, p2 = mbfGrowdampBasicFitting(pd_data)
            else:
                s2, delta2, p2 = mbfGrowdampAdvancedFitting(pd_data, len_averaging)

        # active damping
        x3 = end_of_passive + range(end_of_active)
        ad_data = data_mode[x3]
        if active_override is not None:
            if active_override < len(ad_data):
                ad_data = ad_data[0:active_override]
        else:
            ad_data = truncateToLinear(ad_data, len_averaging)

        if len(x3) < 3:
            s3 = [None, None]
            delta3 = None
        else:
            if len_averaging is None:
                s3, delta3, _1 = mbfGrowdampBasicFitting(ad_data)
            else:
                s3, delta3, _1 = mbfGrowdampAdvancedFitting(ad_data, len_averaging)

        # Each point is dwell time turns long so the
        # damping time needs to be adjusted accordingly.
        s1[0] = s1[0] / growth_dwell
        s2[0] = s2[0] / nat_dwell
        s3[0] = s3[0] / act_dwell

        s1_acum.append(s1)
        s2_acum.append(s2)
        s3_acum.append(s3)
        delta1_acum.append(delta1)
        delta2_acum.append(delta2)
        delta3_acum.append(delta3)
        p2_acum.append(p2[0])

    # Output data structure.
    # axis 1 is mode, axis 2 is expermental state (excitation, natural
    # damping, active damping). axis 3 is damping time, offset and fractional error.
    poly_data = []
    poly_data[0][0] = s1_acum
    poly_data[1][0] = s2_acum
    poly_data[2][0] = s3_acum
    poly_data[0][1] = delta1_acum
    poly_data[1][1] = delta2_acum
    poly_data[2][1] = delta3_acum
    frequency_shifts = p2_acum

    return poly_data, frequency_shifts
