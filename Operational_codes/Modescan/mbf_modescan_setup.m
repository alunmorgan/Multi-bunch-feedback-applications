function mbf_modescan_setup(input_settings, pv_names)
% Sets up the MBF system to be ready for a modescan measurement.
%
%   Args:
%       input_settings(struct): contains all the setup information.
%       pv_names(struct): contains the locations of all the machine parameters.
%
% example: mbf_modescan_setup(input_settings, pv_names)

mbf_tools
% Generate the base PV name.
system_axis = pv_names.hardware_names.(input_settings.mbf_axis);
% state 1 of sequencer
seq = pv_names.tails.Sequencer.seq1;

set_variable([system_axis seq.start_frequency], input_settings.excitation_tune);
set_variable([system_axis seq.step_frequency],1);
set_variable([system_axis seq.turns], input_settings.harmonic_number -1);
set_variable([system_axis seq.holdoff], 0);
set_variable([system_axis seq.dwell], input_settings.dwell);
set_variable([system_axis seq.bank_select], 'Bank 1');
set_variable([system_axis seq.capture_state], 'Capture');
set_variable([system_axis seq.windowing_state], 'Disabled');
set_variable([system_axis seq.gaindb], input_settings.excitation_gain);
set_variable([system_axis seq.blanking_state], 'Off');
