function mbf_fll_detector_setup(mbf_axis, varargin)
% Sets up the detector for FLL operation.
%
%   name (str): <EPICS device>:<axis>
%
% example: mbf_fll_detector_setup(name)

default_fll_detector_select = 'ADC no fill';
default_adc_reject_count = '128 turns';
default_fll_detector_scaling = '48dB';
default_fll_detector_blanking = 'Blanking';
default_fll_detector_dwell = 128;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x >0);
addRequired(p, 'mbf_axis');
addParameter(p, 'fll_detector_select', default_fll_detector_select, @isstring);
addParameter(p, 'adc_reject_count', default_adc_reject_count, @isstring);
addParameter(p, 'fll_detector_scaling', default_fll_detector_scaling, @isstring);
addParameter(p, 'fll_detector_blanking', default_fll_detector_blanking, @isstring);
addParameter(p, 'fll_detector_dwell', default_fll_detector_dwell, validScalarPosNum);

parse(p, mbf_axis, varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

% Set up the FLL detector
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.mode],...
    p.Results.fll_detector_select);
set_variable([mbf_names.(mbf_axis), mbf_vars.adc.reject_count],...
    p.Results.adc_reject_count);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.scaling],...
    p.Results.fll_detector_scaling);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.blanking],...
    p.Results.fll_detector_blanking);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.dwell],...
    p.Results.fll_detector_dwell);
