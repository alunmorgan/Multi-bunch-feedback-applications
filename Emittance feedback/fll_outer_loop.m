function fll_outer_loop(name)
% Monitor the FLL lock state and if unlocked re initialise.
% name          <EPICS device>:<axis>
fll_initialisation(mbf_axis)

lcaSetMonitor([name, 'PLL:CTRL:STATUS'])
while 1 == 1
    lcaNewMonitorWait([name, 'PLL:CTRL:STATUS'])
    fll_status = lcaGet([name, 'PLL:CTRL:STATUS']);
    if strcmpi(fll_status, 'Stopped')
        fll_initialisation(mbf_axis)
    end %if
end %while