function mbf_pll_setup_blowup

namex = mbf_axis_to_name('x');
namey = mbf_axis_to_name('y');
lcaPut([namex, 'NCO2:ENABLE_S'],'Off');
lcaPut([namey, 'NCO2:ENABLE_S'],'Off');
pause(2);

% initialise PLL on two different arbitrary (hopefully these are filled) 
% bunches on both planes.
xbunch=400;
ybunch=400;
mbf_pll_start(namex,xbunch,10)
mbf_pll_start(namey,ybunch,10)
% mbf_fll_bank_setup('SR23C-DI-TMBF-01:X', xbunch, 10)
% mbf_fll_bank_setup('SR23C-DI-TMBF-01:Y', ybunch, 10)
% fll_initialisation('SR23C-DI-TMBF-01:X')
% fll_initialisation('SR23C-DI-TMBF-01:Y')

% Grab frequencies of left sideband from swept tune fitter
leftX=lcaGet([namex, 'TUNE:LEFT:TUNE']);
leftY=lcaGet([namey, 'TUNE:LEFT:TUNE']);

% Programm these as starting values into each NCO2, add harmonic 10 to get to
% slightly higher frequency ~5MHz, where the amplifiers/stripline provide
% better efficiency. This will produce more blowup per RF power.

harmonic=10;
lcaPut([namex, 'NCO2:FREQ_S'],leftX+harmonic);
lcaPut([namey, 'NCO2:FREQ_S'],leftY+harmonic);

% Ensure Track_PLL is on follow, chose a sensible power to start with,
% switch on, then the beam should increase in size

lcaPut([namex, 'NCO2:TUNE_PLL_S'],'Follow');
lcaPut([namey, 'NCO2:TUNE_PLL_S'],'Follow');
lcaPut([namex, 'NCO2:GAIN_DB_S'],-30);
lcaPut([namey, 'NCO2:GAIN_DB_S'],-40);
%fillx=ones(1,936);
%fillx(xbunch)=0;
%filly=ones(1,936);
%filly(ybunch)=0;
fillx=lcaGet([namex, 'BUN:1:SEQ:ENABLE_S']);
filly=lcaGet([namey, 'BUN:1:SEQ:ENABLE_S']);

lcaPut([namex, 'BUN:0:NCO2:ENABLE_S'],fillx)
lcaPut([namey, 'BUN:0:NCO2:ENABLE_S'],filly)
lcaPut([namex, 'BUN:1:NCO2:ENABLE_S'],fillx)
lcaPut([namey, 'BUN:1:NCO2:ENABLE_S'],filly)
lcaPut([namex, 'NCO2:ENABLE_S'],'On');
lcaPut([namey, 'NCO2:ENABLE_S'],'On');









