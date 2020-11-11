function mbf_pll_start(name, pllbunches, guardbunches)
% function mbf_pll_start(name,pllbunches,guardbunches)
%
% name          <EPICS device>:<axis>
% pllbunches    bunches numbers to use for PLL (0-935)
% guardbunches  number of bunches around PLL to also take out of sweeper
%               (defaults to 2)

% ugly check to see if guardbunches are specified
if nargin<3
    guardbunches = 2;
end

% initialise pll pattern
pllpattern=false(1,936);
% Matlab counts idices from 1, but at DLS we count bunches from 0, thus we need to
% add one.
pllpattern(pllbunches+1) = true;

% now we want to create a pattern with a little more room around the
% pll bunches. It's a little tricky with a general pattern, and the cirular
% nature the pattern, so I use circshift in a loop

guardpattern=true(1,936);
for n=-guardbunches:guardbunches
    guardpattern(circshift(pllpattern,n)) = false;
end

% Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps), 
% and in PLL detector.

lcaPut([name ':BUN:0:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name ':BUN:1:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name ':PLL:DET:BUNCHES_S'], double(pllpattern));

% Set sweep (SEQ) and its detector (#1) to NOT operate on these and
% guard bunches around, ie only on guardpattern. This is maybe a little
% keen, as there might be other things configured, which this will jjst
% plow over. Maybe we should check or add to any previous config...

lcaPut([name ':BUN:1:SEQ:ENABLE_S'],double(guardpattern));
lcaPut([name ':DET:0:BUNCHES_S'],double(guardpattern));

% Now comes some setup with 'working values'. These ought to be read from a
% config file or be additinal arguments in the future.


lcaPut([name ':PLL:DET:SELECT_S'],'ADC no fill');
lcaPut([name ':ADC:REJECT_COUNT_S'],'128 turns');
lcaPut([name ':PLL:DET:SCALING_S'],'48dB');
lcaPut([name ':PLL:DET:BLANKING_S'],'Blanking');
lcaPut([name ':PLL:DET:DWELL_S'],128);


lcaPut([name ':PLL:CTRL:KI_S'],1000); %safe also for for low charge, sharp resonance
lcaPut([name ':PLL:CTRL:KP_S'],0);
lcaPut([name ':PLL:CTRL:MIN_MAG_S'],0);
lcaPut([name ':PLL:CTRL:MAX_OFFSET_S'],0.02);
lcaPut([name ':PLL:CTRL:TARGET_S'],-180);



% starting frequency is taken form swept tune measurement, but could also
% be configured from config file (but then it will only work if tune
% feedback has brought the tune to the desired value...)

tune=lcaGet([name ':TUNE:CENTRE:TUNE'],1,'double');
if isnan(tune);
    error('Tune fit invalid, cannot start PLL.')
    %tune=37.45;
end

lcaPut([name ':PLL:NCO:GAIN_DB_S'],-30);
lcaPut([name ':PLL:NCO:FREQ_S'],tune);
lcaPut([name ':PLL:NCO:ENABLE_S'],'On');

% finally, lets start, and then check whether we're still running after 1
% second

lcaPut([name ':PLL:CTRL:START_S.PROC'],0);
pause(1)
status=lcaGet([name ':PLL:CTRL:STATUS']);
display(['PLL is: ' cell2mat(status)]);




