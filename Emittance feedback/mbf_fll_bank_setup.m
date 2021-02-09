function mbf_fll_bank_setup(name, pllbunches, guardbunches)
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

lcaPut([name 'BUN:0:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name 'BUN:1:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name 'PLL:DET:BUNCHES_S'], double(pllpattern));

% Set sweep (SEQ) and its detector (#1) to NOT operate on these and
% guard bunches around, ie only on guardpattern. This is maybe a little
% keen, as there might be other things configured, which this will jjst
% plow over. Maybe we should check or add to any previous config...

lcaPut([name 'BUN:1:SEQ:ENABLE_S'],double(guardpattern));
lcaPut([name 'DET:0:BUNCHES_S'],double(guardpattern));