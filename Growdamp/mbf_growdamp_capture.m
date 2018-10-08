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
% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);
% getting general environment data.
growdamp = machine_environment;
% Add the axis label to the data structure.
growdamp.ax_label = mbf_axis;
% construct name and add it to the structure
growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis'];

%Disarm, so that the current settings will be picked up upon arming.
lcaPut([pv_head, pv_names.tails.triggers.disarm], 1)

% Getting settings for growth, natural damping, and active damping.
exp_state_names = {'spacer', 'act', 'nat', 'growth'};
for n=1:4
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
end %for

% Trigger the measurement
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')
    chan = 0;
elseif strcmp(mbf_axis, 'y')
    chan = 1;
end %if
%Arm
lcaPut([pv_head, pv_names.tails.triggers.arm], 1)
% Trigger
if strcmpi(mbf_axis, 's')
    lcaPut([pv_head(1:end-3), pv_names.tails.triggers.soft], 1)
    [growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_head(1:end-3),...
                                                   'axis', chan, 'lock', 180);
else
    lcaPut([pv_head(1:end-2), pv_names.tails.triggers.soft], 1)
    [growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_head(1:end-2),...
                                                   'axis', chan, 'lock', 60);
end

%% saving the data to a file
save_to_archive(root_string, growdamp)

if nargout == 1
    varargout{1} = growdamp;
end %if
