function varargout = mbf_growdamp_capture(mbf_axis, additional_save_location)
% Gathers data on the machine environment.
% Runs a growdamp experiment on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       additional_save_location (str): Full path to additional save location.
%   Returns:
%       growdamp (struct): data structure containing the experimental
%                          results and the machine conditions.
%                          [optional output]
%
% example growdamp = mbf_growdamp_capture('x')

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's') &&...
        ~strcmpi(mbf_axis, 'tx')&& ~strcmpi(mbf_axis, 'ty')
    error('mbf_growdamp_capture: Incorrect value axis given (should be x, y or s. OR tx, ty if testing)');
end %if
[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')
    pv_head_mem = pv_names.hardware_names.('T');
elseif strcmp(mbf_axis, 's')
    pv_head_mem = pv_names.hardware_names.('L');
elseif strcmp(mbf_axis, 'tx') || strcmp(mbf_axis, 'ty')
    pv_head_mem = pv_names.hardware_names.('lab');
end %if

lcaPut([pv_head_mem, pv_names.tails.triggers.MEM.disarm], 1)
% Arm the memory so that it cycles. This means that all the status PV are
% updated. Otherwise the code will say the memory is not ready as the status is
% stale.
lcaPut([pv_head_mem pv_names.tails.triggers.MEM.arm], 1) 
pause(2) % Letting the hardware sort itself out.
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
end %for

% Trigger the measurement
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')|| strcmp(mbf_axis, 'tx')
    chan = 0;
elseif strcmp(mbf_axis, 'y') || strcmp(mbf_axis, 'ty')
    chan = 1;
end %if
if strcmpi(mbf_axis, 's')
    mem_lock = 180;
else
    mem_lock = 10;
end %if
%Arm
lcaPut([pv_head, pv_names.tails.triggers.SEQ.arm], 1)
% Trigger
lcaPut([pv_head_mem, pv_names.tails.triggers.soft], 1)
[growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_head_mem,...
    'axis', chan, 'lock', mem_lock);

turn_count = 1250 .* 400;
turn_offset = 0;
growdamp.bunch_motion = mbf_read_mem(pv_head_mem, turn_count,'offset', turn_offset, 'channel', 0, 'lock', 60);
%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    save_to_archive(root_string, growdamp)
    if nargin == 2
        save(additional_save_location, growdamp)
    end %if
end %if

if nargout == 1
    varargout{1} = growdamp;
end %if
