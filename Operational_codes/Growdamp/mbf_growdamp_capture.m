function growdamp = mbf_growdamp_capture(mbf_axis, pv_names, capture_full_bunch_motion)
% Gathers data on the machine environment.
% Runs a growdamp experiment on an already setup system.
% Saves the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       capture_full_bunch_motion (str): yes or no. Determines if the full
%           time series of bunch motion is captured and stored (large data).
%
% example mbf_growdamp_capture('x', 'no')

pv_head = pv_names.hardware_names.(mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(mbf_axis);
triggers = pv_names.tails.triggers;
Sequencer = pv_names.tails.Sequencer;
FIR = pv_names.tails.FIR;

% Getting feedback gain
growdamp.FIR_gain = [pv_head, FIR.gain];

start_state = get_variable([pv_head, Sequencer.start_state]);
% getting the state of the sequencer.
exp_state_names = cell(start_state, 1);
for n=start_state:-1:1
    entries = fieldnames(Sequencer.(['seq' num2str(n)]));
    for en = 1:length(entries)
    growdamp.(['seq' num2str(n), '_', entries{en}]) = get_variable([pv_head,...
        Sequencer.(['seq' num2str(n)]).(entries{en})]);
    end %for  
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
    set_variable({[pv_head_mem triggers.MEM.arm]},1);
else
    warning('Memory is not ready trying again')
    pause(5) % Letting the hardware sort itself out.
    temp1 = get_variable([pv_head_mem pv_names.tails.TRG.memory_status]);
    if ~strcmp(temp1, 'Idle') == 1
        set_variable({[pv_head_mem triggers.MEM.arm]},1);
    else
        error('growdamp:memoryNotReady', 'Memory is not ready please rerun')
    end %if
end %if

%Disarm, so that the current settings will be picked up upon arming.
set_variable([pv_head, triggers.SEQ.disarm], 1)

%% Trigger the measurement
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 's')
    chan = 0;
elseif strcmp(mbf_axis, 'y')
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
if strcmpi(capture_full_bunch_motion, 'yes')
    turn_count = 1250 .* 400;
    turn_offset = 0;
    growdamp.bunch_motion = mbf_read_mem(pv_head_mem, turn_count,'offset', turn_offset, 'channel', 0, 'lock', 60);
end


