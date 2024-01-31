function sig = BBBFE_bunch_phase_variation_simulation(mbf_axis)
% This function moves the phase between -60 and +60 around the nominal phase.
% a gain ramp across the train is established using the FIR.
% For each phase value various DAC outputs are captured.
% The idea of this is to simulate the impact of a phase gradient across the
% bunch train.

[~, harmonic_number, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;
bbbfe_vars = pv_names.frontend;

fir_wf = get_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank0.FIR.gainwf]);
% put a ramp pattern on the FIR between 0 and 1
sig.fir_ramp = linspace(0, 1, harmonic_number);
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank0.FIR.gainwf], sig.fir_ramp)

% adjust the phase on the frontend between 0 and 60 in 10 degree steps.

starting_phase = get_variable([bbbfe_vars.base, bbbfe_vars.system_phase.(mbf_axis)]);
disp(['Starting phase: ', num2str(starting_phase)])
sig.phase_sweep = linspace(starting_phase -60, starting_phase +60, 12);

for phase_ind = 1:length(phase_sweep)
    % capture the DAC output
    set_variable([bbbfe_vars.base, bbbfe_vars.system_phase.(mbf_axis)], sig.phase_sweep(phase_ind));
    pause(5) % HOW LONG?
    sig.delta(phase_ind, :) = get_variable([mbf_names.(mbf_axis), mbf_vars.dac.delta]);
    sig.max(phase_ind, :) = get_variable([mbf_names.(mbf_axis), mbf_vars.dac.max]);
    sig.mean(phase_ind, :) = get_variable([mbf_names.(mbf_axis), mbf_vars.dac.mean]);
    sig.min(phase_ind, :) = get_variable([mbf_names.(mbf_axis), mbf_vars.dac.min]);
    sig.std(phase_ind, :) = get_variable([mbf_names.(mbf_axis), mbf_vars.dac.std]);
    pause(5) % HOW LONG?
end %for

% Put the phase back to the starting phase
set_variable([bbbfe_vars.base, bbbfe_vars.system_phase.(mbf_axis)], starting_phase);

% Remove the ramp from the FIR
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank0.FIR.gainwf], fir_wf)

