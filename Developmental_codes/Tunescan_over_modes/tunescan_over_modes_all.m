function tunescan_over_modes_all(mbf_axis, varargin)
% top level function to run the tunescan for all selected plane.
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

default_plotting = 'yes';

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'plotting', default_plotting, @(x) any(validatestring(x, boolean_string)));

parse(p, mbf_axis, varargin{:});

% experiment parameters
ncap        = 1001; % 4096; % 1001 takes ~ 3 minutes
startmode   = 0;
drive_bunch = 0:935;
% drive_bunch = 100;
fb_on_off   = 1;

if strcmpi(mbf_axis,'X')
    start_freq = 0.139;
    end_freq = 0.239;
else
    start_freq = 0.227;
    end_freq = 0.327;
end

% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")
 tunes = get_all_tunes('xys');
 
exp_setup.n_captures = n_cap;
exp_setup.start_mode = startmode;
exp_setup.drive_bunch = drive_bunch;
exp_setup.fb_on_off = fb_on_off;
exp_setup.start_frequency = start_freq;
exp_setup.end_frequency = end_freq;

mbf_tunescan_over_modes_setup(mbf_axis, 'drive_bunches', drive_bunch,...
    'fb_on_off', fb_on_off, 'start_mode', startmode,...
    'start_frequency', start_freq, 'end_frequency', end_freq, 'n_captures', ncap);
pause(2)
tunescan = mbf_tunescan_over_modes_capture(mbf_axis, tunes, exp_setup);
% reset the sweep
configure_tune_sweep(mbf_axis , 0:935, 1, 1, 0, 0, 0)
lcaPut([pv_head pv_names.tails.triggers.mode],'Rearm')
lcaPut([pv_head Sequencer.Base Sequencer.reset],1)
% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")

if strcmp(p.Results.plotting, 'yes')
    mbf_tunescan_over_modes_plotting(data_magnitude, data_phase, tunescan.harmonic_number)
end %if

