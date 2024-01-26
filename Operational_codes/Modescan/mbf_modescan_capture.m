function varargout = mbf_modescan_capture(mbf_axis, varargin)
% wrapper function to call modescan, gather data on the environment
% and to save the resultant data.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tunes (structure): The fractional tunes of the machine.
%       n_repeats (int): The number of repeat datapoints to capture
%   Returns:
%       modescan (struct): data structure containing the experimental
%                          results and the machine conditions.
%                          [optional output]
%
% example data = mbf_modescan_capture('x')
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'tunes',NaN);
addParameter(p, 'n_repeats', 1, valid_number);


parse(p, mbf_axis, varargin{:});
if ~strcmpi(mbf_axis, 'x')&& ~strcmpi(mbf_axis, 'y') && ~strcmpi(mbf_axis, 's')
    error('modescan:invalidAxis', 'mbf_modescan_capture: Incorrect value axis given (should be x, y or s)');
end %if

% getting general environment data
modescan = machine_environment('tunes', p.Results.tunes);

[root_string, modescan.harmonic_number, pv_names] = mbf_system_config;

root_string = root_string{1};

pv_head = pv_names.hardware_names.(mbf_axis);

% Add the axis label to the data structure.
modescan.ax_label = mbf_axis;
% construct name and add it to the structure
modescan.base_name = ['Modescan_' modescan.ax_label '_axis'];

for hs = 1:p.Results.n_repeats
    modescan.magnitude{hs} = get_variable([pv_head, ':TUNE:DMAGNITUDE']);
    modescan.phase{hs} = get_variable([pv_head, ':TUNE:DPHASE']);
end %for


%% saving the data to a file
save_to_archive(root_string, modescan)

if nargout == 1
    varargout{1} = modescan;
end %if