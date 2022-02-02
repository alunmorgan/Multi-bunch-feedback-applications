function mbf_fll_start(mbf_axis, varargin)
% sets up the frequency locked loop of the MBF system.
% but does not start it.
%
%       mbf_axis (str): x, y, or s. Selects which MBF system to operate on.
%       pllbunches (float or list of floats): Selects which bunches to have the
%                                             FLL operational on.
%       guardbunches (int): number of bunches around the FLL bunches which have 
%                           feddback and capture disabled.
%
% example: mbf_fll_setup(mbf_axis, pllbunches, guardbunches)

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
addRequired(p, 'mbf_axis');
addParameter(p, 'fllbunches', NaN);
addParameter(p, 'guardbunches', NaN);

parse(p, mbf_axis, varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;

% lcaPut([pv_names.hardware_names.(mbf_axis), 'NCO2:ENABLE_S'],'Off');
% pause(2);
if ~isnan(p.Results.fllbunches)
mbf_fll_bank_setup(pv_names.hardware_names.(mbf_axis), 'fllbunches', p.Results.fllbunches, 'guardbunches', p.Results.guardbunches)
else
    mbf_fll_bank_setup(pv_names.hardware_names.(mbf_axis))
end
mbf_fll_detector_setup(pv_names.hardware_names.(mbf_axis))
fll_initialisation(pv_names.hardware_names.(mbf_axis))