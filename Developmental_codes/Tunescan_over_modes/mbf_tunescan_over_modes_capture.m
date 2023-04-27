function tunescan = mbf_tunescan_over_modes_capture(mbf_axis, n_repeats)
% wrapper function to call tunescan, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Usually the fractional tune of the machine.
%
% example data = mbf_tunescan_capture('x', 0.17)

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('mbf_tunescan_capture: Incorrect value axis given (should be x, y or s)');
end %if

% getting general environment data
tunescan = machine_environment;

[root_string, tunescan.harmonic_number, pv_names] = mbf_system_config;

root_string = root_string{1};

pv_head = pv_names.hardware_names.(mbf_axis);

% Add the axis label to the data structure.
tunescan.ax_label = mbf_axis;
% construct name and add it to the structure
tunescan.base_name = ['tunescan_' tunescan.ax_label '_axis'];

for hs = 1:n_repeats
    tunescan.magnitude{hs} = lcaGet([pv_head, ':TUNE:DMAGNITUDE']);
    tunescan.phase{hs} = lcaGet([pv_head, ':TUNE:DPHASE']);
end %for


%% saving the data to a file
save_to_archive(root_string, tunescan)

