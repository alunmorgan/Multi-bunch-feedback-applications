function mbf_pll_setup_blowup(varargin)

default_excitation_x = -60;
default_excitation_y = -60;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addParameter(p, 'excitation_x', default_excitation_x, validScalarNum);
addParameter(p, 'excitation_y', default_excitation_y, validScalarNum);
parse(p,varargin{:});

namex = mbf_axis_to_name('x');
namey = mbf_axis_to_name('y');

% initialise PLL on two different arbitrary (hopefully these are filled) 
% bunches on both planes.
fllbunches_x=400;
fllbunches_y=300;
guardbunches_x = 10;
guardbunches_y = 10;
% mbf_pll_start(namex,pllbunches_x,10)
% mbf_pll_start(namey,pllbunches_y,10)
mbf_fll_start('x', 'fllbunches',fllbunches_x, 'guardbunches',guardbunches_x)
mbf_fll_start('y', 'fllbunches',fllbunches_y, 'guardbunches',guardbunches_y)

% Grab frequencies of left sideband from swept tune fitter
[x_tune, y_tune, ~] = get_all_tunes;
leftX = x_tune.lower_sideband;
leftY = y_tune.lower_sideband;

% Programm these as starting values into each NCO2, add harmonic 10 to get to
% slightly higher frequency ~5MHz, where the amplifiers/stripline provide
% better efficiency. This will produce more blowup per RF power.

harmonic=10;
lcaPut([namex, 'NCO2:FREQ_S'],leftX+harmonic);
lcaPut([namey, 'NCO2:FREQ_S'],leftY+harmonic);

%% Setting up the NCO gains and setting the tune sweep to follow the FLL.
lcaPut([namex, 'NCO2:TUNE_PLL_S'],'Follow');
lcaPut([namey, 'NCO2:TUNE_PLL_S'],'Follow');
lcaPut([namex, 'NCO2:GAIN_DB_S'],p.Results.excitation_x);
lcaPut([namey, 'NCO2:GAIN_DB_S'],p.Results.excitation_y);

%% Extracting the bunches the feedback is operating on 
fillx=lcaGet([namex, 'BUN:1:SEQ:ENABLE_S']);
filly=lcaGet([namey, 'BUN:1:SEQ:ENABLE_S']);
%% and applying the same mapping to the NCO
lcaPut([namex, 'BUN:0:NCO2:ENABLE_S'],fillx)
lcaPut([namey, 'BUN:0:NCO2:ENABLE_S'],filly)
lcaPut([namex, 'BUN:1:NCO2:ENABLE_S'],fillx)
lcaPut([namey, 'BUN:1:NCO2:ENABLE_S'],filly)

%% Switching on the excitation
lcaPut([namex, 'NCO2:ENABLE_S'],'On');
lcaPut([namey, 'NCO2:ENABLE_S'],'On');









