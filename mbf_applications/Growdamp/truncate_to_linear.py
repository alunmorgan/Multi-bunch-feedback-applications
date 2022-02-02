import numpy # type: ignore

from mbf_applications.Common.moving_average import movingAverage


def truncateToLinear(data_in, len_averaging, n_tests=100):
    # truncating the data if it falls into the noise

    # reduce the high frequency noise.
    mm = moving_average(abs(data_in), len_averaging)
    p = numpy.polyfit(range(len(mm)), mm, 1)

    if p[0] > 0:
        # growth
        return data_in

    truncation_point_end = findEndTrunctionPoint(mm, n_tests)
    if truncation_point_end < 10:
        print(
            "".join(
                (
                    "truncate_to_linear: Truncation would be too severe. ",
                    "Returning original data.",
                )
            )
        )
        return data_in

    truncation_point_start = findStartTrunctionPoint(
        mm[0:truncation_point_end], n_tests
    )
    if truncation_point_start > truncation_point_end - 10:
        print(
            "".join(
                (
                    "truncate_to_linear: Truncation would be too severe. ",
                    "Setting start truncation to 1",
                )
            )
        )
        data_out = data_in[0:truncation_point_end]
        return data_out

    truncation_point_end = findEndTrunctionPoint(mm[truncation_point_start:-1], n_tests)
    if truncation_point_end < truncation_point_start + 10:
        print(
            "".join(
                (
                    "truncate_to_linear: Truncation would be too severe. ",
                    "Returning original data.",
                )
            )
        )
        return data_in

    data_out = data_in[truncation_point_start:truncation_point_end]
    return data_out


def findEndTrunctionPoint(mm, n_tests):
    # Truncate the end by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit.
    ind = []
    overall_error = numpy.array()
    for gra in range(n_tests):
        ind[gra] = numpy.floor(len(mm) * (gra + 1) / n_tests)
        y = mm[0 : ind[gra]]
        x = range(len(y))
        p, S = numpy.polynomial.Polynomial.fit(x, y, 1)
        _1, delta = numpy.polyval(p, x, S)
        #     The 1/ind is to make the errors at the begining of the decay count for
        #     more than the ones at the end.
        overall_error[gra] = numpy.mean(abs(delta) * 1 / ind[gra])
        if ind[gra] < 100:
            ind = ind[gra:-1]
            overall_error = overall_error[gra:-1]
            break

    min_val = numpy.min(overall_error)
    x_of_min = numpy.where(overall_error == min_val)
    truncation_point_end = ind[x_of_min[0]]
    return truncation_point_end


def findStartTrunctionPoint(mm, n_tests):
    # Truncate the begining by increasing amounts and find the level of truncation which
    # gives the smallest residuals to a linear fit. This is to deal with odd effects
    # which sometimes happen at the beginning (due to delays in the sysytem?)
    ind = []
    overall_error = numpy.array()
    for gra in range(n_tests):
        ind[gra] = numpy.ceil(len(mm) * (gra + 1) / n_tests)
        if ind[gra] >= len(mm) - 5:
            break

        y = mm[ind[gra] : -1]
        x = range(len(y))
        p, S = numpy.polynomial.Polynomial.fit(x, y, 1)
        _1, delta = numpy.polyval(p, x, S)
        overall_error[gra] = numpy.mean(abs(delta) * ind[gra]) / len(delta)

    min_val = numpy.min(overall_error)
    x_of_min = numpy.where(overall_error == min_val)
    truncation_point_start = ind[x_of_min[0]]
    return truncation_point_start
