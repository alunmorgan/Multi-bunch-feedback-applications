function mbf_modescan_setup(mbf_axis, dwell, tune, gain)
% Sets up the MBF system to be ready for a modescan measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Tune from a previous measurement.
%
% example: mbf_modescan_setup('x', 1, 0.18, -30)

mbf_tools
[~, harmonic_number, pv_names] = mbf_system_config;
% Generate the base PV name.
system_axis = pv_names.hardware_names.(mbf_axis);
% state 1 of sequencer
seq = pv_names.tails.Sequencer.seq1;

set_variable([system_axis seq.start_frequency], tune);
set_variable([system_axis seq.step_frequency],1);
set_variable([system_axis seq.count], harmonic_number -1);
set_variable([system_axis seq.holdoff], 0);
set_variable([system_axis seq.dwell], dwell);
set_variable([system_axis seq.bank_select], 'Bank 1');
set_variable([system_axis seq.capture_state], 'Capture');
set_variable([system_axis seq.windowing_state], 'Disabled');
set_variable([system_axis seq.gaindb], gain);
set_variable([system_axis seq.blanking_state], 'Off');
