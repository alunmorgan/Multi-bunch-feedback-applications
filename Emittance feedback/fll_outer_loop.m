function fll_outer_loop

fll_initialisation
% Monitor the FLL lock state and if unlocked re initialise.
fll_status = lcaMonitor('')
if fll_status == 
    fll_initialisation