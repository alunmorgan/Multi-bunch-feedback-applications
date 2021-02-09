import os

from cothread.catools import caget, caput  # type: ignore
from scipy.io import savemat  # type: ignore

from mbf_applications.Common.mbf_system_config import mbfSystemConfig


def mbfGetThenPut(pv_name, new_value):
    """retrieves the value before the caput and then
        write the new value to the PV.
    Example: mbf_get_then_put(pv_name, new_value)
    """

    root_string, _1, _2, _3 = mbfSystemConfig()
    root_string = root_string[0]

    for hse in range(len(pv_name)):
        original_value = caget(pv_name[hse])
        caput(pv_name, new_value)
        savemat(
            os.path.join((root_string, "captured_config", pv_name[hse])), original_value
        )
