from Common import mbfSystemConfig, mbfGetThenPut


def mbfSetState(ax, state, tune, bank, gain, enable, duration, dwell, capture):
    """Setup an individual state in the super sequencer.

    Args:
        ax (str)      : 'x', 'y', or 's' axis
        state (int)   : state number in the sequencer.
        tune (float)  : Tune of the machine.
        bank (int)    : The bunch bank used for this state.
        gain (str)    : the excitation level.
        duration (int): the number of turns the state is active.
        dwell (int)   : Dwell time (turns).
        capture (str) : 'Capture' or 'Discard' depending onn if you want to
                        keep the data or not

    Example: mbf_set_state(ax, state, tune, bank, gain, duration, dwell,
                           capture)
    """
    _1, _2, pv_names, _3 = mbfSystemConfig()

    Sequencer = pv_names["tails"]["Sequencer"]
    pv_head = "".join((pv_names["hardware_names"][ax], Sequencer["Base"], state))

    mbfGetThenPut("".join((pv_head, Sequencer["start_frequency"])), tune)
    mbfGetThenPut("".join((pv_head, Sequencer["step_frequency"])), 0)
    mbfGetThenPut("".join((pv_head, Sequencer["count"])), duration)
    mbfGetThenPut("".join((pv_head, Sequencer["holdoff"])), 0)
    mbfGetThenPut("".join((pv_head, Sequencer["dwell"])), dwell)
    mbfGetThenPut(
        "".join((pv_head, Sequencer["bank_select"])), "".join(("Bank ", bank))
    )
    mbfGetThenPut("".join((pv_head, Sequencer["capture_state"])), capture)
    mbfGetThenPut("".join((pv_head, Sequencer["windowing_state"])), "Disabled")
    mbfGetThenPut("".join((pv_head, Sequencer["gain"])), gain)
    mbfGetThenPut("".join((pv_head, Sequencer["blanking_state"])), "Off")
    mbfGetThenPut("".join((pv_head, Sequencer["enable"])), enable)
