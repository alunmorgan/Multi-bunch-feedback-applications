function mbf_fll_detector_setup(name, varargin)
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
addRequired(p, 'name');
addParameter(p, 'fll_detector_select', default_fll_detector_select, @isstring);
addParameter(p, 'adc_reject_count', default_adc_reject_count, @isstring);
addParameter(p, 'fll_detector_scaling', default_fll_detector_scaling, @isstring);
addParameter(p, 'fll_detector_blanking', default_fll_detector_blanking, @isstring);
addParameter(p, 'fll_detector_dwell', default_fll_detector_dwell, validScalarPosNum);

parse(p, name, varargin{:});

% Set up the FLL detector
set_variable([name ':PLL:DET:SELECT_S'],p.Results.fll_detector_select);
set_variable([name ':ADC:REJECT_COUNT_S'],p.Results.adc_reject_count);
set_variable([name ':PLL:DET:SCALING_S'],p.Results.fll_detector_scaling);
set_variable([name ':PLL:DET:BLANKING_S'],p.Results.fll_detector_blanking);
set_variable([name ':PLL:DET:DWELL_S'],p.Results.fll_detector_dwell);
