function [tunes, orig_fir_gain] = mbf_growdamp_setup(mbf_axis, varargin)
% Sets up the MBF system to be ready for a growdamp measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       durations (list of ints): number of turns for excitation, 
%                                 pasive daming and active damping
%       dwell (int): number of turns at each point.
%       tune_sweep_range (list of floats), tune range to sweep over
%       tune_offset (float): Tune fraction to offset from the peak.
%       excitation_level (float): Strength of the excitation oscillation.
%       fll_tracking (str): yes or no.
%       fll_bunches (float): bunches the fll is active on.
%       fll_guard_bunches (float): the number of bunches surrounding the fll
%                                  bunches for which feedback is switched off.
%       single_mode(int): The mode you want to operate on.
%   Returns:
%       tunes (structure): Tunes of the machine.
%       orig_fir_gain (float): the FIR gain before the meausurement.
%
% example: mbf_growdamp_setup('x')

if strcmpi(mbf_axis, 'x') || strcmpi(mbf_axis, 'y') || strcmpi(mbf_axis, 'tx') || strcmpi(mbf_axis, 'ty')
    default_durations = [250, 500, 500, 2000];
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
binary_string = {'yes', 'no'};

addRequired(p, 'mbf_axis');
addParameter(p, 'durations', default_durations, valid_durations);
addParameter(p, 'dwell', default_dwell, valid_number);
addParameter(p, 'tune_sweep_range', default_tune_sweep_range, valid_sweep);
addParameter(p, 'tune_offset', default_tune_offset, valid_number);
addParameter(p, 'excitation_level', default_excitation_level, valid_number);
addParameter(p, 'fll_tracking', 'no', @(x) any(validatestring(x,binary_string)));
addParameter(p, 'fll_bunches', 400, valid_number);
addParameter(p, 'fll_guard_bunches', 10, valid_number);
addParameter(p, 'single_mode', NaN, valid_number);

parse(p, mbf_axis, varargin{:});

mbf_tools

% Get the tunes
tunes = get_all_tunes('xys');
tune = tunes.([mbf_axis,'_tune']).tune;

if isnan(tune)
    disp('Could not get all tune values')
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
NCO = pv_names.tails.NCO;

% Get the current FIR gain
orig_fir_gain = lcaGet([pv_head, Bunch_bank.FIR_gains]);

% putting the system into a known state.
setup_operational_mode(mbf_axis, "Feedback")
% Setting the FIR gain to its original value.
lcaPut([pv_head, Bunch_bank.FIR_gains], orig_fir_gain)


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
    lcaPut([pv_head triggers.(trigger).enable_status], 'Ignore');
end %for
for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    lcaPut([pv_head_mem triggers.MEM.(trigger).enable_status], 'Ignore');
    lcaPut([pv_head_mem triggers.MEM.(trigger).blanking_status], 'All');
end %for
% Set the trigger to one shot
lcaPut([pv_head triggers.SEQ.mode], 'One Shot');
lcaPut([pv_head_mem triggers.MEM.mode], 'One Shot');
% Set the triggering to Soft only
lcaPut([pv_head triggers.('SOFT').enable_status], 'Enable')
lcaPut([pv_head_mem triggers.MEM.('SOFT').enable_status], 'Enable')
%  set up the memory buffer to capture ADC data.
lcaPut([pv_head_mem, memory.channel_select], 'ADC0/ADC1')
% Delay to make sure the currently set up sweeps have finished.
pause(1) % TODO look for system to be in bank 0.

%% Set up banks
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
% bunch bank 1 (the excitation)
mbf_set_bank(settings.mbf_axis, 1, 4) %Sweep

% bunch bank 2 (the feedback)
mbf_set_bank(settings.mbf_axis, 2, 1) %FIR

% bunch bank 0 (the resting condition)
mbf_set_bank(settings.mbf_axis, 0, 1) %FIR

%% Set up states
% state 4
mbf_set_state(settings.mbf_axis, 4,  tune, 1, ...
    [num2str(settings.excitation_level),'dB'], 'On', ...
    settings.durations(1), ...
    settings.dwell, 'Capture') %excitation
% state 3
mbf_set_state(settings.mbf_axis, 3, tune, 1, ...
    '-48dB', 'Off', ...
    settings.durations(2), ...
    settings.dwell, 'Capture') %passive damping
% state 2
mbf_set_state(settings.mbf_axis, 2, tune, 2, ...
    '-48dB', 'Off', ...
    settings.durations(3), ...
    settings.dwell, 'Capture') %active damping
% state 1
mbf_set_state(settings.mbf_axis, 1, tune, 2, ...
    '-48dB', 'Off', ...
    settings.durations(4), ...
    settings.dwell, 'Discard') %Quiecent

% start state
lcaPut([pv_head Sequencer.start_state], 4);
% steady state bank
lcaPut([pv_head Sequencer.steady_state_bank], 'Bank 0');

% set the super sequencer to scan all modes.
if isnan(p.Results.single_mode)
    lcaPut([pv_head pv_names.tails.Super_sequencer_count], harmonic_number);
else
    lcaPut([pv_head pv_names.tails.Super_sequencer_count], 1);
end %if


if strcmp(p.Results.fll_tracking, 'yes')
    mbf_fll_setup('x', p.Results.fll_bunches, p.Results.fll_guard_bunches)
    lcaPut([pv_head, NCO.Base,'2', NCO.PLL_follow], 'Follow');
    lcaPut([pv_head, NCO.Base,'2', NCO.gaindb],-30);
    fillx=lcaGet([pv_head, Bunch_bank.Base, ':1', Bunch_bank.SEQ_enable]);
    lcaPut([pv_head, Bunch_bank.Base,':0', Bunch_bank.NCO2_enable], fillx)
    lcaPut([pv_head, Bunch_bank.Base,':1', Bunch_bank.NCO2_enable], fillx)
    lcaPut([pv_head, NCO.Base,'2', NCO.enable],'On');
end %if
%% Set up data capture
% Set the detector input to FIR
lcaPut([pv_head Detector.source], 'FIR');
% Enable only detector 0
for n_det = 0:3
    l_det = ['det',num2str(n_det)];
    mbf_get_then_put([pv_head  Detector.(l_det).enable], 'Disabled');
end %for
lcaPut([pv_head  Detector.('det0').enable], 'Enabled');
% Set the bunch mode to all bunches on detector 0
lcaPut([pv_head  Detector.('det0').bunch_selection], ones(936,1)');

