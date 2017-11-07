function modescan = mbf_modescan_capture(mbf_axis, tune)
% wrapper function to call modescan, gather data on the environment
% and to save the resultant data. 
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Usually the fractional tune of the machine.
%
% example data = mbf_modescan_capture('x', 0.17)

if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('mbf_growdamp_capture: Incorrect value axis given (should be x, y or s)');
end %if

[root_string, ~, pv_names] = mbf_system_config;
root_string = root_string{1};
settings = mbf_modescan_config(mbf_axis);
% Generate the base PV name.
pv_head = ax2dev(settings.axis_number);

% getting general environment data
modescan = machine_environment;
% Add the axis label to the data structure.
modescan.ax_label = settings.axis_label;
% construct name and add it to the structure
modescan.base_name = ['Modescan_' modescan.ax_label '_axis'];

modescan.tune = tune;
% setting up the sequencer for modescans
if isnan(modescan.tune)
    disp('mbf_modescan_capture: No valid tune. Stopping')
    return
end
mbf_modescan_setup(ax, modescan.tune)
% starting modescan capture
pause(2)
iq(1,:) = [1 1i]*lcaGet({[pv_head, pv_names.tails.Detector_I];...
                         [pv_head, pv_names.tails.Detector_Q]});
for nsd = 1:10
    iq(nsd,1:size(iq,2)) = [1 1i]*lcaGet({[pv_head, pv_names.tails.Detector_I];...
                                          [pv_head, pv_names.tails.Detector_Q]});
    pause(0.2)
end
modescan.iq = mean(iq,1);
modescan.f_scale = lcaGet([pv_head, pv_names.tails.Detector_scale]);

%% saving the data to a file
save_to_archive(root_string, modescan)

