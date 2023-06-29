function tunescan_over_modes_all(mbf_axis, varargin)
% top level function to run the tunescan for all modes in the selected plane.
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

defaultPlotting = 'yes';
% experiment parameters
defaultNcap = 1001; % 4096; % 1001 takes ~ 3 minutes
defaultStartmode = 0;
defaultDriveBunches = 0:935;% 100
defaultFeedbackState = 'on';
if strcmpi(mbf_axis,'X')
    defaultStartFreq = 0.139;
    defaultEndFreq = 0.239;
elseif strcmpi(mbf_axis,'Y')
    defaultStartFreq = 0.227;
    defaultEndFreq = 0.327;
else
    disp('This currently only works for X and Y axes.')
    return
end

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'plotting', defaultPlotting, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'n_captures', defaultNcap);
addParameter(p, 'start_mode', defaultStartmode);
addParameter(p, 'drive_bunches', defaultDriveBunches);
addParameter(p, 'feedback_state', defaultFeedbackState, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'start_frequency', defaultStartFreq);
addParameter(p, 'end_frequency', defaultEndFreq);

parse(p, mbf_axis, varargin{:});

% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")
 tunes = get_all_tunes('xys');
 
exp_setup.n_captures = p.Results.n_captures;
exp_setup.start_mode = p.Results.start_mode;
exp_setup.drive_bunches = p.Results.drive_bunches;
exp_setup.feedback_state = p.Results.feedback_state;
exp_setup.start_frequency = p.Results.start_frequency;
exp_setup.end_frequency = p.Results.end_frequency;

mbf_tunescan_over_modes_setup(mbf_axis, exp_setup);
pause(2)
tunescan = mbf_tunescan_over_modes_capture(mbf_axis, tunes, exp_setup);
% reset the sweep
%%%%Is this section needed or does the TuneOnly script take care of things?
configure_tune_sweep(mbf_axis , 0:935, 1, 1, 0, 0, 0)
lcaPut([pv_head pv_names.tails.triggers.mode],'Rearm')
lcaPut([pv_head Sequencer.Base Sequencer.reset],1)
%%%%%%%

% Programatiaclly press the tune only button on each system
setup_operational_mode(mbf_axis, "TuneOnly")

if strcmp(p.Results.plotting, 'yes')
    mbf_tunescan_over_modes_plotting(tunescan)
end %if

