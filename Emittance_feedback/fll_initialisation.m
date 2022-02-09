function fll_initialisation(name, varargin)
% This is to start the frequency locked loop (fll) [also called pll] from
% scratch. Once the initial lock is found then the settings are changed to
% improve tracking. if signal is lost this process can be run again.
% base          <EPICS device>:<axis>

default_fll_ki = 1000; %safe also for for low charge, sharp resonance 
default_fll_kp = 0;
default_fll_min_magnitude = 0;
default_fll_max_offset = 0.02;
default_fll_nco_gain = -30; % in dB
default_tune_override = NaN;
default_fll_target_phase = 180;
% For LMBF
%  default_fll_ki =100; %safe also for for low charge, sharp resonance
%     default_fll_kp = 0;
%     default_fll_max_offset = 0.001;

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addRequired(p, 'name', @ischar);
addParameter(p, 'fll_ki', default_fll_ki, validScalarPosNum);
addParameter(p, 'fll_kp', default_fll_kp, validScalarNum);
addParameter(p, 'fll_min_magnitude', default_fll_min_magnitude, validScalarNum);
addParameter(p, 'fll_max_offset', default_fll_max_offset, validScalarPosNum);
addParameter(p, 'fll_nco_gain', default_fll_nco_gain, validScalarNum);
addParameter(p, 'fll_target_phase', default_fll_target_phase, validScalarNum);
addParameter(p, 'tune_override', default_tune_override, validScalarNum);

parse(p,name,varargin{:});

%% Checking tune
% starting frequency is taken from swept tune measurement. Can also
% be overridden from command line input (but then it will only work if tune
% feedback has brought the tune to the desired value...)
if isnan(p.Results.tune_override)
    % Perform a TUNE sweep, record phase at tune peak and the tune value
    tune_frequency_from_sweep = lcaGet([name, ':TUNE:TUNE']);
    if isnan(tune_frequency_from_sweep)
        error('Tune fit invalid, cannot start PLL.')
        return
    end %if
else
    tune_frequency_from_sweep = p.Results.tune_override;
    disp(['Using tune override of ', num2str(p.Results.tune_override)])
end %if

% Disable PLL and turn off the NCO
lcaPut([name, ':PLL:CTRL:STOP_S.PROC'], 1);
lcaPut([name ':PLL:NCO:ENABLE_S'],'Off');

% Set up the FLL feedback loop
lcaPut([name ':PLL:CTRL:KI_S'],p.Results.fll_ki); 
lcaPut([name ':PLL:CTRL:KP_S'],p.Results.fll_kp);
lcaPut([name ':PLL:CTRL:MIN_MAG_S'],p.Results.fll_min_magnitude);
lcaPut([name, ':PLL:CTRL:TARGET_S'], p.Results.fll_target_phase)

% Set up the NCO
lcaPut([name ':PLL:NCO:GAIN_DB_S'],p.Results.fll_nco_gain);
lcaPut([name, ':PLL:NCO:FREQ_S'], tune_frequency_from_sweep)
% Limit tune range of the NCO to +/- 0.002 for initial peak finding.
lcaPut([name, ':PLL:CTRL:MAX_OFFSET_S'], 0.002)

% Enable the NCO and PLL
lcaPut([name ':PLL:NCO:ENABLE_S'],'On');
lcaPut([name, ':PLL:CTRL:START_S.PROC'], 1)

% Wait until PLL has locked (set lower bound to phase error?)
t1 = now;
while abs(abs(lcaGet([name, ':PLL:FILT:PHASE'])) - ...
        abs( p.Results.fll_target_phase)) > 1 % within one degree of target.
    time = (now - t1) *24* 3600;
    if time >10
        disp('Unable to lock within 10 seconds')
        return
    end %if
end %while
% Once locked widen the NCO limits to max required for tracking
lcaPut([name ':PLL:CTRL:MAX_OFFSET_S'],p.Results.fll_max_offset);

