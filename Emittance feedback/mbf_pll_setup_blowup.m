function mbf_pll_setup_blowup(varargin)
% Sets up the Multibunch feedback system to run a frequency locked loop on a
% single bunch in each plane. The use the tracked frequency to run an
% oscillator on the sideband of the tune.
%   Args: (All optional)
%       excitation_x(float): The power of the oscillator in the x axis (in dB).
%       excitation_y(float): The power of the oscillator in the y axis (in dB).
%       fll_monitor_bunches_x(vector of floats): The bunches to be used by the
%                                                FLL for tune tracking (x axis).
%       fll_monitor_bunches_y(vector of floats): The bunches to be used by the
%                                                FLL for tune tracking (y axis).
%       guardbunches_x(int): The number of bunches around the FLL monitor bunches
%                            for which the feedback is turned off. 
%                            This is to reduce distortion of the monitored signal
%       guardbunches_y(int): The number of bunches around the FLL monitor bunches
%                            for which the feedback is turned off. 
%                            This is to reduce distortion of the monitored signal

default_excitation_x = -60;
default_excitation_y = -60;
default_fll_monitor_bunches_x=400;
default_fll_monitor_bunches_y=300;
default_guardbunches_x = 10;
default_guardbunches_y = 10;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
validNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addParameter(p, 'excitation_x', default_excitation_x, validScalarNum);
addParameter(p, 'excitation_y', default_excitation_y, validScalarNum);
addParameter(p, 'fll_monitor_bunches_x', default_fll_monitor_bunches_x, validNum);
addParameter(p, 'fll_monitor_bunches_y', default_fll_monitor_bunches_y, validNum);
addParameter(p, 'guardbunches_x', default_guardbunches_x, validScalarNum);
addParameter(p, 'guardbunches_y', default_guardbunches_y, validScalarNum);
parse(p,varargin{:});

namex = mbf_axis_to_name('x');
namey = mbf_axis_to_name('y');

% initialise PLL on two different arbitrary (hopefully these are filled) 
% bunches on both planes.
mbf_fll_start('x', 'fllbunches',p.Results.fll_monitor_bunches_x,...
    'guardbunches',p.Results.guardbunches_x)
mbf_fll_start('y', 'fllbunches',p.Results.fll_monitor_bunches_y,...
    'guardbunches',p.Results.guardbunches_y)

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









