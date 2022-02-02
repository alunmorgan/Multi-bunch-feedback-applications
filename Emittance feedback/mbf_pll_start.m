function mbf_pll_start(name, varargin)
% function mbf_pll_start(name,varargin)
%
% name          <EPICS device>:<axis>
% pllbunches    (list) bunches numbers to use for PLL (0-935) 
%                      optional: defaults to 400
% guardbunches  (int) number of bunches around PLL to also take out of sweeper
%                    (optional: defaults to 2)
%
% Example: function mbf_pll_start(name,'pllbunches', [200:210],'guardbunches', 5)


%% Input parsing
default_guard_bunches = 2;
default_pll_bunches = 400;

default_fll_detector_select = 'ADC no fill';
default_adc_reject_count = '128 turns';
default_fll_detector_scaling = '48dB';
default_fll_detector_blanking = 'Blanking';
default_fll_detector_dwell = 128;
default_fll_ki = 1000; %safe also for for low charge, sharp resonance
default_fll_kp = 0;
default_fll_min_magnitude = 0;
default_fll_max_offset = 0.02;
default_fll_target_phase = -180;
default_fll_nco_gain = -30; % in dB
default_tune_override = NaN;

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addRequired(p, 'name', @isstring);
addParameter(p, 'pllbunches', default_pll_bunches, @isnumeric);
addParameter(p, 'guardbunches', default_guard_bunches, validScalarPosNum);
addParameter(p, 'fll_detector_select', default_fll_detector_select, @isstring);
addParameter(p, 'adc_reject_count', default_adc_reject_count, @isstring);
addParameter(p, 'fll_detector_scaling', default_fll_detector_scaling, @isstring);
addParameter(p, 'fll_detector_blanking', default_fll_detector_blanking, @isstring);
addParameter(p, 'fll_detector_dwell', default_fll_detector_dwell, validScalarPosNum);
addParameter(p, 'fll_ki', default_fll_ki, validScalarPosNum);
addParameter(p, 'fll_kp', default_fll_kp, validScalarNum);
addParameter(p, 'fll_min_magnitude', default_fll_min_magnitude, validScalarNum);
addParameter(p, 'fll_max_offset', default_fll_max_offset, validScalarPosNum);
addParameter(p, 'fll_target_phase', default_fll_target_phase, validScalarNum);
addParameter(p, 'fll_nco_gain', default_fll_nco_gain, validScalarNum);
addParameter(p, 'tune_override', default_tune_override, validScalarNum);

parse(p,name,varargin{:});
pllbunches = p.Results.pllbunches;
guardbunches = p.Results.guardbunches;

%% Checking tune
% starting frequency is taken from swept tune measurement. Can also
% be overridden from command line input (but then it will only work if tune
% feedback has brought the tune to the desired value...)
if ~isnan(p.Results.tune_override)
    tune=lcaGet([name 'TUNE:CENTRE:TUNE'],1,'double');
    if isnan(tune)
        error('Tune fit invalid, cannot start PLL.')
    end
else
    tune = p.Results.tune_override;
    disp(['Using tune override of ', num2str(p.Results.tune_override)])
end %if

%% Setting up patterns
% initialise pll pattern
pllpattern=false(1,936);
% Matlab counts idices from 1, but at DLS we count bunches from 0, thus we need to
% add one.
pllpattern(pllbunches+1) = true;

% now we want to create a pattern with a little more room around the
% pll bunches. It's a little tricky with a general pattern, and the cirular
% nature the pattern, so I use circshift in a loop

guardpattern=true(1,936);
for n=-guardbunches:guardbunches
    guardpattern(circshift(pllpattern,n)) = false;
end

% Set up PLL bunches in banks 0 and 1 (those are used in typical sweeps), 
% and in PLL detector.

lcaPut([name 'BUN:0:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name 'BUN:1:PLL:ENABLE_S'], double(pllpattern));
lcaPut([name 'PLL:DET:BUNCHES_S'], double(pllpattern));

% Set sweep (SEQ) and its detector (#1) to NOT operate on these and
% guard bunches around, ie only on guardpattern. This is maybe a little
% keen, as there might be other things configured, which this will jjst
% plow over. Maybe we should check or add to any previous config...

lcaPut([name 'BUN:1:SEQ:ENABLE_S'],double(guardpattern));
lcaPut([name 'DET:0:BUNCHES_S'],double(guardpattern));

% Set up the FLL detector
lcaPut([name 'PLL:DET:SELECT_S'],p.Results.fll_detector_select);
lcaPut([name 'ADC:REJECT_COUNT_S'],p.Results.adc_reject_count);
lcaPut([name 'PLL:DET:SCALING_S'],p.Results.fll_detector_scaling);
lcaPut([name 'PLL:DET:BLANKING_S'],p.Results.fll_detector_blanking);
lcaPut([name 'PLL:DET:DWELL_S'],p.Results.fll_detector_dwell);

% Set up the FLL feedback loop
lcaPut([name 'PLL:CTRL:KI_S'],p.Results.fll_ki); 
lcaPut([name 'PLL:CTRL:KP_S'],p.Results.fll_kp);
lcaPut([name 'PLL:CTRL:MIN_MAG_S'],p.Results.fll_min_magnitude);
lcaPut([name 'PLL:CTRL:MAX_OFFSET_S'],p.Results.fll_max_offset);
lcaPut([name 'PLL:CTRL:TARGET_S'],p.Results.fll_target_phase);

% Set up the NCO for the FLL loop
lcaPut([name 'PLL:NCO:GAIN_DB_S'],p.Results.fll_nco_gain);
lcaPut([name 'PLL:NCO:FREQ_S'],tune);
lcaPut([name 'PLL:NCO:ENABLE_S'],'On');

% Start feedback loop. 
%Check whether we're still running after 1 second

lcaPut([name 'PLL:CTRL:START_S.PROC'],0);
pause(1)
status=lcaGet([name 'PLL:CTRL:STATUS']);
display(['PLL is: ' cell2mat(status)]);




