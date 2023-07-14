function mbf_spectrum_all(mbf_axis, varargin)
% Top level function to run all spectral measurements on selected plane.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%       is yes.
%       tunes (structure or NaN): Tune data from a previous measurement. 
%                                 Defaults to Nan.
% 
% Example mbf_spectrum_all('x')
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

default_plotting = 'yes';
default_auto_setup = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

tunes = mbf_spectrum_setup(mbf_axis, ...
    'auto_setup', p.Results.auto_setup, 'tunes', p.Results.tunes);
n_turns = 100;
repeat = 1;
data = mbf_spectrum_capture(mbf_axis, 'tunes', tunes, 'n_turns', n_turns, 'repeat', repeat);
data.tunes = tunes;

if strcmp(p.Results.auto_setup, 'yes')
    % Programatically press the tune only button on each system.
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

if strcmp(p.Results.plotting, 'yes')
    fold = 1;
    analysed_data = mbf_spectrum_analysis(data, fold);
    mbf_spectrum_plotting(analysed_data, data.meta_data)
end %if