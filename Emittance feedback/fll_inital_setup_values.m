function fll_inital_setup_values(name)

% Some setup with 'working values'. These ought to be read from a
% config file or be additional arguments in the future.
% name          <EPICS device>:<axis>

lcaPut([name 'PLL:DET:SELECT_S'],'ADC no fill');
lcaPut([name 'ADC:REJECT_COUNT_S'],'128 turns');
lcaPut([name 'PLL:DET:SCALING_S'],'48dB');
lcaPut([name 'PLL:DET:BLANKING_S'],'Blanking');
lcaPut([name 'PLL:CTRL:MIN_MAG_S'],0);

if contains(name, 'TMBF')
    lcaPut([name 'PLL:CTRL:KI_S'],1000); %safe also for for low charge, sharp resonance
    lcaPut([name 'PLL:CTRL:KP_S'],0);
    lcaPut([name 'PLL:DET:DWELL_S'],128);
    lcaPut([name 'PLL:CTRL:MAX_OFFSET_S'],0.02);
    lcaPut([name 'PLL:CTRL:TARGET_S'],-180);
elseif contains(name, 'LMBF')
    lcaPut([name 'PLL:CTRL:KI_S'],100); %safe also for for low charge, sharp resonance
    lcaPut([name 'PLL:CTRL:KP_S'],0);
    lcaPut([name 'PLL:DET:DWELL_S'],128);
    lcaPut([name 'PLL:CTRL:MAX_OFFSET_S'],0.001);
    lcaPut([name 'PLL:CTRL:TARGET_S'],-5);
end %if