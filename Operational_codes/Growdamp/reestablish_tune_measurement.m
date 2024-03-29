function reestablish_tune_measurement(mbf_axis)
% sets up the tune measurement by setting bank1 and sequencer state one as
% required.
%   Args:
%       mbf_axis(str): 'x','y', or 's'
% Example: reestablish_tune_measurement('x')

[~, harmonic_number, pv_names, ~] = mbf_system_config;

if strcmpi(mbf_axis,'x')
    sweep_start = 80.139;
    sweep_end = 80.239;
    tune_gain = -54;
    tune_dwell = 100;
    tune_count = 4096;
    base = pv_names.hardware_names.x;
elseif strcmpi(mbf_axis, 'y')
    sweep_start = 80.227;
    sweep_end = 80.327;
    tune_gain = -54;
    tune_dwell = 100;
    tune_count = 4096;
    base = pv_names.hardware_names.y;
elseif strcmpi(mbf_axis, 's')
    sweep_start = 80.00320;
    sweep_end = 80.00520;
    tune_gain = -18;
    tune_dwell = 100;
    tune_count = 4096;
    base = pv_names.hardware_names.s;
else
    error('MBF:InputError','Please set required axis to x, y, or s')
end %if

% setting up sequencer state 1 to be the tune sweep.
set_variable([base, pv_names.tails.Super_sequencer.count], 1);
set_variable([base, pv_names.tails.Sequencer.start_state] ,1);

tune_sequencer = pv_names.tails.Sequencer.seq1;

set_variable([base, tune_sequencer.start_frequency], sweep_start);
set_variable([base, tune_sequencer.end_frequency], sweep_end);
set_variable([base, tune_sequencer.gaindb], tune_gain);
set_variable([base, tune_sequencer.count], tune_count);
set_variable([base, tune_sequencer.dwell], tune_dwell);

set_variable([base, tune_sequencer.bank_select], {'Bank 1'});
set_variable([base, tune_sequencer.tune_pll_following], {'Ignore'});
set_variable([base, tune_sequencer.enable], 'On');
set_variable([base, tune_sequencer.holdoff_state], 0);
set_variable([base, tune_sequencer.holdoff], 0);
set_variable([base, tune_sequencer.blanking_state], {'Blanking'});
set_variable([base, tune_sequencer.windowing_state], {'Windowed'});
set_variable([base, tune_sequencer.capture_state], {'Capture'});

tune_bank = pv_names.tails.Bunch_bank.bank1;
% Setting bank 1 to use both the FIR and the sequencer but nothing else.
set_variable([base, tune_bank.FIR.enablewf], ones(1,harmonic_number));
set_variable([base, tune_bank.NCO1.enablewf], zeros(1, harmonic_number));
set_variable([base, tune_bank.NCO2.enablewf], zeros(1, harmonic_number));
set_variable([base, tune_bank.SEQ.enablewf], ones(1, harmonic_number));
set_variable([base, pv_names.tails.Bunch_bank.bank1.PLL.enablewf], zeros(1, harmonic_number));

% triggering
set_variable([base, pv_names.tails.triggers.mode], 'Rearm');
set_variable([base, pv_names.tails.triggers.EXT.enable_status], 'Enable');
set_variable([base, pv_names.tails.triggers.SEQ.arm], 1);