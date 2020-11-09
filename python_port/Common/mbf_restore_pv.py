from common import mbfSystemConfig
import os
from cothread.catools import caPut
from scipy.io import loadmat


def mbfRestorePv(pv_name):
    """ Finds the file corresponding to the pv_name. Loads this file and sets the
    PV to the value in the file.

    Args:
        pv_name (str): name of the requested process variable.

    Example: mbf_restore_pv('SR-DI-MBF-TRIG-01')
    """

    root_string, _1, _2, _3 = mbfSystemConfig()
    root_string = root_string[0]
    original_value = loadmat(os.path.join(root_string, 'captured_config', pv_name))
    caPut(pv_name[0:-4], original_value)
