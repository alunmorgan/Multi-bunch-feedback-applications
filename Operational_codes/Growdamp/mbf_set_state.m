function mbf_set_state(ax, state, tune, bank, gain, enable, duration, dwell, capture)
% Setup an individual state in the super sequencer.
%
% Args:
%       ax (str)      : 'x', 'y', or 's' axis
%       state (int)   : state number in the sequencer.
%       tune (float)  : Tune of the machine.
%       bank (int)    : The bunch bank used for this state.
%       gain (str)    : the excitation level.
%       duration (int): the number of turns the state is active.
%       dwell (int)   : Dwell time (turns).
%       capture (str) : 'Capture' or 'Discard' depending onn if you want to
%                       keep the data or not
%
% Example: mbf_set_state(ax, state, tune, bank, gain, duration, dwell, capture)
[~, ~, pv_names, ~] = mbf_system_config;

system_axis = pv_names.hardware_names.(ax);
seq = pv_names.tails.Sequencer.(['seq' num2str(state)]);

mbf_get_then_put([system_axis, seq.start_frequency], tune);
mbf_get_then_put([system_axis, seq.step_frequency],0);
mbf_get_then_put([system_axis, seq.count], duration);
mbf_get_then_put([system_axis, seq.holdoff], 0);
mbf_get_then_put([system_axis, seq.dwell], dwell);
mbf_get_then_put([system_axis, seq.bank_select], ['Bank ',num2str(bank)]);
mbf_get_then_put([system_axis, seq.capture_state], capture);
mbf_get_then_put([system_axis, seq.windowing_state], 'Disabled');
mbf_get_then_put([system_axis, seq.gain], gain);
mbf_get_then_put([system_axis, seq.blanking_state], 'Off');
mbf_get_then_put([system_axis, seq.enable], enable);
