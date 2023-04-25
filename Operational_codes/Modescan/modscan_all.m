function modscan_all(mbf_axis, varargin)
% top level function to run the modescan for all selected plane.
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};
validScalarNum = @(x) isnumeric(x) && isscalar(x);

default_n_repeats = 10;
default_plotting = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'n_repeats', default_n_repeats, validScalarNum);
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));


parse(p, mbf_axis, varargin{:});
mbf_tools
% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode(mbf_axis, "TuneOnly")
% Get the tunes
tunes = get_all_tunes('xys');
tune = tunes.([mbf_axis,'_tune']).tune;

if isnan(tune)
    disp('Could not get tune value')
    return
end %if

mbf_modescan_setup(mbf_axis, tune)
pause(2)
modescan = mbf_modescan_capture(mbf_axis, p.Results.n_repeats);
modescan.tunes = tunes;
% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")

if strcmp(p.Results.plotting, 'yes')
    [data_magnitude, data_phase] = mbf_modescan_analysis(modescan);
    mbf_modescan_plotting(data_magnitude, data_phase, modescan.harmonic_number)
end %if

