function mbf_emittance_setup(mbf_axis, varargin)
% Sets up the Multibunch feedback system to run a frequency locked loop on a
% single bunch in each plane. The use the tracked frequency to run an
% oscillator on the sideband of the tune.
%   Args: (All optional)
%       excitation(float): The power of the oscillator in the selected axis (in dB).
%       fll_monitor_bunches(vector of floats): The bunches to be used by the
%                                                FLL for tune tracking.
%       guardbunches(int): The number of bunches around the FLL monitor bunches
%                            for which the feedback is turned off. 
%                            This is to reduce distortion of the monitored signal
%       harmonic(int): The harmonic to operate on. Sometimes higher
%                      harmonics have better signal to noise ratios.
%                      Also where the amplifiers/stripline provide
%                      better efficiency. 
%                      This will produce more blowup per RF power.
%       excitation_frequency(float): Usually you want the sideband
%                                    frequency. However this allow a user
%                                    defined tune value to be used.
%
% Example: mbf_emittance_setup('x')

default_excitation = -60; %dB
default_fll_monitor_bunches=400;
default_guardbunches = 10;
default_harmonic = 10;
% Grab frequencies of left sideband from swept tune fitter
tunes = get_all_tunes(mbf_axis);
leftSB = tunes.([mbf_axis, '_tune']).lower_sideband;
default_excitation_frequency = leftSB;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
validNum = @(x) isnumeric(x);
p = inputParser;
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation', default_excitation, validScalarNum);
addParameter(p, 'fll_monitor_bunches', default_fll_monitor_bunches, validNum);
addParameter(p, 'guardbunches', default_guardbunches, validScalarNum);
addParameter(p, 'harmonic', default_harmonic, validScalarNum);
addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
parse(p,mbf_axis, varargin{:});

mbf_name = mbf_axis_to_name(mbf_axis);

% initialise FLL on selected bunches.
mbf_fll_start(mbf_axis, 'fllbunches',p.Results.fll_monitor_bunches,...
    'guardbunches',p.Results.guardbunches)

lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.excitation_frequency);

%% Setting up the NCO gains and setting the tune sweep to follow the FLL.
lcaPut([mbf_name, 'NCO2:TUNE_PLL_S'],'Follow');
lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.harmonic + p.Results.excitation);

%% Extracting the bunches the feedback is operating on 
fillx = lcaGet([mbf_name, 'BUN:1:SEQ:ENABLE_S']);
%% and applying the same mapping to the NCO
lcaPut([mbf_name, 'BUN:0:NCO2:ENABLE_S'],fillx)
lcaPut([mbf_name, 'BUN:1:NCO2:ENABLE_S'],fillx)

%% Switching on the excitation
lcaPut([mbf_name, 'NCO2:ENABLE_S'],'On');









