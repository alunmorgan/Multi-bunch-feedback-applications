function modescan_all(mbf_axis, varargin)
% top level function to run the modescan for all selected plane.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%       is yes.
%
% Example  modscan_all('x')

[root_string, harmonic_number, ~, ~] = mbf_system_config;
root_string = root_string{1};

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);
addParameter(p, 'n_repeats', 10, validScalarNum);
addParameter(p, 'dwell', 500, validScalarNum);
addParameter(p, 'excitation_gain', -30, validScalarNum);

parse(p, mbf_axis, varargin{:});

filter_conditions = {};

% getting general environment data
modescan = machine_environment;

% Add the extra data to the data structure.
modescan.ax_label = mbf_axis;
modescan.base_name = ['Modescan_' mbf_axis '_axis'];
modescan.harmonic_number = harmonic_number;

if strcmp(auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

% Setup the MBF ready for the measurement.
mbf_modescan_setup(mbf_axis, p.Results.dwell, ...
    modescan.tunes.([mbf_axis,'_tune']).tune,...
    excitation_gain)
pause(2)

% Capturing data.
captured_data = mbf_modescan_capture(mbf_axis, p.Results.n_repeats);
% adding to output data structure.
data_fields = fieldnames(captured_data);
for je = 1:length(data_fields)
    modescan.(data_fields{je}) = captured_data.(data_fields{je});
end %for

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

%% saving the data to a file
save_to_archive(root_string, modescan)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, modescan)
end %if

%% Plotting data
if strcmp(p.Results.plotting, 'yes')
    mbf_modescan_archival_retrieval(mbf_axis, [modescan.time modescan.time],...
        filter_conditions)
end %if

