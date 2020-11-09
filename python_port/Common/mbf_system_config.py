def mbfSystemConfig():

    #       harmonic_number (int): Harmonic number of the machine.

    # The first entry in root_path is the currently used location for capture.
    # Additional locations are for alternative archival locations only.
    root_path = [
        "/dls/ops-data/Diagnostics/MBF/",
        "/dls/ops-data/Diagnostics/TMBF/",
        "/dls/ops-data/Diagnostics/LMBF/",
    ]
    harmonic_number = 936
    pv_names = {}
    # Base PVs of the hardware.
    pv_names["hardware_names"] = {}
    pv_names["hardware_names"]["T"] = "SR23C-DI-TMBF-01"
    pv_names["hardware_names"]["L"] = "SR23C-DI-LMBF-01"
    pv_names["hardware_names"]["x"] = "".join((pv_names["hardware_names"]["T"], ":X"))
    pv_names["hardware_names"]["y"] = "".join((pv_names["hardware_names"]["T"], ":Y"))
    pv_names["hardware_names"]["s"] = "".join((pv_names["hardware_names"]["L"], ":IQ"))
    pv_names["hardware_names"]["lab"] = "TS-DI-TMBF-02"
    pv_names["hardware_names"]["tx"] = "".join(
        (pv_names["hardware_names"]["lab"], ":X")
    )  # test system
    pv_names["hardware_names"]["ty"] = "".join(
        (pv_names["hardware_names"]["lab"], ":Y")
    )  # test system

    # External trigger
    pv_names["Hardware_trigger"] = "LI-TI-MTGEN-01:BS-DI-MODE"

    # Emittance measurement
    pv_names["emittance"] = "SR-DI-EMIT-01:ESPREAD_MEAN"

    # Trigger settings
    trigger_inputs = ["SOFT", "EXT", "PM", "ADC0", "ADC1", "SEQ0", "SEQ1"]
    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        pv_names["tails"]["triggers"]["(trigger)"]["enable_status"] = "".join(
            (":TRG:SEQ:", trigger, ":EN_S")
        )
        pv_names["tails"]["triggers"]["(trigger)"]["blanking_status"] = "".join(
            (":TRG:SEQ:", trigger, ":BL_S")
        )

    pv_names["tails"]["triggers"]["SEQ"]["arm"] = ":TRG:SEQ:ARM_S.PROC"
    pv_names["tails"]["triggers"]["SEQ"]["disarm"] = ":TRG:SEQ:DISARM_S.PROC"
    pv_names["tails"]["triggers"]["SEQ"]["mode"] = ":TRG:SEQ:MODE_S"
    pv_names["tails"]["triggers"]["SEQ"]["delay"] = ":TRG:SEQ:DELAY_S"
    # shared with other axis
    # NEED TO TAKE OFF THE X|Y BEFORE USE. in this section
    pv_names["tails"]["triggers"]["MEM"]["arm"] = ":TRG:MEM:ARM_S.PROC"
    pv_names["tails"]["triggers"]["MEM"]["disarm"] = ":TRG:MEM:DISARM_S.PROC"
    pv_names["tails"]["triggers"]["MEM"]["mode"] = ":TRG:MEM:MODE_S"
    pv_names["tails"]["triggers"]["MEM"]["delay"] = ":TRG:MEM:DELAY_S"
    pv_names["tails"]["triggers"]["soft"] = ":TRG:SOFT_S.PROC"
    pv_names["tails"]["triggers"]["soft_settings"] = ":TRG:SOFT_S.SCAN"
    pv_names["tails"]["triggers"]["shared"] = ":TRG:MODE_S"
    pv_names["tails"]["triggers"]["blanking_length"] = ":TRG:BLANKING_S"
    # section ends
    for trigger_ind in range(1, len(trigger_inputs)):
        trigger = trigger_inputs[trigger_ind]
        pv_names["tails"]["triggers"]["MEM"]["(trigger)"]["enable_status"] = "".join(
            (":TRG:MEM:", trigger, ":EN_S")
        )
        pv_names["tails"]["triggers"]["MEM"]["(trigger)"]["blanking_status"] = "".join(
            (":TRG:MEM:", trigger, ":BL_S")
        )

    # Super Sequencer settings
    pv_names["tails"]["Super_sequencer_count"] = ":SEQ:SUPER:COUNT_S"

    # Sequencer settings
    pv_names["tails"]["Sequencer"]["start_state"] = ":SEQ:PC_S"
    pv_names["tails"]["Sequencer"]["steady_state_bank"] = ":SEQ:0:BANK_S"
    pv_names["tails"]["Sequencer"]["Base"] = ":SEQ:"
    pv_names["tails"]["Sequencer"]["start_frequency"] = ":START_FREQ_S"
    pv_names["tails"]["Sequencer"]["count"] = ":COUNT_S"
    pv_names["tails"]["Sequencer"]["dwell"] = ":DWELL_S"
    pv_names["tails"]["Sequencer"]["gain"] = ":GAIN_S"
    pv_names["tails"]["Sequencer"]["enable"] = ":ENABLE_S"
    pv_names["tails"]["Sequencer"]["step_frequency"] = ":STEP_FREQ_S"
    pv_names["tails"]["Sequencer"]["holdoff"] = ":HOLDOFF_S"
    pv_names["tails"]["Sequencer"]["bank_select"] = ":BANK_S"
    pv_names["tails"]["Sequencer"]["capture_state"] = ":CAPTURE_S"
    pv_names["tails"]["Sequencer"]["windowing_state"] = ":ENWIN_S"
    pv_names["tails"]["Sequencer"]["blanking_state"] = ":BLANK_S"

    pv_names["tails"]["Bunch_bank"]["Base"] = ":BUN:"
    pv_names["tails"]["Bunch_bank"]["Gains"] = ":GAINWF_S"
    pv_names["tails"]["Bunch_bank"]["Output_types"] = ":OUTWF_S"
    pv_names["tails"]["Bunch_bank"]["FIR_select"] = ":FIRWF_S"
    pv_names["tails"]["Bunch_bank"]["FIR_enable"] = ":FIR:SET_ENABLE_S"
    pv_names["tails"]["Bunch_bank"]["NCO1_enable"] = ":NCO1:SET_ENABLE_S"
    pv_names["tails"]["Bunch_bank"]["NCO2_enable"] = ":NCO2:SET_ENABLE_S"
    pv_names["tails"]["Bunch_bank"]["SEQ_enable"] = ":SEQ:SET_ENABLE_S"
    pv_names["tails"]["Bunch_bank"]["PLL_enable"] = ":PLL:SET_ENABLE_S"
    pv_names["tails"]["Bunch_bank"]["FIR_disable"] = ":FIR:SET_DISABLE_S"
    pv_names["tails"]["Bunch_bank"]["NCO1_disable"] = ":NCO1:SET_DISABLE_S"
    pv_names["tails"]["Bunch_bank"]["NCO2_disable"] = ":NCO2:SET_DISABLE_S"
    pv_names["tails"]["Bunch_bank"]["SEQ_disable"] = ":SEQ:SET_DISABLE_S"
    pv_names["tails"]["Bunch_bank"]["PLL_disable"] = ":PLL:SET_DISABLE_S"
    pv_names["tails"]["Bunch_bank"]["FIR_gains"] = ":FIR:GAIN_S"
    pv_names["tails"]["Bunch_bank"]["NCO1_gains"] = ":NCO1:GAIN_S"
    pv_names["tails"]["Bunch_bank"]["NCO2_gains"] = ":NCO2:GAIN_S"
    pv_names["tails"]["Bunch_bank"]["SEQ_gains"] = ":SEQ:GAIN_S"
    pv_names["tails"]["Bunch_bank"]["PLL_gains"] = ":PLL:GAIN_S"

    # Detector settings
    # applies to all
    pv_names["tails"]["Detector"]["source"] = ":DET:SELECT_S"
    pv_names["tails"]["Detector"]["fill_waveforms"] = ":DET:FILL_WAVEFORMS_S"
    pv_names["tails"]["Detector"]["fir_delay"] = ":DET:FIR_DELAY_S"
    for n_det in range(4):
        l_det = "".join(("det", n_det))
        pv_names["tails"]["Detector"][l_det]["enable"] = "".join(
            (":DET:", n_det, ":ENABLE_S")
        )
        pv_names["tails"]["Detector"][l_det]["bunch_selection"] = "".join(
            (":DET:", n_det, ":BUNCHES_S")
        )  # How do you set all?
        pv_names["tails"]["Detector"][l_det]["scale"] = "".join(
            (":DET:", n_det, ":SCALING_S")
        )  # gain?
        pv_names["tails"]["Detector"][l_det]["I"] = "".join((":DET:", n_det, ":I"))
        pv_names["tails"]["Detector"][l_det]["Q"] = "".join((":DET:", n_det, ":Q"))

    # Memory settings
    # NEED TO TAKE OFF THE X|Y BEFORE USE. in this section
    pv_names["tails"]["MEM.status"] = ":MEM:BUSY"
    pv_names["tails"]["MEM.channel_select"] = ":MEM:SELECT_S"
    pv_names["tails"]["MEM.offset"] = ":MEM:OFFSET_S"
    pv_names["tails"]["MEM.runout"] = ":MEM:RUNOUT_S"
    # section ends
    pv_names["tails"]["TRG.memory_status"] = ":TRG:MEM:STATUS"

    # # NCO settings
    pv_names["tails"]["NCO"]["Base"] = ":NCO"
    pv_names["tails"]["NCO"]["frequency"] = ":FREQ_S"
    pv_names["tails"]["NCO"]["gain"] = ":GAIN_S"
    pv_names["tails"]["NCO"]["enable"] = ":ENABLE_S"

    # FIR settings
    pv_names["tails"]["FIR"]["Base"] = ":FIR:"
    pv_names["tails"]["FIR"]["gain"] = "GAIN_S"
    pv_names["tails"]["FIR"]["method_of_construction"] = ":USEWF_S"

    # Tune settings
    pv_names["tails"]["tune"]["peak"]["left_area"] = ":PEAK:LEFT:AREA"
    pv_names["tails"]["tune"]["peak"]["right_area"] = ":PEAK:RIGHT:AREA"
    pv_names["tails"]["tune"]["peak"]["centre_area"] = ":PEAK:CENTRE:AREA"
    pv_names["tails"]["tune"]["peak"]["sync_tune"] = ":PEAK:SYNCTUNE"

    return root_path, harmonic_number, pv_names, trigger_inputs
