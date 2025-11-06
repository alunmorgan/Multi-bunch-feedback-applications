function varargout = mbf_growdamp_capture(mbf_axis, varargin)
% Gathers data on the machine environment.
% Runs a growdamp experiment on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tunes (structure): Tunes of the machine.
%       additional_save_location (str): Full path to additional save location.
%       capture_full_bunch_motion (str): yes or no. Determines if the full
%       time series of bunch motion is captured and stored (large data).
%       save_to_archive (str): yes or no.
%       excitation_location: Tune or Sideband.
%   Returns:
%       growdamp (struct): data structure containing the experimental
%                          results and the machine conditions.
%                          [optional output]
%
% example growdamp = mbf_growdamp_capture('x')

excitation_locations = {'Tune', 'Sideband'};
binary_string = {'yes', 'no'};
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'tunes', NaN);
addParameter(p, 'save_to_archive', 'yes', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'additional_save_location', NaN, valid_string);
addParameter(p, 'capture_full_bunch_motion', 'no', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'excitation_location', 'Tune', @(x) any(validatestring(x,excitation_locations)));
addParameter(p, 'excitation', 'yes', @(x) any(validatestring(x,binary_string)));
parse(p, mbf_axis, varargin{:});

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's') &&...
        ~strcmpi(mbf_axis, 'tx')&& ~strcmpi(mbf_axis, 'ty')
    error('growdamp:invalidAxis', 'mbf_growdamp_capture: Incorrect value axis given (should be x, y or s. OR tx, ty if testing)');
end %if
[root_string, ~, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

pv_head = pv_names.hardware_names.(mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(mbf_axis);
triggers = pv_names.tails.triggers;
Sequencer = pv_names.tails.Sequencer;
FIR = pv_names.tails.FIR;

%% Getting setup data
% getting general environment data.
growdamp = machine_environment('tunes', p.Results.tunes);
% Add the axis label to the data structure.
growdamp.ax_label = mbf_axis;
% construct name and add it to the structure
if strcmp(p.Results.excitation,'no')
    growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis_no_excitation'];
else
    if strcmp(p.Results.excitation_location,'Sideband')
        growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis_Sideband_excitation'];
    else
        growdamp.base_name = ['Growdamp_' growdamp.ax_label '_axis'];
    end %if
end %if

% Getting feedback gain
growdamp.FIR_gain = [pv_head, FIR.gain];

% ordering is important here. (reverse order of experiment)
if strcmp(p.Results.excitation, 'no')
    exp_state_names = {'active', 'growth'};
else
    % Getting settings for growth, natural damping, and active damping.
    exp_state_names = {'spacer2', 'active',  'growth2','spacer', 'passive','growth'};
end %if

for n=1:length(exp_state_names)
    % Getting the number of turns
    growdamp.([exp_state_names{n}, '_turns']) = get_variable([pv_head,...
        Sequencer.(['seq' num2str(n)]).count]);
    % Getting the number of turns each point dwells at
    growdamp.([exp_state_names{n}, '_dwell']) = get_variable([pv_head,...
        Sequencer.(['seq' num2str(n)]).dwell]);
    % Getting the gain
    growdamp.([exp_state_names{n}, '_gain']) = get_variable([pv_head,...
        Sequencer.(['seq' num2str(n)]).gain]);
end %for
growdamp.exp_state_names = exp_state_names;

%% Preparing system for data capture
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
    error('growdamp:memoryNotReady', 'Memory is not ready please try again')
end %if

%Disarm, so that the current settings will be picked up upon arming.
set_variable([pv_head, triggers.SEQ.disarm], 1)

%% Trigger the measurement
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')|| strcmp(mbf_axis, 'tx')
    chan = 0;
elseif strcmp(mbf_axis, 'y') || strcmp(mbf_axis, 'ty')
    chan = 1;
end %if
if strcmpi(mbf_axis, 's')
    mem_lock = 180;
else
    mem_lock = 30;
end %if
%Arm
set_variable([pv_head, triggers.SEQ.arm], 1)
% Trigger
set_variable([pv_head_mem, triggers.soft], 1)
[growdamp.data, growdamp.data_freq, ~] = mbf_read_det(pv_head_mem,...
    'axis', chan, 'lock', mem_lock);

%% Capturing full bunch motion data
if strcmpi(p.Results.capture_full_bunch_motion, 'yes')
    turn_count = 1250 .* 400;
    turn_offset = 0;
    growdamp.bunch_motion = mbf_read_mem(pv_head_mem, turn_count,'offset', turn_offset, 'channel', 0, 'lock', 60);
end

%% saving the data to a file
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')|| strcmp(mbf_axis, 's')
    %     only save if not on test system
    if strcmp(p.Results.save_to_archive, 'yes')
        save_to_archive(root_string, growdamp)
    end %if
    if ~isnan(p.Results.additional_save_location)
        save(additional_save_location, growdamp)
    end %if
end %if

if nargout == 1
    varargout{1} = growdamp;
end %if
