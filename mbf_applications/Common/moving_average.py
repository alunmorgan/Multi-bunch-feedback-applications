import numpy as np # type: ignore


def movingAverage(a, n=3):
    """
    Args:
     a(array): input data
     n(int): length of averaging window
    Returns:
     An array containing the moving average.
     This changes size with changing window size.
    """
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1 :] / n
