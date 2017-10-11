function mbf_set_state(ax, state, tune, bank, gain, duration, dwell, capture)
% Setup an individual state in the super sequencer.
%
% Args:
%       ax (int)      : 1,2 or 3 corresponds to x, y, or s axis
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

mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':START_FREQ_S'], tune);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':STEP_FREQ_S'],0);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':COUNT_S'], duration);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':HOLDOFF_S'], 0);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':DWELL_S'], dwell);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':BANK_S'], ['Bank ',num2str(bank)]);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':CAPTURE_S'], capture);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':ENWIN_S'], 'Disabled');
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':GAIN_S'], gain);
mbf_get_then_put([ax2dev(ax) ':SEQ:',num2str(state),':BLANK_S'], 'Off');