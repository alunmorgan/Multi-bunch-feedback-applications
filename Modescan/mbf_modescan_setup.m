function mbf_modescan_setup(mbf_axis, tune)
% Sets up the MBF system to be ready for a modescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Tune of the machine.
%
% example: mbf_modescan_setup('x', 0.17)

[~, harmonic_number, pv_names] = mbf_system_config;
settings = mbf_modescan_config(mbf_axis);
Bunch_bank = pv_names.tails.Bunch_bank;
Sequencer = pv_names.tails.Sequencer;
NCO = pv_names.tails.NCO;
FIR = pv_names.tails.FIR;

% Generate the base PV name.
pv_head = ax2dev(settings.axis_number);

% bunch bank0
mbf_get_then_put([pv_head, Bunch_bank.Base, '0', Bunch_bank.Gains], ...
    ones(1,harmonic_number) .* 1023); % bunch gains
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
mbf_get_then_put([pv_head, Bunch_bank.Base, '0', Bunch_bank.Output_types], ...
    ones(1,harmonic_number) .* 1);
mbf_get_then_put([pv_head, Bunch_bank.Base, '0', Bunch_bank.FIR_select], ...
    ones(1,harmonic_number) .* 0); % select which FIR filter to use

% bunch bank1
mbf_get_then_put([pv_head, Bunch_bank.Base, '1', Bunch_bank.Gains], ...
    ones(1,harmonic_number) .* 1023); % bunch gains
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
mbf_get_then_put([pv_head, Bunch_bank.Base, '1', Bunch_bank.Output_types], ...
    ones(1,harmonic_number) .* 4);
mbf_get_then_put([pv_head, Bunch_bank.Base, '1', Bunch_bank.FIR_select], ...
    ones(1,harmonic_number) .* 0); % select which FIR filter to use


% state 1
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.start_frequency], tune);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.step_frequency],1);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.count], harmonic_number/2 -1);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.holdoff], 0);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.dwell], settings.dwell);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.bank_select], 'Bank 1');
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.capture_state], 'Capture');
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.windowing_state], 'Disabled');
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.gain], [num2str(settings.seq_gain),'dB']);
mbf_get_then_put([pv_head, Sequencer.Base, '1', Sequencer.blanking_state], 'Off');


% start state
mbf_get_then_put([pv_head, Sequencer_start_state], 1);
% steady state bank
mbf_get_then_put([pv_head, Sequencer_steady_state_bank], 'Bank 0');


% NCO setup
mbf_get_then_put([pv_head, NCO.Base, NCO.frequency], tune);
mbf_get_then_put([pv_head, NCO.Base, NCO.gain], '0dB');

% select if using waveform or settings
mbf_get_then_put([pv_head, FIR.Base, '0', FIR.method_of_construction], 'Settings');

mbf_get_then_put([pv_head, FIR.Base, FIR.gain], [num2str(settings.ex_level),'dB']);

mbf_get_then_put([pv_head, Detector_mode], 'All Bunches')
mbf_get_then_put([pv_head, Detector_gain], [num2str(settings.det_gain),'dB'])