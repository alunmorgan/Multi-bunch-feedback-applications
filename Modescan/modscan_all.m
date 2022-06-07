function modscan_all(mbf_axis)
% top level function to run the modescan for all selected plane.
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));

parse(p, mbf_axis);
mbf_tools
% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode(mbf_axis, "TuneOnly")
% Get the tunes
tunes = get_all_tunes(mbf_axis);
tune = tunes.([mbf_axis,'_tune']).tune;

if isnan(tune)
    disp('Could not get tune value')
    return
end %if

mbf_modescan_setup(mbf_axis, tune)
modescan = mbf_modescan_capture(mbf_axis);
mbf_modescan_plotting(modescan)

% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")
