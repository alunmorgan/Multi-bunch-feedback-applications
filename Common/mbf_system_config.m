function [root_path, harmonic_number, pv_names, trigger_inputs] = mbf_system_config

%       harmonic_number (int): Harmonic number of the machine.

% The first entry in root_path is the currently used location for capture. 
% Additional locations are for alternative archival locations only.
root_path = {'/dls/ops-data/Diagnostics/MBF/', ...
             '/dls/ops-data/Diagnostics/TMBF/', ...
             '/dls/ops-data/Diagnostics/LMBF/'};
harmonic_number = 936;

% Base PVs of the hardware.
pv_names.hardware_names.x = 'SR23C-DI-TMBF-01:X';
pv_names.hardware_names.y = 'SR23C-DI-TMBF-01:Y';
pv_names.hardware_names.s = 'SR23C-DI-LMBF-01:IQ';
pv_names.hardware_names.t = 'TS-DI-TMBF-01'; % test system

% External trigger
pv_names.Hardware_trigger = 'LI-TI-MTGEN-01:BS-DI-MODE';

% Emittance measurement
pv_names.emittance = 'SR-DI-EMIT-01:ESPREAD_MEAN';

% Trigger settings
trigger_inputs = {'SOFT', 'EXT', 'PM', 'ADC0', 'ADC1', 'SEQ0', 'SEQ1'};
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    pv_names.tails.triggers.(trigger).enable_status = [':TRG:SEQ:',trigger,':EN_S'];
    pv_names.tails.triggers.(trigger).blanking_status = [':TRG:SEQ:',trigger,':BL_S'];
end
pv_names.tails.triggers.SEQ.arm = ':TRG:SEQ:ARM_S.PROC';
pv_names.tails.triggers.SEQ.disarm = ':TRG:SEQ:DISARM_S.PROC';
pv_names.tails.triggers.SEQ.mode = ':TRG:SEQ:MODE_S';
pv_names.tails.triggers.SEQ.delay = ':TRG:SEQ:DELAY_S';
% shared with other axis
pv_names.tails.trigger.mem_arm = ':TRG:MEM:ARM_S.PROC'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.trigger.mem_disarm = ':TRG:MEM:DISARM_S.PROC'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.soft = ':TRG:SOFT_S.PROC';  % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.soft_settings = ':TRG:SOFT_S.SCAN';  % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.shared = ':TRG:MODE_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.blanking_length = ':TRG:BLANKING_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.

% Super Sequencer settings
pv_names.tails.Super_sequencer_count = ':SEQ:SUPER:COUNT_S';

% Sequencer settings
pv_names.tails.Sequencer.start_state = ':SEQ:PC_S';
pv_names.tails.Sequencer.steady_state_bank = ':SEQ:0:BANK_S';
pv_names.tails.Sequencer.Base = ':SEQ:';
pv_names.tails.Sequencer.start_frequency = ':START_FREQ_S';
pv_names.tails.Sequencer.count = ':COUNT_S';
pv_names.tails.Sequencer.dwell = ':DWELL_S';
pv_names.tails.Sequencer.gain = ':GAIN_S';
pv_names.tails.Sequencer.enable = ':ENABLE_S';
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
% applies to all
pv_names.tails.Detector.source = ':DET:SELECT_S';
pv_names.tails.Detector.fill_waveforms = ':DET:FILL_WAVEFORMS_S';
pv_names.tails.Detector.fir_delay = ':DET:FIR_DELAY_S';
for n_det = 0:3
    l_det = ['det',num2str(n_det)];
    n_det_label = num2str(n_det);
    pv_names.tails.Detector.(l_det).enable = [':DET:',n_det_label,':ENABLE_S'];
    pv_names.tails.Detector.(l_det).bunch_selection = [':DET:',n_det_label,':BUNCHES_S']; % How do you set all?
    pv_names.tails.Detector.(l_det).scale = [':DET:',n_det_label,':SCALING_S']; % gain?
    pv_names.tails.Detector.(l_det).I = [':DET:',n_det_label,':I'];
    pv_names.tails.Detector.(l_det).Q = [':DET:',n_det_label,':Q'];
end %for

% Memory settings
pv_names.tails.MEM_status = ':MEM:BUSY';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.channel_select = ':MEM:SELECT_S';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.offset = ':MEM:OFFSET_S';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.runout = ':MEM:RUNOUT_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.


% % NCO settings
pv_names.tails.NCO.Base = ':NCO';
pv_names.tails.NCO.frequency = ':FREQ_S';
pv_names.tails.NCO.gain = ':GAIN_S';
pv_names.tails.NCO.enable = ':ENABLE_S';

% FIR settings
pv_names.tails.FIR.Base = ':FIR:';
pv_names.tails.FIR.gain = 'GAIN_S';
pv_names.tails.FIR.method_of_construction = ':USEWF_S';

% Tune settings
pv_names.tails.tune.peak.left_area = ':PEAK:LEFT:AREA';
pv_names.tails.tune.peak.right_area = ':PEAK:RIGHT:AREA';
pv_names.tails.tune.peak.centre_area = ':PEAK:CENTRE:AREA';
pv_names.tails.tune.peak.sync_tune = ':PEAK:SYNCTUNE';

