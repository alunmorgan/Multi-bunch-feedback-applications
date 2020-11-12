from time import sleep

import numpy # type: ignore
from cothread.catools import caget, caput # type: ignore


def mbf_pll_start(name, pllbunches, guardbunches=2):
    """
    name          <EPICS device>:<axis>
    pllbunches    bunches numbers to use for PLL (0-935)
    guardbunches  number of bunches around PLL to also take out of sweeper
                (defaults to 2)
    """

    # initialise pll pattern
    pllpattern = numpy.zeros((1, 936), dtype=bool)
    pllpattern[pllbunches] = True

    # now we want to create a pattern with a little more room around the
    # pll bunches. It's a little tricky with a general pattern, and the cirular
    # nature the pattern, so I use circshift in a loop

    guardpattern = numpy.ones((1, 936), dtype=bool)
    for n in range(-guardbunches, guardbunches):
        guardpattern[numpy.roll(pllpattern, n)] = False

    # Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps),
    # and in PLL detector.

    caput("".join((name, ":BUN:0:PLL:ENABLE_S")), pllpattern)
    caput("".join((name, ":BUN:1:PLL:ENABLE_S")), pllpattern)
    caput("".join((name, ":PLL:DET:BUNCHES_S")), pllpattern)

    # Set sweep (SEQ) and its detector (#1) to NOT operate on these and
    # guard bunches around, ie only on guardpattern. This is maybe a little
    # keen, as there might be other things configured, which this will jjst
    # plow over. Maybe we should check or add to any previous config...

    caput("".join((name, ":BUN:1:SEQ:ENABLE_S")), guardpattern)
    caput("".join((name, ":DET:0:BUNCHES_S")), guardpattern)

    # Now comes some setup with 'working values'. These ought to be read from a
    # config file or be additinal arguments in the future.

    caput("".join((name, ":PLL:DET:SELECT_S")), "ADC no fill")
    caput("".join((name, ":ADC:REJECT_COUNT_S")), "128 turns")
    caput("".join((name, ":PLL:DET:SCALING_S")), "48dB")
    caput("".join((name, ":PLL:DET:BLANKING_S")), "Blanking")
    caput("".join((name, ":PLL:DET:DWELL_S")), 128)

    caput("".join((name, ":PLL:CTRL:KI_S")), 1000)
    caput("".join((name, ":PLL:CTRL:KP_S")), 0)
    caput("".join((name, ":PLL:CTRL:MIN_MAG_S")), 0)
    caput("".join((name, ":PLL:CTRL:MAX_OFFSET_S")), 0.02)
    caput("".join((name, ":PLL:CTRL:TARGET_S")), -180)

    # starting frequency is taken form swept tune measurement, but could also
    # be configured from config file (but then it will only work if tune
    # feedback has brought the tune to the desired value...)

    tune = caget("".join((name, ":TUNE:CENTRE:TUNE")), 1, "double")
    if numpy.isnan(tune):
        raise ValueError("Tune fit invalid, cannot start PLL.")
        # tune=37.45

    caput("".join((name, ":PLL:NCO:GAIN_DB_S")), -30)
    caput("".join((name, ":PLL:NCO:FREQ_S")), tune)
    caput("".join((name, ":PLL:NCO:ENABLE_S")), "On")

    # finally, lets start, and then check whether we're still running after 1
    # second

    caput("".join((name, ":PLL:CTRL:START_S.PROC")), 0)
    sleep(1)
    status = caget("".join((name, ":PLL:CTRL:STATUS")))
    print("".join(("PLL is: ", status)))
