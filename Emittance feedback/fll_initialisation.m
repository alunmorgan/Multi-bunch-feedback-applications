function fll_initialisation(base)
% This is to start the frequency locked loop (fll) [also called pll] from
% scratch. Once the initial lock is found then the settings are changed to
% improve tracking. if signal is lost this process can be run again.
% base          <EPICS device>:<axis>


% Perform a TUNE sweep, record phase at tune peak and the tune value
tune_frequency_from_sweep = lcaGet([base, 'TUNE:TUNE']);
tune_phase_from_sweep = lcaGet([base, 'TUNE:PHASE']);
if isnan(tune_frequency_from_sweep) || isnan(tune_phase_from_sweep)
    warning('Tune fit invalid, cannot start PLL.')
    return
end %if

% Disable PLL and turn off the NCO
lcaPut([base, 'PLL:CTRL:STOP_S.PROC'], 1);
lcaPut([base ':PLL:NCO:ENABLE_S'],'Off');
% Load tune peak value into the NCO as starting frequency, load recorded phase as set point
lcaPut([base, 'PLL:NCO:FREQ_S'], tune_frequency_from_sweep)
lcaPut([base, 'PLL:CTRL:TARGET_S'], tune_phase_from_sweep)
% Limit tune range of the NCO to +/- 0.002
lcaPut([base, 'PLL:CTRL:MAX_OFFSET_S'], 0.002)
% Enable the NCO and PLL
lcaPut([base ':PLL:NCO:GAIN_DB_S'],-30);
lcaPut([base ':PLL:NCO:ENABLE_S'],'On');
lcaPut([base, 'PLL:CTRL:START_S.PROC'], 1)
% Wait until PLL has locked (set lower bound to phase error?)
t1 = now;
while abs(abs(lcaGet([base, 'PLL:FILT:PHASE'])) - ...
        abs( tune_phase_from_sweep)) > 1 % within one degree of target.
    time = (now - t1) *24* 3600;
    if time >10
        disp('Unable to lock within 10 seconds')
        return
    end %if
end %while
% Once locked widen the NCO limits to max required for tracking
lcaPut([base, 'PLL:CTRL:MAX_OFFSET_S'], 0.02)

