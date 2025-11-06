function [root_path, harmonic_number, pv_names, trigger_inputs] = mbf_system_config

%       harmonic_number (int): Harmonic number of the machine.

% The first entry in root_path is the currently used location for capture.
% Additional locations are for alternative archival locations only.
root_path = {'/dls/ops-data/Diagnostics/MBF/', ...
    '/dls/ops-data/Diagnostics/TMBF/', ...
    '/dls/ops-data/Diagnostics/LMBF/'};
harmonic_number = 936;

%% RF frequency
pv_names.RF = 'SR-CS-RFFB-01:TARGET';

%% Beam current
pv_names.current = 'SR-DI-DCCT-01:SIGNAL';

%% Bunch pattern
pv_names.bunch_pattern = 'SR-DI-PICO-01:BUCKETS_180';

%% Topup countdown
pv_names.topup.countdown = 'SR-CS-FILL-01:COUNTDOWN';

%% DORIS PVs
pv_names.doris.phase = 'SR23C-DI-DORIS-01:TARGET_S';

%% Frontend PVs
pv_names.frontend.base = 'SR23C-DI-BBFE-01';
pv_names.frontend.system_phase.x = ':PHA:OFF:X';
pv_names.frontend.system_phase.y = ':PHA:OFF:Y';
pv_names.frontend.system_phase.sI = ':PHA:OFF:IT';
pv_names.frontend.system_phase.sQ = ':PHA:OFF:IL';
pv_names.frontend.clock_phase.x = ':PHA:CLO:3';
pv_names.frontend.clock_phase.y = ':PHA:CLO:3';
pv_names.frontend.clock_phase.s = ':PHA:CLO:4';

%% Backend PVs
% Base PVs of the hardware.
pv_names.hardware_names.T = 'SR23C-DI-TMBF-01';
pv_names.hardware_names.L = 'SR23C-DI-LMBF-01';
pv_names.hardware_names.mem.x = pv_names.hardware_names.T;
pv_names.hardware_names.mem.y = pv_names.hardware_names.T;
pv_names.hardware_names.mem.s = pv_names.hardware_names.L;
pv_names.hardware_names.x = [pv_names.hardware_names.T, ':X'];
pv_names.hardware_names.y = [pv_names.hardware_names.T, ':Y'];
pv_names.hardware_names.s = [pv_names.hardware_names.L, ':IQ'];
pv_names.hardware_names.lab = 'TS-DI-TMBF-02';
pv_names.hardware_names.mem.tx = pv_names.hardware_names.lab; % test system
pv_names.hardware_names.mem.ty = pv_names.hardware_names.lab; % test system
pv_names.hardware_names.tx = [pv_names.hardware_names.lab, ':X']; % test system
pv_names.hardware_names.ty = [pv_names.hardware_names.lab, ':Y']; % test system

%% External trigger
pv_names.Hardware_trigger = 'LI-TI-MTGEN-01:BS-DI-MODE';

%% Pinhole PVs
pv_names.pinhole1 = 'SR01C-DI-DCAM-04';
pv_names.pinhole2 = 'SR01C-DI-DCAM-05';

%% Emittance measurement
pv_names.emittance.status = 'SR-DI-EMIT-01:STATUS';
pv_names.emittance.x.val = 'SR-DI-EMIT-01:HEMIT';
pv_names.emittance.x.mean = 'SR-DI-EMIT-01:HEMIT_MEAN';
pv_names.emittance.x.error = 'SR-DI-EMIT-01:HERROR';
pv_names.energy_spread.val = 'SR-DI-EMIT-01:ESPREAD';
pv_names.energy_spread.mean = 'SR-DI-EMIT-01:X:ESPREAD_MEAN';
pv_names.emittance.y.val = 'SR-DI-EMIT-01:VEMIT';
pv_names.emittance.y.mean = 'SR-DI-EMIT-01:VEMIT_MEAN';
pv_names.emittance.y.error = 'SR-DI-EMIT-01:VERROR';
pv_names.coupling.val = 'SR-DI-EMIT-01:COUPLING';
pv_names.coupling.mean = 'SR-DI-EMIT-01:COUPLING_MEAN';
pv_names.beam_size.pinhole1.sigmax = 'SR-DI-EMIT-01:P1:SIGMAX';
pv_names.beam_size.pinhole1.sigmay = 'SR-DI-EMIT-01:P1:SIGMAY';
pv_names.beam_size.pinhole2.sigmax = 'SR-DI-EMIT-01:P2:SIGMAX';
pv_names.beam_size.pinhole2.sigmay = 'SR-DI-EMIT-01:P2:SIGMAY';

%% Trigger settings
pv_names.tails.triggers.mode = ':TRG:SEQ:MODE_S';
pv_names.tails.triggers.arm = ':TRG:SEQ:ARM_S.PROC';
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
pv_names.tails.triggers.MEM.arm = ':TRG:MEM:ARM_S.PROC'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.MEM.disarm = ':TRG:MEM:DISARM_S.PROC'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.MEM.mode = ':TRG:MEM:MODE_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.MEM.delay = ':TRG:MEM:DELAY_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.soft = ':TRG:SOFT_S.PROC';  % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.soft_settings = ':TRG:SOFT_S.SCAN';  % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.shared = ':TRG:MODE_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.triggers.blanking_length = ':TRG:BLANKING_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    pv_names.tails.triggers.MEM.(trigger).enable_status = [':TRG:MEM:',trigger,':EN_S'];
    pv_names.tails.triggers.MEM.(trigger).blanking_status = [':TRG:MEM:',trigger,':BL_S'];
end
%% Super Sequencer settings
pv_names.tails.Super_sequencer_count = ':SEQ:SUPER:COUNT_S';
pv_names.tails.Super_sequencer_reset = ':SEQ:SUPER:RESET_S.PROC';
pv_names.tails.Super_sequencer.count = ':SEQ:SUPER:COUNT_S';
pv_names.tails.Super_sequencer.reset = ':SEQ:SUPER:RESET_S.PROC';

%% Sequencer settings
% pv_names.tails.Sequencer.start_state = ':SEQ:PC_S';
% pv_names.tails.Sequencer.steady_state_bank = ':SEQ:0:BANK_S';
% pv_names.tails.Sequencer.Base = ':SEQ';
% pv_names.tails.Sequencer.start_frequency = ':START_FREQ_S';
% pv_names.tails.Sequencer.end_frequency = ':END_FREQ_S';
% pv_names.tails.Sequencer.count = ':COUNT_S';
% pv_names.tails.Sequencer.dwell = ':DWELL_S';
% pv_names.tails.Sequencer.gain = ':GAIN_S';
% pv_names.tails.Sequencer.gaindb = ':GAIN_DB_S';
% pv_names.tails.Sequencer.enable = ':ENABLE_S';
% pv_names.tails.Sequencer.step_frequency = ':STEP_FREQ_S';
% pv_names.tails.Sequencer.holdoff = ':HOLDOFF_S';
% pv_names.tails.Sequencer.bank_select = ':BANK_S';
% pv_names.tails.Sequencer.capture_state = ':CAPTURE_S';
% pv_names.tails.Sequencer.windowing_state = ':ENWIN_S';
% pv_names.tails.Sequencer.blanking_state = ':BLANK_S';
% pv_names.tails.Sequencer.reset = ':RESET_S.PROC';

% applies to all
pv_names.tails.Sequencer.start_state = ':SEQ:PC_S';
pv_names.tails.Sequencer.steady_state_bank = ':SEQ:0:BANK_S';
pv_names.tails.Sequencer.reset = ':SEQ:RESET_S.PROC';

for n_seq = 1:7
    l_seq = ['seq',num2str(n_seq)];
    n_seq_label = num2str(n_seq);
    pv_names.tails.Sequencer.(l_seq).start_frequency = [':SEQ:', n_seq_label,':START_FREQ_S'];
    pv_names.tails.Sequencer.(l_seq).end_frequency = [':SEQ:', n_seq_label,':END_FREQ_S'];
    pv_names.tails.Sequencer.(l_seq).count = [':SEQ:', n_seq_label, ':COUNT_S'];
    pv_names.tails.Sequencer.(l_seq).dwell = [':SEQ:', n_seq_label, ':DWELL_S'];
    pv_names.tails.Sequencer.(l_seq).gain = [':SEQ:', n_seq_label, ':GAIN_S'];
    pv_names.tails.Sequencer.(l_seq).gaindb = [':SEQ:', n_seq_label, ':GAIN_DB_S'];
    pv_names.tails.Sequencer.(l_seq).enable = [':SEQ:', n_seq_label, ':ENABLE_S'];
    pv_names.tails.Sequencer.(l_seq).step_frequency = [':SEQ:', n_seq_label, ':STEP_FREQ_S'];
    pv_names.tails.Sequencer.(l_seq).holdoff = [':SEQ:', n_seq_label, ':HOLDOFF_S'];
    pv_names.tails.Sequencer.(l_seq).bank_select = [':SEQ:', n_seq_label, ':BANK_S'];
    pv_names.tails.Sequencer.(l_seq).capture_state = [':SEQ:', n_seq_label, ':CAPTURE_S'];
    pv_names.tails.Sequencer.(l_seq).windowing_state = [':SEQ:', n_seq_label, ':ENWIN_S'];
    pv_names.tails.Sequencer.(l_seq).blanking_state = [':SEQ:', n_seq_label, ':BLANK_S'];
    pv_names.tails.Sequencer.(l_seq).holdoff_state = [':SEQ:', n_seq_label, ':STATE_HOLDOFF_S'];
    pv_names.tails.Sequencer.(l_seq).tune_pll_following = [':SEQ:', n_seq_label, ':TUNE_PLL_S'];

end %for


%% Bank settings
% pv_names.tails.Bunch_bank.Base = ':BUN';
% pv_names.tails.Bunch_bank.Gains = ':GAINWF_S';
% pv_names.tails.Bunch_bank.Output_types = ':OUTWF_S';
% pv_names.tails.Bunch_bank.FIR_select = ':FIRWF_S';
% pv_names.tails.Bunch_bank.FIR_set_enable = ':FIR:SET_ENABLE_S.PROC';
% pv_names.tails.Bunch_bank.FIR_enable = ':FIR:ENABLE_S';
% pv_names.tails.Bunch_bank.NCO1_set_enable = ':NCO1:SET_ENABLE_S.PROC';
% pv_names.tails.Bunch_bank.NCO2_set_enable = ':NCO2:SET_ENABLE_S.PROC';
% pv_names.tails.Bunch_bank.NCO1_enable = ':NCO1:ENABLE_S';
% pv_names.tails.Bunch_bank.NCO2_enable = ':NCO2:ENABLE_S';
% pv_names.tails.Bunch_bank.SEQ_set_enable = ':SEQ:SET_ENABLE_S.PROC';
% pv_names.tails.Bunch_bank.SEQ_enable = ':SEQ:ENABLE_S';
% pv_names.tails.Bunch_bank.PLL_enable = ':PLL:SET_ENABLE_S';
% pv_names.tails.Bunch_bank.FIR_set_disable = ':FIR:SET_DISABLE_S.PROC';
% pv_names.tails.Bunch_bank.FIR_disable = ':FIR:DISABLE_S';
% pv_names.tails.Bunch_bank.NCO1_disable = ':NCO1:SET_DISABLE_S.PROC';
% pv_names.tails.Bunch_bank.NCO2_disable = ':NCO2:SET_DISABLE_S.PROC';
% pv_names.tails.Bunch_bank.SEQ_disable = ':SEQ:SET_DISABLE_S.PROC';
% pv_names.tails.Bunch_bank.PLL_disable = ':PLL:SET_DISABLE_S.PROC';
% pv_names.tails.Bunch_bank.FIR_gains = ':FIR:GAIN_S';
% pv_names.tails.Bunch_bank.NCO1_gains = ':NCO1:GAIN_S';
% pv_names.tails.Bunch_bank.NCO2_gains = ':NCO2:GAIN_S';
% pv_names.tails.Bunch_bank.SEQ_gains = ':SEQ:GAIN_S';
% pv_names.tails.Bunch_bank.PLL_gains = ':PLL:GAIN_S';

for n_bank = 0:3
    l_bank = ['bank',num2str(n_bank)];
    n_bank_label = num2str(n_bank);
    pv_names.tails.Bunch_bank.(l_bank).Output_types = [':BUN:', n_bank_label, ':OUTWF_S'];
    pv_names.tails.Bunch_bank.(l_bank).bunch_select = [':BUN:', n_bank_label, ':BUNCH_SELECT_S'];

    pv_names.tails.Bunch_bank.(l_bank).FIR.enablewf = [':BUN:', n_bank_label, ':FIR:ENABLE_S']; 
    pv_names.tails.Bunch_bank.(l_bank).FIR.set_enable = [':BUN:', n_bank_label, ':FIR:SET_ENABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).FIR.set_disable = [':BUN:', n_bank_label, ':FIR:SET_DISABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).FIR.gainwf = [':BUN:', n_bank_label, ':FIR:GAIN_S']; 
    pv_names.tails.Bunch_bank.(l_bank).FIR.gainswfdb = [':BUN:', n_bank_label, ':FIR:GAIN_DB']; 
    %     Select which filter to use on which bunch
    pv_names.tails.Bunch_bank.(l_bank).FIR.selectwf = [':BUN:', n_bank_label, ':FIRWF_S']; 
    pv_names.tails.Bunch_bank.(l_bank).FIR.set_select = [':BUN:', n_bank_label, ':FIRWF_SET_S.PROC'];

    pv_names.tails.Bunch_bank.(l_bank).NCO1.enablewf = [':BUN:', n_bank_label, ':NCO1:ENABLE_S'];
    pv_names.tails.Bunch_bank.(l_bank).NCO1.set_enable = [':BUN:', n_bank_label, ':NCO1:SET_ENABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).NCO1.set_disable = [':BUN:', n_bank_label, ':NCO1:SET_DISABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).NCO1.gainswf = [':BUN:', n_bank_label, ':NCO1:GAIN_S'];
    pv_names.tails.Bunch_bank.(l_bank).NCO1.gainswfdb = [':BUN:', n_bank_label, ':NCO1:GAIN_DB'];

    pv_names.tails.Bunch_bank.(l_bank).NCO2.enablewf = [':BUN:', n_bank_label, ':NCO2:ENABLE_S'];
    pv_names.tails.Bunch_bank.(l_bank).NCO2.set_enable = [':BUN:', n_bank_label, ':NCO2:SET_ENABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).NCO2.set_disable = [':BUN:', n_bank_label, ':NCO2:SET_DISABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).NCO2.gainswf = [':BUN:', n_bank_label, ':NCO2:GAIN_S'];
    pv_names.tails.Bunch_bank.(l_bank).NCO2.gainswfdb = [':BUN:', n_bank_label, ':NCO2:GAIN_DB'];

    pv_names.tails.Bunch_bank.(l_bank).SEQ.enablewf = [':BUN:', n_bank_label, ':SEQ:ENABLE_S'];
    pv_names.tails.Bunch_bank.(l_bank).SEQ.set_enable = [':BUN:', n_bank_label, ':SEQ:SET_ENABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).SEQ.set_disable = [':BUN:', n_bank_label, ':SEQ:SET_DISABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).SEQ.gainswf = [':BUN:', n_bank_label, ':SEQ:GAIN_S'];
    pv_names.tails.Bunch_bank.(l_bank).SEQ.gainswfdb = [':BUN:', n_bank_label, ':SEQ:GAIN_DB'];

    pv_names.tails.Bunch_bank.(l_bank).PLL.enablewf = [':BUN:', n_bank_label, ':PLL:ENABLE_S'];
    pv_names.tails.Bunch_bank.(l_bank).PLL.set_enable = [':BUN:', n_bank_label, ':PLL:SET_ENABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).PLL.set_disable = [':BUN:', n_bank_label, ':PLL:SET_DISABLE_S.PROC'];
    pv_names.tails.Bunch_bank.(l_bank).PLL.gainswf = [':BUN:', n_bank_label, ':PLL:GAIN_S'];
    pv_names.tails.Bunch_bank.(l_bank).PLL.gainswfdb = [':BUN:', n_bank_label, ':PLL:GAIN_DB'];
end %for

%% Detector settings
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
    pv_names.tails.Detector.(l_det).power = [':DET:',n_det_label,':POWER'];
    pv_names.tails.Detector.(l_det).bunch_select = [':DET:',n_det_label,':BUNCH_SELECT_S'];
    pv_names.tails.Detector.(l_det).reset_selection = [':DET:',n_det_label,':RESET_SELECT_S.PROC'];
    pv_names.tails.Detector.(l_det).set_selection = [':DET:',n_det_label,':SET_SELECT_S.PROC'];
end %for

%% Memory settings
pv_names.tails.MEM.status = ':MEM:BUSY';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.channel_select = ':MEM:SELECT_S';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.offset = ':MEM:OFFSET_S';% NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.runout = ':MEM:RUNOUT_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.channel0_target = ':MEM:SEL0_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.MEM.channel1_target = ':MEM:SEL1_S'; % NEED TO TAKE OFF THE X|Y BEFORE USE.
pv_names.tails.TRG.memory_status = ':TRG:MEM:STATUS';


%% NCO1 settings
pv_names.tails.NCO1.frequency = ':NCO1:FREQ_S';
pv_names.tails.NCO1.gain = ':NCO1:GAIN_S';
pv_names.tails.NCO1.gaindb = ':NCO1:GAIN_DB_S';
pv_names.tails.NCO1.enable = ':NCO1:ENABLE_S';
pv_names.tails.NCO1.PLL_follow = ':NCO1:TUNE_PLL_S';

%% NCO2 settings
pv_names.tails.NCO2.gain_scalar = ':NCO2:GAIN_SCALAR_S';
pv_names.tails.NCO2.gain_db = ':NCO2:GAIN_DB_S';
pv_names.tails.NCO2.enable = ':NCO2:ENABLE_S';
pv_names.tails.NCO2.frequency = ':NCO2:FREQ_S';
pv_names.tails.NCO2.enable = ':NCO2:ENABLE_S';
pv_names.tails.NCO2.PLL_follow = ':NCO2:TUNE_PLL_S';

%% FIR settings
pv_names.tails.FIR.gain = ':FIR:GAIN_S';
pv_names.tails.FIR.gaindb = ':FIR:GAIN_DB_S';
pv_names.tails.FIR.method_of_construction = ':FIR:USEWF_S';

%% Tune settings
pv_names.tails.tune.peak.left_area = ':PEAK:LEFT:AREA';
pv_names.tails.tune.peak.right_area = ':PEAK:RIGHT:AREA';
pv_names.tails.tune.peak.centre_area = ':PEAK:CENTRE:AREA';
pv_names.tails.tune.peak.sync_tune = ':PEAK:SYNCTUNE';
pv_names.tails.tune.centre = ':TUNE:CENTRE:TUNE';
pv_names.tails.tune.left = ':TUNE:LEFT:TUNE';
pv_names.tails.tune.right = ':TUNE:RIGHT:TUNE';

%% PLL settings
pv_names.tails.pll.detector.dwell = ':PLL:DET:DWELL_S';
pv_names.tails.pll.detector.target_bunches = ':PLL:DET:BUNCHES_S';
pv_names.tails.pll.detector.mode = ':PLL:DET:SELECT_S';
pv_names.tails.pll.detector.scaling = ':PLL:DET:SCALING_S';
pv_names.tails.pll.detector.blanking = ':PLL:DET:BLANKING_S';
pv_names.tails.pll.detector.dwell = ':PLL:DET:DWELL_S';
pv_names.tails.pll.nco.enable = ':PLL:NCO:ENABLE_S';
pv_names.tails.pll.nco.gain = ':PLL:NCO:GAIN_DB_S';
pv_names.tails.pll.nco.set_frequency = ':PLL:NCO:FREQ_S';
pv_names.tails.pll.nco.frequency = ':PLL:NCO:FREQ';
pv_names.tails.pll.nco.offset_waveform = ':PLL:NCO:OFFSETWF';
pv_names.tails.pll.nco.mean_offset = ':PLL:NCO:MEAN_OFFSET';
pv_names.tails.pll.nco.std_offset = ':PLL:NCO:STD_OFFSET';
pv_names.tails.pll.nco.offset = ':PLL:NCO:OFFSET';
pv_names.tails.pll.nco.tune = ':PLL:NCO:TUNE';
pv_names.tails.pll.start = ':PLL:CTRL:START_S.PROC';
pv_names.tails.pll.stop = ':PLL:CTRL:STOP_S.PROC';
pv_names.tails.pll.p = ':PLL:CTRL:KP_S';
pv_names.tails.pll.i = ':PLL:CTRL:KI_S';
pv_names.tails.pll.target_phase = ':PLL:CTRL:TARGET_S';
pv_names.tails.pll.minumum_magnitude = ':PLL:CTRL:MIN_MAG_S';
pv_names.tails.pll.maximum_offset = ':PLL:CTRL:MAX_OFFSET_S';
pv_names.tails.pll.status = ':PLL:CTRL:STATUS';
pv_names.tails.pll.readback.magnitude = ':PLL:FILT:MAG';
pv_names.tails.pll.readback.phase = ':PLL:FILT:PHASE';
pv_names.tails.pll.readback.i = ':PLL:FILT:I';
pv_names.tails.pll.readback.q = ':PLL:FILT:Q';
pv_names.tails.pll.stop_reasons.stop = ':PLL:CTRL:STOP:STOP';
pv_names.tails.pll.stop_reasons.detector_overflow = ':PLL:CTRL:STOP:DET_OVF';
pv_names.tails.pll.stop_reasons.offset_overflow = ':PLL:CTRL:STOP:OFFSET_OVF';
pv_names.tails.pll.stop_reasons.magnitude_error = ':PLL:CTRL:STOP:MAG_ERROR';

%% ADC buffers
pv_names.tails.adc.delta = ':ADC:MMS:DELTA';
pv_names.tails.adc.max = ':ADC:MMS:MAX';
pv_names.tails.adc.mean = ':ADC:MMS:MEAN';
pv_names.tails.adc.min = ':ADC:MMS:MIN';
pv_names.tails.adc.std = ':ADC:MMS:STD';
pv_names.tails.adc.reject_count = ':ADC:REJECT_COUNT_S';
pv_names.tails.adc.phase.mean = ':ADC:PHASE_MEAN';
pv_names.tails.adc.dram_source = ':ADC:DRAM_SOURCE_S';
pv_names.tails.adc.loopback = ':ADC:LOOPBACK_S';


%% DAC buffers
pv_names.tails.dac.delta = ':DAC:MMS:DELTA';
pv_names.tails.dac.max = ':DAC:MMS:MAX';
pv_names.tails.dac.mean = ':DAC:MMS:MEAN';
pv_names.tails.dac.min = ':DAC:MMS:MIN';
pv_names.tails.dac.std = ':DAC:MMS:STD';
pv_names.tails.dac.dram_source = ':DAC:DRAM_SOURCE_S';
