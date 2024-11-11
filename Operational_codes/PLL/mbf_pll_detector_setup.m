function mbf_pll_detector_setup(mbf_axis, varargin)
% Sets up the detector for FLL operation.
%
%   mbf_axis (str): x, y, or s. Selects which MBF system to operate on.
%
% example: mbf_pll_detector_setup(mbf_axis, varargin)

default_pll_detector_select = 'ADC no fill';
default_adc_reject_count = '128 turns';
default_pll_detector_scaling = '48dB';
default_pll_detector_blanking = 'Blanking';
default_pll_detector_dwell = 128;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x >0);
addRequired(p, 'mbf_axis');
addParameter(p, 'pll_detector_select', default_pll_detector_select, @isstring);
addParameter(p, 'adc_reject_count', default_adc_reject_count, @isstring);
addParameter(p, 'pll_detector_scaling', default_pll_detector_scaling, @isstring);
addParameter(p, 'pll_detector_blanking', default_pll_detector_blanking, @isstring);
addParameter(p, 'pll_detector_dwell', default_pll_detector_dwell, validScalarPosNum);

parse(p, mbf_axis, varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

% Set up the PLL detector
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.mode],...
    p.Results.pll_detector_select);
set_variable([mbf_names.(mbf_axis), mbf_vars.adc.reject_count],...
    p.Results.adc_reject_count);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.scaling],...
    p.Results.pll_detector_scaling);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.blanking],...
    p.Results.pll_detector_blanking);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.dwell],...
    p.Results.pll_detector_dwell);
