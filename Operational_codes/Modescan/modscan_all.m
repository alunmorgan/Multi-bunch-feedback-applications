function modscan_all(mbf_axis, varargin)
% top level function to run the modescan for all selected plane.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       plotting(str): set whether the data is plotted as well as saved. Default
%       is yes.
%       tunes (structure or NaN): Tune data from a previous measurement. 
%                                 Defaults to Nan.
%
% Example  modscan_all('x')
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

default_n_repeats = 10;
default_plotting = 'yes';
default_auto_setup = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'n_repeats', default_n_repeats, validScalarNum);
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

tunes = mbf_modescan_setup(mbf_axis, ...
    'auto_setup', p.Results.auto_setup, 'tunes', p.Results.tunes);
pause(2)
modescan = mbf_modescan_capture(mbf_axis, 'tunes', tunes, 'n_repeats', p.Results.n_repeats);

if strcmp(p.Results.auto_setup, 'yes')
    % Programatiaclly press the tune only button on each system
    setup_operational_mode(mbf_axis, "TuneOnly")
end %if

if strcmp(p.Results.plotting, 'yes')
    if ~isfield(modescan, 'harmonic_number')
        [~, modescan.harmonic_number, ~, ~] = mbf_system_config;
    end %if
    [data_magnitude, data_phase] = mbf_modescan_analysis(modescan);
    mbf_modescan_plotting(data_magnitude, data_phase, modescan)
end %if

