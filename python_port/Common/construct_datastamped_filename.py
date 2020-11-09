from math import round


def constructDatastampedFilename(name_str, c):
    """Constructs a datestamped filename
     name_str is a identifier string added at the begining of the name.
     c is a time vector such as generated by the clock function.

    Example: name = construct_filename('MBF', clock)
    """
    yr = c[0]
    mth = c[1]
    dy = c[2]
    hr = c[3]
    mn = c[4]
    sec = round(c[5])

    if mnt < 10:
        mth = ''.join(('0', mth))

    if dy < 10:
        dy = ''.join(('0', dy))

    if hr < 10:
        hr = ''.join(('0', hr))

    if mn < 10:
        mn = ''.join(('0', mn))

    if sec < 10:
        sec = ''.join(('0', sec)

    return ''.join((name_str, '_', dy, '_', mth, '_', yr, '_',
                    hr, '-', mn, '-', sec))
