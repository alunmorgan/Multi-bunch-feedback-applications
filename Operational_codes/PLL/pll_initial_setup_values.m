function pll_initial_setup_values(mbf_axis)

% Some setup with 'working values'. These ought to be read from a
% config file or be additional arguments in the future.
% mbf_axis(str): xys

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.mode],'ADC no fill');
set_variable([mbf_names.(mbf_axis) mbf_vars.adc.reject_count],'128 turns');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.scaling],'48dB');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.blanking],'Blanking');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.minumum_magnitude],0);

if contains(name, 'TMBF')
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.i],1000); %safe also for for low charge, sharp resonance
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.p],0);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.dwell],128);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.maximum_offset],0.02);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.target_phase],-180);
elseif contains(mbf_names.(mbf_axis), 'LMBF')
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.i],100); %safe also for for low charge, sharp resonance
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.p],0);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.dwell],128);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.maximum_offset],0.001);
    set_variable([mbf_names.(mbf_axis) mbf_vars.pll.target_phase],-5);
end %if