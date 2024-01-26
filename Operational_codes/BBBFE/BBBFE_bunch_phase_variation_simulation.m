function sig = BBBFE_bunch_phase_variation_simulation(ax)
% This function moves the phase between -60 and +60 around the nominal phase.
% a gain ramp across the train is established using the FIR.
% For each phase value various DAC outputs are captured.
% The idea of this is to simulate the impact of a phase gradient across the
% bunch train.

[~, harmonic_number, pv_names, ~] = mbf_system_config;

fir_wf = get_variable([pv_names.hardware_names.(ax),':BUN:0:FIR:GAIN_S']);
% put a ramp pattern on the FIR between 0 and 1
sig.fir_ramp = linspace(0, 1, harmonic_number);
set_variable([pv_names.hardware_names.(ax),':BUN:0:FIR:GAIN_S'], sig.fir_ramp)

% adjust the phase on the frontend between 0 and 60 in 10 degree steps.

starting_phase = get_variable(['SR23C-DI-BBFE-01:PHA:OFF:', upper(ax)]);
disp(['Starting phase: ', num2str(starting_phase)])
sig.phase_sweep = linspace(starting_phase -60, starting_phase +60, 12);

for phase_ind = 1:length(phase_sweep)
    % capture the DAC output
    set_variable(['SR23C-DI-BBFE-01:PHA:OFF:', upper(ax)], sig.phase_sweep(phase_ind));
    pause(5) % HOW LONG?
    sig.delta(phase_ind, :) = get_variable([pv_names.hardware_names.(ax),':DAC:MMS:DELTA']);
    sig.max(phase_ind, :) = get_variable([pv_names.hardware_names.(ax),':DAC:MMS:MAX']);
    sig.mean(phase_ind, :) = get_variable([pv_names.hardware_names.(ax),':DAC:MMS:MEAN']);
    sig.min(phase_ind, :) = get_variable([pv_names.hardware_names.(ax),':DAC:MMS:MIN']);
    sig.std(phase_ind, :) = get_variable([pv_names.hardware_names.(ax),':DAC:MMS:STD']);
    pause(5) % HOW LONG?
end %for

% Put the phase back to the starting phase
set_variable(['SR23C-DI-BBFE-01:PHA:OFF:', upper(ax)], starting_phase);

% Remove the ramp from the FIR
set_variable([pv_names.hardware_names.(ax),':BUN:0:FIR:GAIN_S'], fir_wf)

