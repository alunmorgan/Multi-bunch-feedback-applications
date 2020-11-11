from cothread.catools import caGet, caPut
from Common import mbfSystemConfig
import os
from scipy.io import savemat


def mbfGetThenPut(pv_name, new_value):
    """retrieves the value before the caPut and then
        write the new value to the PV.
    Example: mbf_get_then_put(pv_name, new_value)
    """

    root_string, _1, _2, _3 = mbfSystemConfig()
    root_string = root_string[0]

    for hse in range(len(pv_name)):
        original_value = caGet(pv_name[hse])
        caPut(pv_name, new_value)
        savemat(
            os.path.join((root_string, "captured_config", pv_name[hse])), original_value
        )
