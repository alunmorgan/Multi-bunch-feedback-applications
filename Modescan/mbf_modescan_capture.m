function modescan = mbf_modescan_capture(mbf_axis)
% wrapper function to call modescan, gather data on the environment
% and to save the resultant data. 
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Usually the fractional tune of the machine.
%
% example data = mbf_modescan_capture('x', 0.17)

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('mbf_modescan_capture: Incorrect value axis given (should be x, y or s)');
end %if

[root_string, ~, pv_names] = mbf_system_config;
root_string = root_string{1};
% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);
% getting general environment data
modescan = machine_environment;
% Add the axis label to the data structure.
modescan.ax_label = mbf_axis;
% construct name and add it to the structure
modescan.base_name = ['Modescan_' modescan.ax_label '_axis'];

% modescan.tune = tune;
% % setting up the sequencer for modescans
% if isnan(modescan.tune)
%     disp('mbf_modescan_capture: No valid tune. Stopping')
%     return
% end
% mbf_modescan_setup(ax, modescan.tune)
% starting modescan capture
% pause(2)
modescan.magnitude = lcaGet([pv_head, ':TUNE:DMAGNITUDE']);
modescan.phase = lcaGet([pv_head, ':TUNE:DPHASE']);


%% saving the data to a file
save_to_archive(root_string, modescan)

