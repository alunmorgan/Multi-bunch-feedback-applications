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

default_excitation_frequency = 0.28; %dB
default_excitation_gain = -60; %dB
default_harmonic = 10;
default_delay = 1;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation_gain', default_excitation_gain, validScalarNum);
addParameter(p, 'harmonic', default_harmonic, validScalarNum);
addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
addParameter(p, 'delay', default_delay, validScalarNum)
parse(p,mbf_axis, varargin{:});

mbf_name = mbf_axis_to_name(mbf_axis);
%% Turning off the external trigger
set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 0);

%% Setting up the sequencer for single shot
set_variable([mbf_name, 'TRG:SEQ:MODE_S'], 'One Shot') 

%% Setting up the excitation
set_variable([mbf_name, 'SEQ:PC_S'], 2)
set_variable([mbf_name, 'SEQ:2:BANK_S'], 'Bank 1')
set_variable([mbf_name, 'SEQ:2:START_FREQ_S'], p.Results.harmonic + p.Results.excitation_frequency)
set_variable([mbf_name, 'SEQ:2:STEP_FREQ_S'], 0)
set_variable([mbf_name, 'SEQ:2:COUNT_S'], 1)
set_variable([mbf_name, 'SEQ:2:DWELL_S'], p.Results.delay)
set_variable([mbf_name, 'SEQ:2:ENABLE_S'], 'Off')
set_variable([mbf_name, 'SEQ:1:START_FREQ_S'], p.Results.harmonic + p.Results.excitation_frequency)
set_variable([mbf_name, 'SEQ:1:STEP_FREQ_S'], 0)
set_variable([mbf_name, 'SEQ:1:COUNT_S'], 1)
set_variable([mbf_name, 'SEQ:1:DWELL_S'], 1)
set_variable([mbf_name, 'SEQ:1:ENABLE_S'], 'On')
set_variable([mbf_name, 'SEQ:1:GAIN_DB_S'], p.Results.excitation_gain)












