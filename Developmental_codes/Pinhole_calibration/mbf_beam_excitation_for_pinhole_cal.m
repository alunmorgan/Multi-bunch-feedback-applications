function mbf_beam_excitation_for_pinhole_cal(mbf_axis, varargin)
% Sets up the FLL with an additional excitation at a user defined gain 
% and harmonic.
%   Args:
%       mbf_axis(str): 'x', or 'y'
%       excitation_gain(float): the magnitude of the excitation in dB.
%       harmonic(int): The tune harmonic to operate on.
%
% Example: data =  mbf_beam_excitation('y','excitation_gain', -30);

% Define input and default values
validScalarNum = @(x) isnumeric(x) && isscalar(x);

default_excitation_gain = -60; %dB
default_harmonic = 10;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
addRequired(p, 'mbf_axis');
addParameter(p, 'excitation_gain', default_excitation_gain);
addParameter(p, 'harmonic', default_harmonic, validScalarNum);
parse(p, mbf_axis, varargin{:});

[~] = mbf_emittance_setup(mbf_axis, ...
    'excitation', p.Results.excitation_gain,...
    'harmonic', p.Results.harmonic);
