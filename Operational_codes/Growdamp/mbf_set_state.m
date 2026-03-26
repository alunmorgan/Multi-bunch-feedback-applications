function mbf_set_state(ax, state, tune, setup_data)
% Setup an individual state in the super sequencer.
%
% Args:
%       ax (str)      : 'x', 'y', or 's' axis
%       state (int)   : state number in the sequencer.
%       tune (float)  : Tune of the machine.
%       setup_data (struct): containing
%           bank (int)    : The bunch bank used for this state.
%           gain (str)    : the excitation level.
%           duration (int): the number of turns the state is active.
%           dwell (int)   : Dwell time (turns).
%           capture (str) : 'Capture' or 'Discard' depending onn if you want to
%                            keep the data or not
%
% Example: mbf_set_state(ax, state, tune, setup_data)
[~, ~, pv_names, ~] = mbf_system_config;

system_axis = pv_names.hardware_names.(ax);
seq = pv_names.tails.Sequencer.(['seq' num2str(state)]);

set_variable([system_axis, seq.start_frequency], tune);
set_variable([system_axis, seq.step_frequency],0);
set_variable([system_axis, seq.count], setup_data.duration);
set_variable([system_axis, seq.holdoff], 0);
set_variable([system_axis, seq.dwell], setup_data.dwell);
set_variable([system_axis, seq.bank_select], ['Bank ',num2str(setup_data.bank)]);
set_variable([system_axis, seq.capture_state], setup_data.capture);
set_variable([system_axis, seq.windowing_state], 'Disabled');
set_variable([system_axis, seq.gain], setup_data.excitation_level);
set_variable([system_axis, seq.blanking_state], 'Off');
set_variable([system_axis, seq.enable], setup_data.excitation);
