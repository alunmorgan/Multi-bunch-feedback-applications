function mbf_pll_start(mbf_axis, pllbunches, varargin)
% function mbf_pll_start(name,pllbunches,guardbunches)
%
% mbf_axis(str): x, y, or s      
% pllbunches    bunches numbers to use for PLL (0-935)
% guardbunches  number of bunches around PLL to also take out of sweeper
%               (defaults to 2)

[~, harmonic_number, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};

default_guardbunches = 2;

errorMsg_gb = 'Value must be positive, scalar, and numeric.'; 
errorMsg_pb = ['Value must be numeric and within the range 0 - ', num2str(harmonic_number),'.']; 

addRequired(p, 'mbf_axis', @(x) any(validatestring(x, axis_string)));
addRequired(p, 'pllbunches', @(x) assert(isnumeric(x) && (x >= 0) && (x < harmonic_number),errorMsg_pb));
addParameter(p, 'guardbunches', default_guardbunches, @(x) assert(isnumeric(x) && isscalar(x) ...
    && (x > 0),errorMsg_gb));

parse(p, mbf_axis, pllbunches, varargin{:});

% initialise pll pattern
pllpattern=false(1,harmonic_number);
% Matlab counts idices from 1, but at DLS we count bunches from 0, thus we need to
% add one.
pllpattern(pllbunches+1)=true;

% now we want to create a pattern with a little more room around the
% pll bunches. It's a little tricky with a general pattern, and the cirular
% nature the pattern, so I use circshift in a loop

guardpattern=true(1,harmonic_number);
for n=-guardbunches:guardbunches
    guardpattern(circshift(pllpattern,n))=false;
end

% Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps), 
% and in PLL detector.

set_variable([mbf_names.(mbf_axis) mbf_vars.Bunch_bank.bank0.PLL.enablewf],...
    double(pllpattern));
set_variable([mbf_names.(mbf_axis) mbf_vars.Bunch_bank.bank1.PLL.enablewf],...
    double(pllpattern));
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.target_bunches],...
    double(pllpattern));

% Set sweep (SEQ) and its detector (#1) to NOT operate on these and
% guard bunches around, ie only on guardpattern. This is maybe a little
% keen, as there might be other things configured, which this will jjst
% plow over. Maybe we should check or add to any previous config...

set_variable([mbf_names.(mbf_axis) mbf_vars.Bunch_bank.bank1.SEQ.enablewf],...
    double(guardpattern));
set_variable([mbf_names.(mbf_axis) mbf_vars.Detector.det0.bunch_selection],...
    double(guardpattern));

% Now comes some setup with 'working values'. These ought to be read from a
% config file or be additinal arguments in the future.

set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.mode],'ADC no fill');
set_variable([mbf_names.(mbf_axis) mbf_vars.adc.reject_count],'128 turns');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.scaling],'48dB');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.blanking],'Blanking');
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.detector.dwell],128);

set_variable([mbf_names.(mbf_axis) mbf_vars.pll.i],1000); %safe also for for low charge, sharp resonance
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.p],0);
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.minumum_magnitude],0);
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.maximum_offset],0.02);
set_variable([mbf_names.(mbf_axis) mbf_varss.pll.target_phase],-180);

% starting frequency is taken form swept tune measurement, but could also
% be configured from config file (but then it will only work if tune
% feedback has brought the tune to the desired value...)

tune=get_variable([mbf_names.(mbf_axis) mbf_vars.tune.centre],1,'double');
if isnan(tune)
    error('PLL:invalidTuneFit', 'Tune fit invalid, cannot start PLL.')
    %tune=37.45;
end

set_variable([mbf_names.(mbf_axis) mbf_vars.pll.nco.gain],-30);
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.nco.set_frequency],tune);
set_variable([mbf_names.(mbf_axis) mbf_vars.pll.nco.enable],'On');

% finally, lets start, and then check whether we're still running after 1
% second

set_variable([mbf_names.(mbf_axis) mbf_vars.pll.start],0);
pause(1)
status=get_variable([mbf_names.(mbf_axis) mbf_vars.pll.status]);
display(['PLL is: ' cell2mat(status)]);
