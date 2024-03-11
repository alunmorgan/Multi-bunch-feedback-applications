function mbf_pll_start(mbf_axis, varargin)
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
axis_string = {'x', 'y', 's'};

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addParameter(p, 'pllbunches', 400, @(x) isnumeric(x));
addParameter(p, 'guardbunches', 2, @(x) isnumeric(x) && isscalar(x));
addParameter(p, 'pll_nco_gain', -30, @(x) isnumeric(x) && isscalar(x));
addParameter(p, 'target_phase', 180, @(x) isnumeric(x) && isscalar(x));

parse(p, mbf_axis, varargin{:});

mbf_pll_bank_setup(mbf_axis, 'pllbunches', p.Results.pllbunches, 'guardbunches', p.Results.guardbunches)
mbf_pll_detector_setup(mbf_axis)
pll_initialisation(mbf_axis, 'pll_target_phase', p.Results.target_phase, 'pll_nco_gain', p.Results.pll_nco_gain)
