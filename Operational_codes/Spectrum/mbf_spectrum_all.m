function varargout = mbf_spectrum_all(mbf_axis, varargin)
% Top level function to run all spectral measurements on selected plane.
% Args:
%       auto_setup(str): sets whether the setup scripts will be used to put the
%                        system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%                      is yes.
%       n_turns (int): number of turns to capture. Default is 1000.
%       repeat (int): Number of repeat points. Default is 1.
%
% Example mbf_spectrum_all
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};
axis_string = {'x', 'y', 's'};
valid_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'auto_setup', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'n_turns', 1000, valid_number);
addParameter(p, 'repeat', 1, valid_number);
addParameter(p, 'plotting', 'yes', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'additional_save_location', NaN);

parse(p, mbf_axis, varargin{:});

[root_string, harmonic_number, pv_names, ~] = mbf_system_config;
root_string = root_string{1};

% getting general environment data.
spectrum = machine_environment;

% Add the extra data to the data structure.
spectrum.n_turns = p.Results.n_turns;
spectrum.time = datevec(datetime("now"));
spectrum.repeat = p.Results.repeat;
spectrum.harmonic_number = harmonic_number;
spectrum.base_name = ['Spectrum_',mbf_axis '_axis'];

if  strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
    spectrum.mbf_state = "TuneOnly";
end %if

spectrum.mbf_state = get_operational_mode(mbf_axis);

mbf_spectrum_setup(mbf_axis);

spectrum.raw_data  = mbf_spectrum_capture(p.Results.n_turns,...
    p.Results.repeat, pv_names);

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, spectrum.mbf_state)
end %if

%% saving the data to a file
save_to_archive(root_string, spectrum)
if ~isnan(p.Results.additional_save_location)
    save(additional_save_location, spectrum)
end %if

if strcmp(p.Results.plotting, 'yes')
    conditioned_data = mbf_spectra_archival_retrieval(mbf_axis, [spectrum.time spectrum.time])
    analysed.x_axis = mbf_spectrum_analysis(spectrum.raw_data.x_data, spectrum.n_turns, spectrum.repeat, spectrum.harmonic_number, spectrum.RF);
    analysed.y_axis = mbf_spectrum_analysis(spectrum.raw_data.y_data, spectrum.n_turns, spectrum.repeat, spectrum.harmonic_number, spectrum.RF);
    analysed.s_axis = mbf_spectrum_analysis(spectrum.raw_data.s_data, spectrum.n_turns, spectrum.repeat, spectrum.harmonic_number, spectrum.RF);

    mbf_spectrum_plotting(analysed, spectrum.current, spectrum.time)
end %if