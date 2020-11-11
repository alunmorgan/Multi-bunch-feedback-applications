from time import sleep
import cmath
import numpy
from cothread.catools import caGet, caPut
from Common import findPositionInList


def mbfPllPeakFind(name, input_range, step=5):
    """
    name          <EPICS device>:<axis>
    input_range   phase input_range in degree to search around current target phase
    step          step in degree, default is 5 degrees
    """
    start = caGet(''.join((name, ':PLL:CTRL:TARGET_S')))
    phase = range(start - input_range, start + input_range, step)
    phase.extend(range(start + input_range, start - input_range, -step))
    mag = []
    iq = []
    f = []
    for n in range(len(phase)):
        # the funny mod is required to get into the right input_range of -180 to +179
        caPut(''.join((name, ':PLL:CTRL:TARGET_S')),
              numpy.mod(phase[n] + 180, 360) - 180)
        # This sleep will depend on the dwell time and PLL config,
        # but works with the default
        sleep(.2)
        mag.append(caGet(''.join((name, ':PLL:FILT:MAG'))))  # get magnitude
        iq.append(complex(caGet(''.join((name, ':PLL:FILT:I'))),
                          caGet(''.join((name, ':PLL:FILT:Q')))))
        f.append(caGet(''.join((name, ':PLL:NCO:FREQ'))))

    mi = max(abs(mag))
    ind = findPositionInList(mag, mi)
    peak = numpy.degrees(cmath.phase(iq[ind]))

    status = caGet(''.join((name, ':PLL:CTRL:STATUS')))
    if status == 'Running':
        caPut(''.join((name, ':PLL:CTRL:TARGET_S')), numpy.mod(peak + 180, 360) - 180)
        print(''.join((name, ':PLL:CTRL:TARGET_S set to ',
                       numpy.mod(peak + 180, 360) - 180)))
    else:
        raise ValueError(''.join(('PLL stopped during phase sweep, ',
                                  'please restart using mbf_pll_start')))

    return iq, f, phase