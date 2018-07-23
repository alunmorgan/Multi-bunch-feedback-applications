function [root_path, harmonic_number, pv_names] = mbf_system_config

%       harmonic_number (int): Harmonic number of the machine.

% The first entry in root_path is the currently used location for capture. 
% Additional locations are for alternative archival locations only.
root_path = {'/dls/ops-data/Diagnostics/MBF/', ...
             '/dls/ops-data/Diagnostics/TMBF/', ...
             '/dls/ops-data/Diagnostics/LMBF/'};
harmonic_number = 936;

% External trigger
pv_names.Hardware_trigger = 'LI-TI-MTGEN-01:BS-DI-MODE';

% Emittance measurement
pv_names.emittance = 'SR-DI-EMIT-01:ESPREAD_MEAN';

% Trigger settings
pv_names.tails.MEM_trigger_select = ':TRG:MEM:SEL_S';
pv_names.tails.MEM_trigger_mode = ':TRG:MEM:MODE_S';
pv_names.tails.Sequencer_trigger_select = ':TRG:SEQ:SEL_S';
pv_names.tails.MEM_external_trigger_enable_status = ':TRG:MEM:EXT:EN_S';
pv_names.tails.MEM_post_mortem_trigger_enable_status = ':TRG:MEM:PM:EN_S';
pv_names.tails.MEM_ADC_trigger_enable_status = ':TRG:MEM:ADC:EN_S';
pv_names.tails.MEM_sequencer_trigger_enable_status = ':TRG:MEM:SEQ:EN_S';
pv_names.tails.MEM_system_clock_trigger_enable_status = ':TRG:MEM:SCLK:EN_S';
pv_names.tails.MEM_external_trigger_blanking_status = ':TRG:MEM:EXT:BL_S';
pv_names.tails.MEM_post_mortem_trigger_blanking_status   = ':TRG:MEM:PM:BL_S';
pv_names.tails.MEM_ADC_trigger_blanking_status = ':TRG:MEM:ADC:BL_S';
pv_names.tails.MEM_sequencer_trigger_blanking_status = ':TRG:MEM:SEQ:BL_S';
pv_names.tails.MEM_system_clock_trigger_blanking_status = ':TRG:MEM:SCLK:BL_S';

% Super Sequencer settings
pv_names.tails.Super_sequencer_count = ':SEQ:SUPER:COUNT_S';

% Sequencer settings
pv_names.tails.Sequencer_trigger_state = ''; %????? was ':SEQ:TRIGGER_S';
pv_names.tails.Sequencer_start_state = ':SEQ:PC_S';
pv_names.tails.Sequencer_steady_state_bank = ':SEQ:0:BANK_S';
pv_names.tails.Sequencer.Base = ':SEQ:';
pv_names.tails.Sequencer.start_frequency = ':START_FREQ_S';
pv_names.tails.Sequencer.count = ':COUNT_S';
pv_names.tails.Sequencer.dwell = ':DWELL_S';
pv_names.tails.Sequencer.gain = ':GAIN_S';
pv_names.tails.Sequencer.step_frequency = ':STEP_FREQ_S';
pv_names.tails.Sequencer.holdoff = ':HOLDOFF_S';
pv_names.tails.Sequencer.bank_select = ':BANK_S';
pv_names.tails.Sequencer.capture_state = ':CAPTURE_S';
pv_names.tails.Sequencer.windowing_state = ':ENWIN_S';
pv_names.tails.Sequencer.blanking_state = ':BLANK_S';

pv_names.tails.Bunch_bank.Base = ':BUN:';
pv_names.tails.Bunch_bank.Gains = ':GAINWF_S';
pv_names.tails.Bunch_bank.Output_types = ':OUTWF_S';
pv_names.tails.Bunch_bank.FIR_select = ':FIRWF_S';

% Detector settings
% NOW HAVE FOUR SEPARATE DETECTORS
% pv_names.tails.Detector1.gain = ':DET:GAIN_S';
% pv_names.tails.Detector1.mode = ':DET:MODE_S';
% pv_names.tails.Detector1.autogain_state = ':DET:AUTOGAIN_S';
% pv_names.tails.Detector1.input = ':DET:INPUT_S';
% pv_names.tails.Detector.1scale = ':DET:SCALE';
% pv_names.tails.Detector1.I = ':DET:I:M';
% pv_names.tails.Detector1.Q = ':DET:Q:M';

% Memory settings
pv_names.tails.MEM_arm = ':TRG:MEM:ARM_S.PROC';
pv_names.tails.MEM_status = ':MEM:STATUS';
pv_names.tails.MEM_buffer = ':MEM:LONGWF';
pv_names.tails.MEM_input = ':MEM:INPUT_S';
pv_names.tails.MEM_IQ_overflow = ':MEM:OVF:IQ';
pv_names.tails.MEM_IQ_mode = ':MEM:IQMODE_S';
pv_names.tails.MEM_autostop_setting = ':MEM:AUTOSTOP_S';

% Buffer settings
% THERE IS NO BUFFER ANY MORE.
% pv_names.tails.Buffer_trigger_mode = ':TRG:BUF:MODE_S';
% pv_names.tails.Buffer_trigger_stop = ':TRG:BUF:RESET_S.PROC';

% % NCO settings
% NOT IMPLEMENTED ON THE NEW HARDWARE YET.
% pv_names.tails.NCO.Base = ':NCO';
% pv_names.tails.NCO.frequency = ':FREQ_S';
% pv_names.tails.NCO.gain = ':GAIN_S';

% FIR settings
pv_names.tails.FIR.Base = ':FIR:';
pv_names.tails.FIR.gain = 'GAIN_S';
pv_names.tails.FIR.method_of_construction = ':USEWF_S';

% Tune settings
pv_names.tails.tune.peak.left_area = ':PEAK:LEFT:AREA';
pv_names.tails.tune.peak.right_area = ':PEAK:RIGHT:AREA';
pv_names.tails.tune.peak.centre_area = ':PEAK:CENTRE:AREA';
pv_names.tails.tune.peak.sync_tune = ':PEAK:SYNCTUNE';

