function varargout = mbf_growthrates_capture(mbf_axis, varargin)
% Gathers data on the machine environment.
% Runs a growth rates experiment on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tunes (structure): Tunes of the machine.
%       additional_save_location (str): Full path to additional save location.
%       save_to_archive (str): yes or no. 
%   Returns:
%       growdamp (struct): data structure containing the experimental
%                          results and the machine conditions.
%                          [optional output]
%
% example growdamp = mbf_growdamp_capture('x')

binary_string = {'yes', 'no'};
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'tunes', NaN);
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
parse(p, mbf_axis, varargin{:});

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's') &&...
        ~strcmpi(mbf_axis, 'tx')&& ~strcmpi(mbf_axis, 'ty')
    error('growthrates:invalidAxis', 'mbf_growdamp_capture: Incorrect value axis given (should be x, y or s. OR tx, ty if testing)');
end %if
[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

pv_head = pv_names.hardware_names.(mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(mbf_axis);
triggers = pv_names.tails.triggers;
Sequencer = pv_names.tails.Sequencer;

set_variable([pv_head_mem, triggers.MEM.disarm], 1)
pause(0.5) % Letting the hardware sort itself out.
% Arm the memory so that it cycles. This means that all the status PV are
% updated. Otherwise the code will say the memory is not ready as the status is
% stale.
set_variable([pv_head_mem triggers.MEM.arm], 1)
pause(2) % Letting the hardware sort itself out.
temp1 = get_variable([pv_head_mem pv_names.tails.TRG.memory_status]);
if ~strcmp(temp1, 'Idle') == 1
    mbf_get_then_put({[pv_head_mem triggers.MEM.arm]},1);
else
    error('growthrates:memoryNotReady', 'Memory is not ready please try again')
end %if
% getting general environment data.
growthrates = machine_environment('tunes', p.Results.tunes);
% Add the axis label to the data structure.
growthrates.ax_label = mbf_axis;
% construct name and add it to the structure
    growthrates.base_name = ['Growthrates_' growthrates.ax_label '_axis'];

%Disarm, so that the current settings will be picked up upon arming.
set_variable([pv_head, triggers.SEQ.disarm], 1)

% Getting settings for growth.
exp_state_names = {'act', 'growth'};
for n=1:2
    % Getting the number of turns
    growthrates.([exp_state_names{n}, '_turns']) = get_variable([pv_head,...
        Sequencer.Base, ':', num2str(n), Sequencer.count]);
    % Getting the number of turns each point dwells at
    growthrates.([exp_state_names{n}, '_dwell']) = get_variable([pv_head,...
        Sequencer.Base, ':', num2str(n), Sequencer.dwell]);
    % Getting the gain
    growthrates.([exp_state_names{n}, '_gain']) = get_variable([pv_head,...
        Sequencer.Base, ':', num2str(n), Sequencer.gain]);
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
set_variable([pv_head, triggers.SEQ.arm], 1)
% Trigger
set_variable([pv_head_mem, triggers.soft], 1)
[growthrates.data, growthrates.data_freq, ~] = mbf_read_det(pv_head_mem,...
    'axis', chan, 'lock', mem_lock);

%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, growthrates)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, growthrates)
    end %if
end %if

if nargout == 1
    varargout{1} = growthrates;
end %if
