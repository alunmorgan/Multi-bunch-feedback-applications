function tunescan_over_modes_all(mbf_axis, varargin)
% top level function to run the tunescan for all selected plane.
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

tunes = mbf_tunescan_over_modes_setup(mbf_axis);
pause(2)
tunescan = mbf_tunescan_over_modes_capture(mbf_axis, p.Results.n_repeats);
tunescan.tunes = tunes;
% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")

if strcmp(p.Results.plotting, 'yes')
    [data_magnitude, data_phase] = mbf_tunescan_over_modes_analysis(tunescan);
    mbf_tunescan_over_modes_plotting(data_magnitude, data_phase, tunescan.harmonic_number)
end %if

