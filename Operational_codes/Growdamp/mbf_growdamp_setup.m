function mbf_growdamp_setup(mbf_axis, states, excitation_tune, pll_setup,...
    bunch_monitor)
% Sets up the MBF system to be ready for a growdamp measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       states (cell(structs)): Setup details of individual states.
%       excitation_tune (float) : The excitation location in tune space.
%       pll_setup (struct): Setup details for the PLL.
%       bunch_monitor (list(int)): Locations of the bunches to be monitored.
%                                  Defaults to all bunches.
%
% example: mbf_growdamp_setup('x')

[~, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
mbf_tools

pv_head = pv_names.hardware_names.(mbf_axis);
pv_head_mem = pv_names.hardware_names.mem.(mbf_axis);
triggers = pv_names.tails.triggers;
memory = pv_names.tails.MEM;
Sequencer = pv_names.tails.Sequencer;
Detector = pv_names.tails.Detector;
Bunch_bank = pv_names.tails.Bunch_bank;
NCO2 = pv_names.tails.NCO2;

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

% bunch bank 2 (the feedback)
mbf_set_bank(mbf_axis, 2, 1) %FIR

% bunch bank 1 (the excitation)
mbf_set_bank(mbf_axis, 1, 4) %Sweep

% bunch bank 0 (the resting condition)
mbf_set_bank(mbf_axis, 0, 1) %FIR

%% Set up states
%(ax, state, tune, bank, gain, enable, duration, dwell, capture)
for st = 1:length(states)
    mbf_set_state(mbf_axis, st,  excitation_tune, states{st})
end %for

% start state
set_variable([pv_head Sequencer.start_state], length(states));

% steady state bank
set_variable([pv_head Sequencer.steady_state_bank], 'Bank 0');

% set the super sequencer to scan all modes.
if isnan(p.Results.single_mode)
    set_variable([pv_head pv_names.tails.Super_sequencer_count], harmonic_number);
else
    set_variable([pv_head pv_names.tails.Super_sequencer_count], 1);
end %if

if strcmp(pll_setup.pll_tracking, 'yes')
    mbf_fll_setup('x', pll_setup.pll_bunches, pll_setup.pll_guard_bunches)
    set_variable([pv_head, NCO2.PLL_follow], 'Follow');
    set_variable([pv_head, NCO2.gaindb],-30);
    fillx = get_variable([pv_head, Bunch_bank.bank1.SEQ_enablewf]);
    set_variable([pv_head, Bunch_bank.bank0.NCO2_enablewf], fillx)
    set_variable([pv_head, Bunch_bank.bank1.NCO2_enablewf], fillx)
    set_variable([pv_head, NCO2.enable],'On');
end %if

%% Set up the detector.
% Set the detector input to FIR
set_variable([pv_head Detector.source], 'FIR');
% Enable only detector 0
for n_det = 0:3
    l_det = ['det',num2str(n_det)];
    set_variable([pv_head  Detector.(l_det).enable], 'Disabled');
end %for
set_variable([pv_head  Detector.det0.enable], 'Enabled');
% Set which bunches detector 0 records.
set_variable([pv_head  Detector.det0.bunch_selection], bunch_monitor');

