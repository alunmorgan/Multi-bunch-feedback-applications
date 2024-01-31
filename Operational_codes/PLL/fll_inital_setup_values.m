function fll_inital_setup_values(mbf_axis)

% Some setup with 'working values'. These ought to be read from a
% config file or be additional arguments in the future.
% mbf_axis(str): xys

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
% mbf_vars = pv_names.tails;

set_variable([mbf_names.(mbf_axis) ':PLL:DET:SELECT_S'],'ADC no fill');
set_variable([mbf_names.(mbf_axis) ':ADC:REJECT_COUNT_S'],'128 turns');
set_variable([mbf_names.(mbf_axis) ':PLL:DET:SCALING_S'],'48dB');
set_variable([mbf_names.(mbf_axis) ':PLL:DET:BLANKING_S'],'Blanking');
set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:MIN_MAG_S'],0);

if contains(name, 'TMBF')
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:KI_S'],1000); %safe also for for low charge, sharp resonance
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:KP_S'],0);
    set_variable([mbf_names.(mbf_axis) ':PLL:DET:DWELL_S'],128);
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:MAX_OFFSET_S'],0.02);
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:TARGET_S'],-180);
elseif contains(mbf_names.(mbf_axis), 'LMBF')
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:KI_S'],100); %safe also for for low charge, sharp resonance
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:KP_S'],0);
    set_variable([mbf_names.(mbf_axis) ':PLL:DET:DWELL_S'],128);
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:MAX_OFFSET_S'],0.001);
    set_variable([mbf_names.(mbf_axis) ':PLL:CTRL:TARGET_S'],-5);
end %if