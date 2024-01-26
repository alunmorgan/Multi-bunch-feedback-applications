function mbf_fll_start(mbf_axis, varargin)
% sets up the frequency locked loop of the MBF system.
% and starts.
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
addParameter(p, 'fllbunches', 400);
addParameter(p, 'guardbunches', 2);
addParameter(p, 'fll_nco_gain', -30);

parse(p, mbf_axis, varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;
if strcmp(mbf_axis, 'x')
    target_phase = 160;
elseif strcmp(mbf_axis, 'y')
    target_phase = 180;
else
    error('PLL:invalidAxis', 'Invalid axis selected. (expected x or y)')
end

mbf_fll_bank_setup(pv_names.hardware_names.(mbf_axis), 'fllbunches', p.Results.fllbunches, 'guardbunches', p.Results.guardbunches)
mbf_fll_detector_setup(pv_names.hardware_names.(mbf_axis))
fll_initialisation(mbf_axis, 'fll_target_phase', target_phase, 'fll_nco_gain', p.Results.fll_nco_gain)