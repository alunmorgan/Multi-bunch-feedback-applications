function mbf_growdamp_setup(mbf_axis, tune, varargin)
% Sets up the MBF system to be ready for a growdamp measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Tune of the machine.
%       varargin: other settings (dwell, excitation, etc)
%
% example: mbf_growdamp_setup('x', 0.17)
if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y') || strcmpi(mbf_axis, 'tx') || strcmpi(mbf_axis, 'ty')
    default_durations = [250, 250, 250, 500];
    default_dwell = 1;
    default_tune_sweep_range = [80.00500, 80.49500];
    default_tune_offset = 0;
    default_excitation_level = -18;
elseif strcmpi(mbf_axis, 's')
    default_durations = [10, 10, 50, 100];
    default_dwell = 480;
    default_tune_sweep_range = [80.00220, 80.00520];
    default_tune_offset = 0;
    default_excitation_level = -18;
else
    error('Incorrect axis selected. Should be x, y, s, tx, ty')
end %if
p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_durations = @(x) isnumeric(x) && length(x) == 4;
valid_number = @(x) isnumeric(x);
valid_sweep = @(x) isnumeric(x) && length(x) == 2;
addRequired(p, 'mbf_axis');
addRequired(p, 'tune', valid_number);
addParameter(p, 'durations', default_durations, valid_durations);
addParameter(p, 'dwell', default_dwell, valid_number);
addParameter(p, 'tune_sweep_range', default_tune_sweep_range, valid_sweep);
addParameter(p, 'tune_offset', default_tune_offset, valid_number);
addParameter(p, 'excitation_level', default_excitation_level, valid_number);

parse(p, mbf_axis, tune, varargin{:});


[~, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
settings = p.Results;
% Generate the base PV name.
pv_head = pv_names.hardware_names.(mbf_axis);
if strcmp(mbf_axis, 'x') || strcmp(mbf_axis, 'y')
    pv_head_mem = pv_names.hardware_names.('T');
elseif strcmp(mbf_axis, 's')
    pv_head_mem = pv_names.hardware_names.('L');
elseif strcmp(mbf_axis, 'tx') || strcmp(mbf_axis, 'ty')
    pv_head_mem = pv_names.hardware_names.('lab');
end %if
%% Set up triggering
% set up the appropriate triggering
% Stop triggering first, otherwise there's a good chance the first thing
% we'll do is loose the beam as we change things.
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    mbf_get_then_put([pv_head pv_names.tails.triggers.(trigger).enable_status], 'Ignore');
end %for
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    mbf_get_then_put([pv_head_mem pv_names.tails.triggers.MEM.(trigger).enable_status], 'Ignore');
    mbf_get_then_put([pv_head_mem pv_names.tails.triggers.MEM.(trigger).blanking_status], 'All');
end %for
% Set the trigger to one shot
mbf_get_then_put([pv_head pv_names.tails.triggers.SEQ.mode], 'One Shot');
mbf_get_then_put([pv_head_mem pv_names.tails.triggers.MEM.mode], 'One Shot');
% Set the triggering to Soft only
lcaPut([pv_head pv_names.tails.triggers.('SOFT').enable_status], 'Enable')
lcaPut([pv_head_mem pv_names.tails.triggers.MEM.('SOFT').enable_status], 'Enable')
%  set up the memory buffer to capture ADC data.
mbf_get_then_put([pv_head_mem, pv_names.tails.MEM.channel_select], 'ADC0/ADC1')
% Delay to make sure the currently set up sweeps have finished.
pause(1) % TODO look for system to be in bank 0.

%% Set up banks
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
% bunch bank 1 (the excitation)
mbf_set_bank(mbf_axis, 1, 4) %Sweep

% bunch bank 2 (the feedback)
mbf_set_bank(mbf_axis, 2, 1) %FIR

% bunch bank 0 (the resting condition)
mbf_set_bank(mbf_axis, 0, 1) %FIR

%% Set up states
% state 4
mbf_set_state(mbf_axis, 4,  tune, 1, ...
    [num2str(settings.excitation_level),'dB'], 'On', ...
    settings.durations(1), ...
    settings.dwell, 'Capture') %excitation
% state 3
mbf_set_state(mbf_axis, 3, tune, 1, ...
    '-48dB', 'Off', ...
    settings.durations(2), ...
    settings.dwell, 'Capture') %passive damping
% state 2
mbf_set_state(mbf_axis, 2, tune, 2, ...
    '-48dB', 'Off', ...
    settings.durations(3), ...
    settings.dwell, 'Capture') %active damping
% state 1
mbf_set_state(mbf_axis, 1, tune, 2, ...
    '-48dB', 'Off', ...
    settings.durations(4), ...
    settings.dwell, 'Discard') %Quiecent

% start state
mbf_get_then_put([pv_head pv_names.tails.Sequencer.start_state], 4);
% steady state bank
mbf_get_then_put([pv_head pv_names.tails.Sequencer.steady_state_bank], 'Bank 0');

% set the super sequencer to scan all modes.
mbf_get_then_put([pv_head pv_names.tails.Super_sequencer_count], harmonic_number);


%% Set up data capture
% Set the detector input to FIR
mbf_get_then_put([pv_head pv_names.tails.Detector.source], 'FIR');
% Enable only detector 0
for n_det = 0:3
    l_det = ['det',num2str(n_det)];
    mbf_get_then_put([pv_head  pv_names.tails.Detector.(l_det).enable], 'Disabled');
end %for
lcaPut([pv_head  pv_names.tails.Detector.('det0').enable], 'Enabled');
% Set the bunch mode to all bunches on detector 0
mbf_get_then_put([pv_head  pv_names.tails.Detector.('det0').bunch_selection], ones(936,1)');



