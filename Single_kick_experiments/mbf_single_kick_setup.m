function mbf_single_kick_setup(mbf_axis, varargin)
% Sets up the Multibunch feedback system to 
%   Args: (All optional)
%       excitation(float): The power of the oscillator in the selected axis (in dB).
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
default_harmonic = 10;
% Grab frequencies of left sideband from swept tune fitter
tunes = get_all_tunes(mbf_axis);
leftSB = tunes.([mbf_axis, '_tune']).lower_sideband;
default_excitation_frequency = leftSB;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation_gain', default_excitation, validScalarNum);
addParameter(p, 'harmonic', default_harmonic, validScalarNum);
addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
parse(p,mbf_axis, varargin{:});

mbf_name = mbf_axis_to_name(mbf_axis);
%% Turning off the external trigger
lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 0);

%% Setting up the sequencer for single shot
lcaPut([mbf_name, 'TRG:SEQ:MODE_S'], 'Oneshot') %FIXME - need to check the value

%% Setting up the excitation
lcaPut([mbf_name, 'NCO2:FREQ_S'], p.Results.harmonic + p.Results.excitation_frequency);
lcaPut([mbf_name, 'NCO2:GAIN_DB_S'],p.Results.excitation);
lcaPut([mbf_name, 'NCO2:ENABLE_S'],'On');











