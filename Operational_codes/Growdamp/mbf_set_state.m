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

Sequencer = pv_names.tails.Sequencer;
% pv_head = [pv_names.hardware_names.(ax), Sequencer.Base, num2str(state)];
pv_head = [pv_names.hardware_names.(ax), Sequencer.Base, ':', num2str(state)];

mbf_get_then_put([pv_head, Sequencer.start_frequency], tune);
mbf_get_then_put([pv_head, Sequencer.step_frequency],0);
mbf_get_then_put([pv_head, Sequencer.count], duration);
mbf_get_then_put([pv_head, Sequencer.holdoff], 0);
mbf_get_then_put([pv_head, Sequencer.dwell], dwell);
mbf_get_then_put([pv_head, Sequencer.bank_select], ['Bank ',num2str(bank)]);
mbf_get_then_put([pv_head, Sequencer.capture_state], capture);
mbf_get_then_put([pv_head, Sequencer.windowing_state], 'Disabled');
mbf_get_then_put([pv_head, Sequencer.gain], gain);
mbf_get_then_put([pv_head, Sequencer.blanking_state], 'Off');
mbf_get_then_put([pv_head, Sequencer.enable], enable);
