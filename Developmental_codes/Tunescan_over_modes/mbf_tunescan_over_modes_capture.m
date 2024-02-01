function tunescan = mbf_tunescan_over_modes_capture(mbf_axis, tunes, exp_setup)
% wrapper function to call tunescan, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (structure): The fractional tunes of the machine.
%
% example data = mbf_tunescan_capture('x', 0.17)

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('TunescanOverModes:IOError', 'mbf_tunescan_capture: Incorrect value axis given (should be x, y or s)');
end %if

% getting general environment data
tunescan = machine_environment('tunes', tunes);
% Adding details of teh experimental setup.
tunescan.exp_setup = exp_setup;

[root_string, tunescan.harmonic_number, pv_names] = mbf_system_config;

root_string = root_string{1};

pv_head = pv_names.hardware_names.(mbf_axis);

% Add the axis label to the data structure.
tunescan.ax_label = mbf_axis;
% construct name and add it to the structure
tunescan.base_name = ['tunescan_' tunescan.ax_label '_axis'];

% start the multi-mode sweep
set_variable([pv_head pv_names.tails.triggers.arm], 1)

% download the data
% (Eww.  Convert axis string into 0 or 1.)
det_axis = find('XY' == mbf_axis) - 1;
[tunescan.data, tunescan.scale] = mbf_read_det('SR23C-DI-TMBF-01', 'axis', det_axis, 'lock', 1800 );

%% saving the data to a file
save_to_archive(root_string, tunescan)
