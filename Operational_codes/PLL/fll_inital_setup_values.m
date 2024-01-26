function fll_inital_setup_values(name)

% Some setup with 'working values'. These ought to be read from a
% config file or be additional arguments in the future.
% name          <EPICS device>:<axis>

set_variable([name 'PLL:DET:SELECT_S'],'ADC no fill');
set_variable([name 'ADC:REJECT_COUNT_S'],'128 turns');
set_variable([name 'PLL:DET:SCALING_S'],'48dB');
set_variable([name 'PLL:DET:BLANKING_S'],'Blanking');
set_variable([name 'PLL:CTRL:MIN_MAG_S'],0);

if contains(name, 'TMBF')
    set_variable([name 'PLL:CTRL:KI_S'],1000); %safe also for for low charge, sharp resonance
    set_variable([name 'PLL:CTRL:KP_S'],0);
    set_variable([name 'PLL:DET:DWELL_S'],128);
    set_variable([name 'PLL:CTRL:MAX_OFFSET_S'],0.02);
    set_variable([name 'PLL:CTRL:TARGET_S'],-180);
elseif contains(name, 'LMBF')
    set_variable([name 'PLL:CTRL:KI_S'],100); %safe also for for low charge, sharp resonance
    set_variable([name 'PLL:CTRL:KP_S'],0);
    set_variable([name 'PLL:DET:DWELL_S'],128);
    set_variable([name 'PLL:CTRL:MAX_OFFSET_S'],0.001);
    set_variable([name 'PLL:CTRL:TARGET_S'],-5);
end %if