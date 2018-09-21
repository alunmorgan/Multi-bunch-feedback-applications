function varargout = mbf_growdamp_capture(mbf_axis)
% Gathers data on the machine environment.
% Runs a growdamp experiment on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%   Returns:
%       growdamp (struct): data structure containing the experimental
%                          results and the machine conditions. 
%                          [optional output]
%
% example growdamp = mbf_growdamp_capture('x')

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('mbf_growdamp_capture: Incorrect value axis given (should be x, y or s)');
end %if
[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
% settings = mbf_growdamp_config(mbf_axis);
% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);
% getting general environment data.
growdamp = machine_environment;
% Add the axis label to the data structure.
growdamp.ax_label = mbf_axis;
% construct name and add it to the structure
growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis'];

% set tune, should only be required on excitation (state 4), but do it on
% all just in case someone makes a big jump!
%  Also getting settings for growth, natural damping, and active damping.
exp_state_names = {'spacer', 'act', 'nat', 'growth'};
for n=2:4
    mbf_get_then_put([pv_head, ...
        pv_names.tails.Sequencer.Base, num2str(n),...
        pv_names.tails.Sequencer.start_frequency], tune);
    % Getting the number of turns
    growdamp.([exp_state_names{n}, '_turns']) = lcaGet([pv_head,...
        pv_names.tails.Sequencer.Base, num2str(n), ...
        pv_names.tails.Sequencer.count]);
    % Getting the number of turns each point dwells at
    growdamp.([exp_state_names{n}, '_dwell']) = lcaGet([pv_head,... 
        pv_names.tails.Sequencer.Base, num2str(n), ...
        pv_names.tails.Sequencer.dwell]);
    % Getting the gain
    growdamp.([exp_state_names{n}, '_gain']) = lcaGet([pv_head,... 
        pv_names.tails.Sequencer.Base, num2str(n), ...
        pv_names.tails.Sequencer.gain]);
end

% Trigger the measurement
% NEED TO SELECT THE CORRECT CHANNEL.
% LENGTH 467?
lcaPut([pv_head(1:end-2), pv_names.tails.triggers.arm], 1)
% readout under a lock
growdamp.data = mbf_read_det(pv_head, 467 ,'channel', 0, 'lock', 60);
% Trigger
lcaPut([pv_head(1:end-2), pv_names.tails.triggers.soft], 1)

%% saving the data to a file
save_to_archive(root_string, growdamp)

if nargout == 1
    varargout{1} = growdamp;
end %if

