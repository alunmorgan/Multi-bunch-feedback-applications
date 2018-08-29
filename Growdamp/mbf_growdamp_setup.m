function mbf_growdamp_setup(mbf_axis, tune)
% Sets up the MBF system to be ready for a growdamp measurement.
%
%   Args:
%       mbf_axis (str): Selects which MBF axis to work on (x, y, s).
%       tune (float): Tune of the machine.
%
% example: mbf_growdamp_setup('x', 0.17)

[~, harmonic_number, pv_names, trigger_inputs] = mbf_system_config;
settings = mbf_growdamp_config(mbf_axis);
% Generate the base PV name.
pv_head = ax2dev(settings.axis_number);
%% Set up triggering
% set up the apropriate triggering
% Stop triggering first, otherwise there's a good chance the first thing
% we'll do is loose the beam as we change things.
for trigger_ind = 1:legnth(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    mbf_get_then_put([pv_head pv_names.tails.triggers.(trigger).enable_status], 'Ignore');
end

% Set the trigger to one shot
mbf_get_then_put([pv_head pv_names.tails.triggers.mode], 'One Shot');
% Set the triggering to Soft only
lcaPut([pv_head pv_names.tails.triggers.SOFT.enable_status], 'Enable')

%% Set up banks
% bunch output (0=off 1=FIR 2=NCO 3 =NCO+FIR 4=sweep 5=sweep+FIR 6=sweep+NCO 7=sweep+NCO+FIR)
% bunch bank 1 (the excitation)
mbf_set_bank(settings.axis_number, 1, 4) %Sweep

% bunch bank 2 (the feedback)
mbf_set_bank(settings.axis_number, 2, 1) %FIR

% bunch bank 0 (the resting condition)
mbf_set_bank(settings.axis_number, 0, 1) %FIR

% bank0=lcaGet([pv_head ':BUN:0:OUTWF_S']);
% bank0(1)=2; 
% mbf_get_then_put([pv_head ':BUN:0:OUTWF_S'], bank0);

%% Set up states
% state 4
 mbf_set_state(settings.axis_number, 4,  tune, 1, [num2str(settings.ex_level),'dB'], settings.durations(1), settings.dwell, 'Capture') %excitation
 % state 3
 mbf_set_state(settings.axis_number, 3, tune, 1, 'Off', settings.durations(2), settings.dwell, 'Capture') %passive damping
 % state 2
 mbf_set_state(settings.axis_number, 2, tune, 2, 'Off', settings.durations(3), settings.dwell, 'Capture') %active damping
 % state 1
 mbf_set_state(settings.axis_number, 1, tune, 2, 'Off', settings.durations(4), settings.dwell, 'Discard') %Quiecent

% start state
mbf_get_then_put([pv_head pv_names.tails.Sequencer_start_state], 4);
% steady state bank
mbf_get_then_put([pv_head pv_names.tails.Sequencer_steady_state_bank], 'Bank 0');

% set the super sequencer to scan all modes.
mbf_get_then_put([pv_head pv_names.tails.Super_sequencer_count], harmonic_number);


%% Set up data capture
% Set the detector input to FIR
mbf_get_then_put([pv_head pv_names.tails.Detector.source]);
% Enable only detector 0
for n_det = 0:3
    l_det = num2str(n_det);
    mbf_get_then_put([pv_head  pv_names.tails.Detector.(l_det).enable], 'Disabled');
end
lcaPut([pv_head  pv_names.tails.Detector.(0).enable], 'Enabled');
% Set the bunch mode to all bunches on detector 0
mbf_get_then_put([pv_head  pv_names.tails.Detector.(0).bunch_selection], ones(936,1));



