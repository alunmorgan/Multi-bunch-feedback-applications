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
pv_head_mem = pv_names.hardware_names.('T');
lcaPut([pv_head_mem, pv_names.tails.triggers.MEM.disarm], 1) % TESTING CODE
temp1 = lcaGet([pv_head_mem pv_names.tails.TRG.memory_status]);
if strcmp(temp1, 'Idle') == 1
    mbf_get_then_put({[pv_head_mem pv_names.tails.triggers.MEM.arm]},1);
else
    error('Memory is not ready please try again')
end %if
% getting general environment data.
growdamp = machine_environment;
% Add the axis label to the data structure.
growdamp.ax_label = mbf_axis;
% construct name and add it to the structure
growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis'];

%Disarm, so that the current settings will be picked up upon arming.
lcaPut([pv_head, pv_names.tails.triggers.SEQ.disarm], 1)

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
    % ADD STARTING FREQ
    %SR23C-DI-TMBF-01:X:SEQ:4:START_FREQ_S
%     growdamp.([exp_state_names{n}, '_gain']) = lcaGet([pv_head,... 
%         pv_names.tails.Sequencer.Base, num2str(n), ...
%         pv_names.tails.Sequencer.gain]);
end %for

% Trigger the measurement
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')
    chan = 0;
elseif strcmp(mbf_axis, 'y')
    chan = 1;
end %if
%Arm
lcaPut([pv_head, pv_names.tails.triggers.SEQ.arm], 1)
% Trigger
if strcmpi(mbf_axis, 's')
    lcaPut([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
    [growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_names.hardware_names.L,...
                                                   'axis', chan, 'lock', 180);
else
    lcaPut([pv_names.hardware_names.T, pv_names.tails.triggers.soft], 1)
    [growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_names.hardware_names.T,...
                                                   'axis', chan, 'lock', 60);
end
turn_count = 1250 .* 400;
turn_offset = 0;
growdamp.bunch_motion = mbf_read_mem(pv_names.hardware_names.T, turn_count,'offset', turn_offset, 'channel', 0, 'lock', 60);
%% saving the data to a file
save_to_archive(root_string, growdamp)

if nargout == 1
    varargout{1} = growdamp;
end %if
