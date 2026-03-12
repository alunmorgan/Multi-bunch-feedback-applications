function varargout = mbf_spectrum_all(varargin)
% Top level function to run all spectral measurements on all planes.
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

default_plotting = 'yes';
default_auto_setup = 'yes';
valid_number = @(x) isnumeric(x);

addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'n_turns', 1000, valid_number);
addParameter(p, 'repeat', 1, valid_number);

parse(p, varargin{:});

[root_string, harmonic_number, pv_names, ~] = mbf_system_config;
root_string = root_string{1};
spectrum = machine_environment;
spectrum.n_turns = n_turns;
spectrum.time = datevec(datetime("now"));
spectrum.repeat = repeat;
spectrum.harmonic_number = harmonic_number;
spectrum.base_name = ['Spectrum_', mbf_axis, '_axis'];

x_return_state = get_operational_mode('x');
y_return_state = get_operational_mode('y');
s_return_state = get_operational_mode('s');

if strcmp(p.Results.auto_setup, 'no')
    spectrum.mbf_state.x = x_return_state;
    spectrum.mbf_state.y = y_return_state;
    spectrum.mbf_state.s = s_return_state;
elseif  strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode('x', "TuneOnly")
    setup_operational_mode('y', "TuneOnly")
    setup_operational_mode('s', "TuneOnly")
    spectrum.mbf_state.x = "TuneOnly";
    spectrum.mbf_state.y = "TuneOnly";
    spectrum.mbf_state.s = "TuneOnly";
end %if

mbf_spectrum_setup('x');
mbf_spectrum_setup('y');
mbf_spectrum_setup('s');

spectrum.raw_data  = mbf_spectrum_capture(p.Results.n_turns,...
    p.Results.repeat, pv_names);

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode('x', x_return_state)
    setup_operational_mode('y', y_return_state)
    setup_operational_mode('s', s_return_state)
end %if

%% saving the data to a file
save_to_archive(root_string, spectrum)
if nargout == 1
    varargout{1} = spectrum;
end %if

if strcmp(p.Results.plotting, 'yes')
    fold = 1;
    analysed.x_axis = mbf_spectrum_analysis(spectrum.raw_data.x_data, fold);
    analysed.y_axis = mbf_spectrum_analysis(spectrum.raw_data.y_data, fold);
    analysed.s_axis = mbf_spectrum_analysis(spectrum.raw_data.s_data, fold);

    mbf_spectrum_plotting(analysed, spectrum.current, spectrum.time)
end %if