import numpy


def mbfGrowdampBasicFitting(data):

    x_ax = range(len(data))
    s = numpy.polynomial.Polynomial.fit(x_ax, numpy.log(abs(data)), 1)
    c = numpy.polyval(s, x_ax)
    delta = numpy.mean(abs(c - numpy.log(abs(data))) / c)
    temp = numpy.unwrap(numpy.angle(data)) / (2 * numpy.pi)
    p = numpy.polynomial.Polynomial.fit(x_ax, temp, 1)
    return s, delta, p
