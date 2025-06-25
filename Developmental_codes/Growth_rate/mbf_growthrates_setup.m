function [tunes, orig_fir_gain] = mbf_growthrates_setup(mbf_axis, varargin)
% Sets up the MBF system to be ready for a growth rates measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       durations (list of ints): number of turns for excitation,
%                                 pasive daming and active damping
%       dwell (int): number of turns at each point.
%       tune_sweep_range (list of floats), tune range to sweep over
%       tune_offset (float): Tune fraction to offset from the peak.
%       single_mode(int): The mode you want to operate on.
%       auto_setup(str): sets whether the setup scripts will be used to put the
%       system into a particular state. Default is yes.
%       tunes (structure or NaN): Tune data from a previous measurement. 
%                                 Defaults to Nan.
%   Returns:
%       tunes (structure): Tunes of the machine.
%       orig_fir_gain (float): the FIR gain before the meausurement.
%
% example: mbf_growthrates_setup('x')

if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y') || strcmpi(mbf_axis, 'tx') || strcmpi(mbf_axis, 'ty')
    default_durations = [2500, 2000];
    default_dwell = 1;
    default_tune_sweep_range = [80.00500, 80.49500];
    default_tune_offset = 0;
elseif strcmpi(mbf_axis, 's')
    default_durations = [10, 100];
    default_dwell = 480;
    default_tune_sweep_range = [80.00220, 80.00520];
    default_tune_offset = 0;
else
    error('growdamp:setup:invalidAxis', 'Incorrect axis selected. Should be x, y, s, tx, ty')
end %if

default_auto_setup = 'yes';

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_durations = @(x) isnumeric(x) && length(x) == 4;
valid_number = @(x) isnumeric(x);
valid_sweep = @(x) isnumeric(x) && length(x) == 2;
boolean_string = {'yes', 'no'};

addRequired(p, 'mbf_axis');
addParameter(p, 'durations', default_durations, valid_durations);
addParameter(p, 'dwell', default_dwell, valid_number);
addParameter(p, 'tune_sweep_range', default_tune_sweep_range, valid_sweep);
addParameter(p, 'tune_offset', default_tune_offset, valid_number);
addParameter(p, 'single_mode', NaN, valid_number);
addParameter(p, 'auto_setup', default_auto_setup, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'tunes', NaN);

parse(p, mbf_axis, varargin{:});

mbf_tools

if isstruct(p.Results.tunes)
    tunes = p.Results.tunes;
else
        % Get the tunes
    tunes = get_all_tunes;
end %if
tune = tunes.([mbf_axis,'_tune']).tune;

if isnan(tune)
    disp('Could not get all tune values')
    orig_fir_gain = NaN;
    return
end %if

[~, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
settings = p.Results;

pv_head = pv_names.hardware_names.(settings.mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(settings.mbf_axis);
triggers = pv_names.tails.triggers;
memory = pv_names.tails.MEM;
Sequencer = pv_names.tails.Sequencer;
Detector = pv_names.tails.Detector;
Bunch_bank = pv_names.tails.Bunch_bank;

% Get the current FIR gain
orig_fir_gain = get_variable([pv_head, Bunch_bank.FIR_gains]);

if strcmp(p.Results.auto_setup, 'yes')
    % putting the system into a known state.
    setup_operational_mode(mbf_axis, "Feedback")
    % Setting the FIR gain to its original value.
    set_variable([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)
end %if

% Change the tune to be around the chosen mode.
if ~isnan(settings.single_mode)
    tune = ...
        settings.single_mode + mod(tune,1);
end %if

%% Set up triggering
% set up the appropriate triggering
% Stop triggering first, otherwise there's a good chance the first thing
% we'll do is loose the beam as we change things.
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    set_variable([pv_head triggers.(trigger).enable_status], 'Ignore');
end %for
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    set_variable([pv_head_mem triggers.MEM.(trigger).enable_status], 'Ignore');
    set_variable([pv_head_mem triggers.MEM.(trigger).blanking_status], 'All');
end %for
% Set the trigger to one shot
set_variable([pv_head triggers.SEQ.mode], 'One Shot');
set_variable([pv_head_mem triggers.MEM.mode], 'One Shot');
% Set the triggering to Soft only
set_variable([pv_head triggers.('SOFT').enable_status], 'Enable')
set_variable([pv_head_mem triggers.MEM.('SOFT').enable_status], 'Enable')
%  set up the memory buffer to capture ADC data.
set_variable([pv_head_mem, memory.channel_select], 'ADC0/ADC1')
% Delay to make sure the currently set up sweeps have finished.
pause(1) % TODO look for system to be in bank 0.

%% Set up banks
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
% bunch bank 1 (the excitation)
mbf_set_bank(settings.mbf_axis, 1, 4) %Sweep

% bunch bank 0 (the resting condition)
mbf_set_bank(settings.mbf_axis, 0, 1) %FIR

%% Set up states
% state 2
mbf_set_state(settings.mbf_axis, 2,  tune, 1, ...
    '-48dB', 'Off', ...
    settings.durations(1), ...
    settings.dwell, 'Capture') %Growth
% state 1
mbf_set_state(settings.mbf_axis, 1, tune, 0, ...
    '-48dB', 'Off', ...
    settings.durations(2), ...
    settings.dwell, 'Capture') %Feedback

% start state
set_variable([pv_head Sequencer.start_state], 2);
% steady state bank
set_variable([pv_head Sequencer.steady_state_bank], 'Bank 0');

% set the super sequencer to scan all modes.
if isnan(p.Results.single_mode)
    set_variable([pv_head pv_names.tails.Super_sequencer_count], harmonic_number);
else
    set_variable([pv_head pv_names.tails.Super_sequencer_count], 1);
end %if

%% Set up data capture
% Set the detector input to FIR
set_variable([pv_head Detector.source], 'FIR');
% Enable only detector 0
for n_det = 0:3
    l_det = ['det',num2str(n_det)];
    set_variable([pv_head  Detector.(l_det).enable], 'Disabled');
end %for
set_variable([pv_head  Detector.('det0').enable], 'Enabled');
% Set the bunch mode to all bunches on detector 0
set_variable([pv_head  Detector.('det0').bunch_selection], ones(harmonic_number,1)');

