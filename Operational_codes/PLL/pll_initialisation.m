function pll_initialisation(mbf_axis, varargin)
% This is to start the frequency locked loop (fll) [also called pll] from
% scratch. Once the initial lock is found then the settings are changed to
% improve tracking. if signal is lost this process can be run again.
% mbf_axis(str): x, y, or s

default_pll_ki = 1000; %safe also for for low charge, sharp resonance 
default_pll_kp = 0;
default_pll_min_magnitude = 0;
default_pll_locking_max_offset = 0.003;
default_pll_tracking_max_offset = 0.02;
default_pll_nco_gain = -30; % in dB
default_tune_override = NaN;
default_pll_target_phase = 160;
% For LMBF
%  default_pll_ki =100; %safe also for for low charge, sharp resonance
%     default_pll_kp = 0;
%     default_pll_max_offset = 0.001;

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
validScalarNum = @(x) isnumeric(x) && isscalar(x);
p = inputParser;
addRequired(p, 'name', @ischar);
addParameter(p, 'pll_ki', default_pll_ki, validScalarPosNum);
addParameter(p, 'pll_kp', default_pll_kp, validScalarNum);
addParameter(p, 'pll_min_magnitude', default_pll_min_magnitude, validScalarNum);
addParameter(p, 'pll_locking_max_offset', default_pll_locking_max_offset, validScalarPosNum);
addParameter(p, 'pll_tracking_max_offset', default_pll_tracking_max_offset, validScalarPosNum);
addParameter(p, 'pll_nco_gain', default_pll_nco_gain, validScalarNum);
addParameter(p, 'pll_target_phase', default_pll_target_phase, validScalarNum);
addParameter(p, 'tune_override', default_tune_override, validScalarNum);

parse(p,mbf_axis,varargin{:});

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

%% Checking tune
% starting frequency is taken from swept tune measurement. Can also
% be overridden from command line input (but then it will only work if tune
% feedback has brought the tune to the desired value...)
if isnan(p.Results.tune_override)
    % Perform a TUNE sweep, record phase at tune peak and the tune value
    tune_frequency_from_sweep = get_variable([mbf_names.(mbf_axis), mbf_vars.tune.centre]);
    if isnan(tune_frequency_from_sweep)
        error('pllInitialisation:invalidTuneFit', 'Tune fit invalid, cannot start PLL.')
    end %if
else
    tune_frequency_from_sweep = p.Results.tune_override;
    disp(['Using tune override of ', num2str(p.Results.tune_override)])
end %if

% Disable PLL and turn off the NCO
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.stop], 1);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.nco.enable],'Off');

% Set up the FLL feedback loop
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.i],p.Results.fll_ki); 
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.p],p.Results.fll_kp);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.minumum_magnitude],...
    p.Results.fll_min_magnitude);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.target_phase],...
    p.Results.fll_target_phase)

% Set up the NCO
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.nco.gain],...
    p.Results.fll_nco_gain);
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.nco.set_frequency],...
    tune_frequency_from_sweep)
% Limit tune range of the NCO for initial peak finding.
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.maximum_offset],...
    p.Results.fll_locking_max_offset)

% Enable the NCO and PLL
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.nco.enable],'On');
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.start], 1)

% Wait until PLL has locked (set lower bound to phase error?)
t1 = datetime("now");
while abs(abs(get_variable([mbf_names.(mbf_axis), mbf_vars.pll.readback.phase])) - ...
        abs( p.Results.fll_target_phase)) > 1 % within one degree of target.
    lock_time = datetime("now");
    if lock_time > t1 + seconds(10)
        disp('Unable to lock within 10 seconds')
        return
    end %if
end %while
% Once locked widen the NCO limits to max required for tracking
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.maximum_offset],...
    p.Results.fll_tracking_max_offset);


