from Common import movingAverage
import numpy


def mbf_growdamp_advanced_fitting(data, length_averaging):

    mm = movingAverage(abs(data), length_averaging)
    # Get an initial starting value.
    p_initial = numpy.polynomial.Polynomial.fit(range(len(mm)), mm, 1)
    if p_initial[0] < 0:
        # damping
        # find the max so as to allow any initial rise in the data to be
        # removed.
        max_val = numpy.max(mm)
        dm_loc = numpy.where(mm == max_val)
        dm_loc = 2 * dm_loc
    else:
        # growth
        dm_loc = 0

    x_ax = range(len(mm)-1 - dm_loc)
    n_tests = 200
    # compare linear fits to the data.
    vals = linspace(p_initial(1), p_initial(1) - 2e-7, n_tests)
    # sweep the gradient. Large changes in sample length indicate that a large
    # fraction of the line has moved from below the line to above it.
    sample_length = numpy.array()
    for gra in range(n_tests):
        y = vals[gra] * x_ax + mm[dm_loc + 1]
        weighted_error = mm[dm_loc + 1:-1] - y  # .* linspace(length(mm)-1 - dm_loc, 0 , length(mm)-dm_loc)
        weighted_error[weighted_error > 0] = 0
        err_min = min(weighted_error)
        min_loc = numpy.where(weighted_error == err_min)
        sample_length_temp = find(weighted_error[min_loc:-1] == 0, 1, 'first')
        if isempty(sample_length_temp):
            sample_length[gra] = len(x_ax)
        else:
            sample_length[gra] = sample_length_temp + min_loc - 1

        if sample_length[gra] < 3:
            break

    ts = numpy.diff(sample_length)
    min_val = min(ts)
    Idw = numpy.where(ts == min_val)
    if not Idw == 1:
        Idw = Idw-1

    s = [vals(Idw), mm(dm_loc + 1)]
    c = numpy.polyval(s, range(len(mm)))
    delta = numpy.mean(abs(c - numpy.log(abs(data))) / c)
    temp = numpy.unwrap(numpy.angle(data)) / (2 * numpy.pi)
    p = numpy.polynomial.Polynomial.fit(range(len(mm)), temp, 1)

    return s, delta, p
