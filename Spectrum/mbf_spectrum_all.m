function mbf_spectrum_all(mbf_axis)
% Top level function to run all spectral measurements on selected plane.

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));

parse(p, mbf_axis);
mbf_tools

% Programatically press the tune only button on each system.
setup_operational_mode(mbf_axis, "TuneOnly")

mbf_spectrum_setup(mbf_axis)
data = mbf_spectrum_capture(mbf_axis, n_turns, repeat);
analysed_data = mbf_spectrum_analysis(data, fold);
mbf_spectrum_plotting(analysed_data, data.meta_data)

% Programatically press the tune only button on each system.
setup_operational_mode(mbf_axis, "TuneOnly")