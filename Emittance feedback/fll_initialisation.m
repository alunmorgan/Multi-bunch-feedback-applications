function fll_initialisation
% This is to start the frequency locked loop (fll) [also called pll] from
% scratch. Once the initial lock is found then the settings are changed to
% improve tracking. if signal is lost this process can be run again.


% Disable PLL
lcaPut('',);
% Perform a TUNE sweep, record phase at tune peak and the tune value
tune_frequency_from_sweep = lcaGet('');
tune_phase_from_sweep = lcaGet('');
% Load tune peak value into the NCO as starting frequency, load recorded phase as set point
lcaPut('', tune_frequency_from_sweep)
lcaPut('', tune_phase_from_sweep)
% Limit tune range of the NCO to +/- 0.002
lcaPut('',)
% Enable the PLL
lcaPut('',)
% Wait until PLL has locked (set lower bound to phase error?)
while lcaGet('') == 
    time
    if time >10
        disp('Unable to lock within 10 seconds')
        break
% Once locked widen the NCO limits to max required for tracking
lcaPut('',)
lcaPut('',)

