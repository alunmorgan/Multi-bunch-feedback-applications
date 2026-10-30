import numpy as np

from Common import (
    get_variable,
    mbf_system_config,
    set_variable,
)


def setup_feedback_for_bunch_train(mbf_axis, train_length, clear_previous="yes"):
    # This allows the setup of the MBF to be adjusted to be suitable for the
    # different bunch train lengths[''] The feedback will ignore anything not in the
    # bunch train
    # Inputs:
    #        mbf_axis (str): axis to apply the settings to[''] ('x' or 'y')
    #        train_length (int): length of train to apply tune measurement and
    #                            feedback to[''] Starts from first bunch as per the
    #                            master timing generator['']
    #        clear_previous(str): if yes removes existing enable patterns['']
    #                            Defaults to yes['']
    #
    # Example: setup_for_bunch_train('x', 686)

    [_1, harmonic_number, pv_names] = mbf_system_config()
    pv_head = pv_names["hardware_names"][mbf_axis]
    # feedback during quiecent mode
    feedback0 = pv_names["tails"]["Bunch_bank"]["bank0"]["FIR"]["enablewf"]
    # feedback during tune measurement
    feedback1 = pv_names["tails"]["Bunch_bank"]["bank1"]["FIR"]["enablewf"]

    if clear_previous.lower() == "yes":
        enable_feedback0 = np.zeros(harmonic_number)
        enable_feedback1 = np.zeros(harmonic_number)
    else:
        enable_feedback0 = get_variable(f"{pv_head}{feedback0}")
        enable_feedback1 = get_variable(f"{pv_head}{feedback1}")

    for js in range(train_length):
        enable_feedback0[js] = 1
        enable_feedback1[js] = 1

    # Apply changes
    set_variable(f"{pv_head}{feedback0}", enable_feedback0)
    set_variable(f"{pv_head}{feedback1}", enable_feedback1)


def setup_tune_bunch_selection(
    mbf_axis, start_bunch=1, step_bunch=1, n_bunch="all", clear_previous="yes"
):
    # This allows the setup of the tune to be adjusted from using all bunches to
    # using a subset[''] This is useful if the tune measurement is struggling due to
    # distortion of the IQ plot[''] Defaults to all bunches['']
    # Inputs:
    #       mbf_axis (str): axis to apply the settings to[''] ('x' or 'y')
    #       start_bunch(int): The first position to take the tune measurement['']
    #       step_bunch(int): The spacing of measurement positions['']
    #       n_bunch(int): How many positions are used['']
    #       clear_previous(str): if yes removes existing enable patterns['']
    #                            Defaults to yes['']
    #
    # Example: setup_tune_bunch_selection('x', 40, 90, 10)
    [_1, harmonic_number, pv_names] = mbf_system_config
    if n_bunch == "all":
        n_bunch = harmonic_number

    pv_head = pv_names["hardware_names"][mbf_axis]
    # tune measurement
    detector0 = pv_names["tails"]["Detector"]["det0"]["bunch_selection"]
    # tune excitation
    sequencer1 = pv_names["tails"]["Bunch_bank"]["bank1"]["SEQ"]["enablewf"]

    if clear_previous == "yes":
        det_enable_wfm = np.zeros(harmonic_number)
        seq_enable_wfm = np.zeros(harmonic_number)
    else:
        det_enable_wfm = get_variable([pv_head, detector0])
        seq_enable_wfm = get_variable([pv_head, sequencer1])

    for js in range(n_bunch):
        det_enable_wfm[start_bunch + (js - 1) * step_bunch] = 1
        seq_enable_wfm[start_bunch + (js - 1) * step_bunch] = 1

    # Apply changes
    set_variable(f"{pv_head}{detector0}", det_enable_wfm)
    set_variable(f"{pv_head}{sequencer1}", seq_enable_wfm)
