function mbf_pll_setup_blowup
lcaPut('SR23C-DI-TMBF-01:X:NCO2:ENABLE_S','Off');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:ENABLE_S','Off');
pause(2);

% initialise PLL on two different arbitrary (hopefully these are filled) 
% bunches on both planes.
xbunch=920;
ybunch=920;
mbf_pll_start('SR23C-DI-TMBF-01:X',xbunch,10)
mbf_pll_start('SR23C-DI-TMBF-01:Y',ybunch,10)

% Grab frequencies of left sideband from swept tune fitter
leftX=lcaGet('SR23C-DI-TMBF-01:X:TUNE:LEFT:TUNE');
leftY=lcaGet('SR23C-DI-TMBF-01:Y:TUNE:LEFT:TUNE');

% Programm these as starting values into each NCO2, add harmonic 10 to get to
% slightly higher frequency ~5MHz, where the amplifiers/stripline provide
% better efficiency. This will produce more blowup per RF power.

harmonic=10;
lcaPut('SR23C-DI-TMBF-01:X:NCO2:FREQ_S',leftX+harmonic);
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:FREQ_S',leftY+harmonic);

% Ensure Track_PLL is on follow, chose a sensible power to start with,
% switch on, then the beam should increase in size

lcaPut('SR23C-DI-TMBF-01:X:NCO2:TUNE_PLL_S','Follow');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:TUNE_PLL_S','Follow');
lcaPut('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S',-15);
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S',-30);
%fillx=ones(1,936);
%fillx(xbunch)=0;
%filly=ones(1,936);
%filly(ybunch)=0;
fillx=lcaGet('SR23C-DI-TMBF-01:X:BUN:1:SEQ:ENABLE_S');
filly=lcaGet('SR23C-DI-TMBF-01:Y:BUN:1:SEQ:ENABLE_S');

lcaPut('SR23C-DI-TMBF-01:X:BUN:0:NCO2:ENABLE_S',fillx)
lcaPut('SR23C-DI-TMBF-01:Y:BUN:0:NCO2:ENABLE_S',filly)
lcaPut('SR23C-DI-TMBF-01:X:BUN:1:NCO2:ENABLE_S',fillx)
lcaPut('SR23C-DI-TMBF-01:Y:BUN:1:NCO2:ENABLE_S',filly)
lcaPut('SR23C-DI-TMBF-01:X:NCO2:ENABLE_S','On');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:ENABLE_S','On');









