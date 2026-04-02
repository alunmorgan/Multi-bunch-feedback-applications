function modescan = mbf_modescan_capture(mbf_axis, n_repeats)
% wrapper function to call modescan, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       n_repeats (int): The number of repeat datapoints to capture
%   Returns:
%       modescan (struct): data structure containing the experimental
%                          results and the machine conditions.
%                          [optional output]
%
% example data = mbf_modescan_capture('x', 100)

[~, ~, pv_names] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);

for hs = 1:n_repeats
    modescan.magnitude{hs} = get_variable([pv_head, ':TUNE:DMAGNITUDE']);
    modescan.phase{hs} = get_variable([pv_head, ':TUNE:DPHASE']);
end %for
