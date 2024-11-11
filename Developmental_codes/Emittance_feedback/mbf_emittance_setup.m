function varargout = mbf_emittance_setup(mbf_axis, varargin)
% Sets up the Multibunch feedback system to run a frequency locked loop on a
% single bunch in each plane. The use the tracked frequency to run an
% oscillator on the sideband of the tune.
%   Args: 
%       mbf_axis(str): the axis to do the setup on (x, y, or s).
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

mbf_axis = lower(mbf_axis);
[~, harmonic_number, pv_names, ~] = mbf_system_config;

default_excitation = -60; %dB
default_excitation_pattern = ones(harmonic_number,1);
default_fll_monitor_bunches=400;
default_guardbunches = 10;
default_harmonic = 10;
% Grab frequencies of left sideband from swept tune fitter
tunes = get_all_tunes;
leftSB = tunes.([mbf_axis, '_tune']).lower_sideband;
default_excitation_frequency = leftSB;

validScalarNum = @(x) isnumeric(x) && isscalar(x);
validNum = @(x) isnumeric(x);
p = inputParser;
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation', default_excitation, validScalarNum);
addParameter(p, 'excitation_pattern', default_excitation_pattern);
addParameter(p, 'fll_monitor_bunches', default_fll_monitor_bunches, validNum);
addParameter(p, 'guardbunches', default_guardbunches, validScalarNum);
addParameter(p, 'harmonic', default_harmonic, validScalarNum);
addParameter(p, 'excitation_frequency', default_excitation_frequency, validScalarNum)
parse(p,mbf_axis, varargin{:});


mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

if isnan(p.Results.excitation)
    excitation_frequency = default_excitation_frequency;
else
    excitation_frequency = p.Results.excitation_frequency;
end %if

% initialise FLL on selected bunches.
mbf_pll_start(mbf_axis, 'pllbunches',p.Results.fll_monitor_bunches,...
    'guardbunches',p.Results.guardbunches)

set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency], p.Results.harmonic + excitation_frequency);

%% Setting up the NCO gains and setting the tune sweep to follow the PLL.
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.PLL_follow],'Follow');
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db],p.Results.excitation);

%% Extracting the bunches the feedback is operating on 
fillx = get_variable([mbf_names.(mbf_axis), pv_names.tails.Bunch_bank.bank1.SEQ.enablewf]);

%% Applying the same mapping to the NCO and combining it with the user defined pattern
pattern = and(fillx, p.Results.excitation_pattern'); 
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank0.NCO2.enablewf], double(pattern))
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank1.NCO2.enablewf], double(pattern))

%% Switching on the excitation
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.enable],'On');

if nargout > 0 
    varargout{1} = pattern;
end%if







