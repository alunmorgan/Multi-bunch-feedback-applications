function tunescan = mbf_tunescan_over_modes_capture(mbf_axis, pv_names)
% wrapper function to call tunescan, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%
% example data = mbf_tunescan_over_modes_capture('x', pv_names)

pv_head = pv_names.hardware_names.(mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(mbf_axis);
triggers = pv_names.tails.triggers;

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
% download the data
[tunescan.data, tunescan.scale, ~] = mbf_read_det(pv_head_mem,...
    'axis', chan, 'lock', mem_lock);