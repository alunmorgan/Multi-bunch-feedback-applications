function mbf_emittance_control(varargin)
% Starts the emittance control loop using the multibunch feedback system.
%   Args:
%       hemit_target(float): Target value for horizontal emittance (nm rad)
%       vemit_target(float): Target value for vertical emittance (pm rad)
%
% Example: mbf_emittance_control('hemit_target', 3, 'vemit_target', 9)

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
p = inputParser;
addParameter(p, 'hemit_target', NaN, validScalarPosNum);
addParameter(p, 'vemit_target', NaN, validScalarPosNum);
parse(p,varargin{:});

if isnan(p.Results.hemit_target) && isnan(p.Results.vemit_target)
    disp('You need to select either a hemit_target (nm rad), or a vemit_target (pm rad), or both.')
    return
end %if

if lcaGet('SR-DI-DCCT-01:SIGNAL') < 1 %mA
    disp('This needs to be run with beam. No changes have been made.')
    return
end %if

if ~isnan(p.Results.hemit_target)
existing_excitation_x = lcaGet('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S');
mbf_emittance_setup('x','excitation',existing_excitation_x, 'fll_monitor_bunches', 300)
emittance_control_loop('X', p.Results.hemit_target)
end %if

if ~isnan(p.Results.vemit_target)
existing_excitation_y = lcaGet('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S');
mbf_emittance_setup('y','excitation',existing_excitation_y, 'fll_monitor_bunches', 400)
emittance_control_loop('Y', p.Results.vemit_targetY)
end %if
