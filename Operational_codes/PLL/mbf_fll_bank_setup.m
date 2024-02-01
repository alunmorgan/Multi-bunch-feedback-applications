function mbf_fll_bank_setup(mbf_axis, varargin)
% Sets up the banks for FLL operation.
%
%   mbf_axis(str): x, y, or s
%   pllbunches (float or list of floats): bunches numbers to use for PLL (0-935)
%                                         (defaults to 400)
%   guardbunches (int): number of bunches around PLL to also take out
%                       of sweeper (defaults to 2)
%
% example: mbf_fll_bank_setup(name,pllbunches,guardbunches)

default_guard = 2;
default_bunch = 400;

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_number = @(x) isnumeric(x) && isscalar(x);
addRequired(p, 'mbf_axis');
addParameter(p, 'fllbunches', default_bunch);
addParameter(p, 'guardbunches', default_guard, valid_number);

parse(p, mbf_axis, varargin{:});

guardbunches = p.Results.guardbunches;
fllbunches = mod(p.Results.fllbunches, 935);

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

% initialise pll pattern
pllpattern=false(1,936);
% Matlab counts idices from 1, but at DLS we count bunches from 0, thus we need to
% add one.
pllpattern(fllbunches+1) = true;

% now we want to create a pattern with a little more room around the
% pll bunches. It's a little tricky with a general pattern, and the cirular
% nature the pattern, so I use circshift in a loop

guardpattern=true(1,936);
for n=-guardbunches:guardbunches
    guardpattern(circshift(pllpattern,n)) = false;
end

% Set up PLL bunches in banks 0 and 1 (those are used in typcal sweeps), 
% and in PLL detector.

set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank0.PLL.enablewf],...
    double(pllpattern));
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank1.PLL.enablewf],...
    double(pllpattern));
set_variable([mbf_names.(mbf_axis), mbf_vars.pll.detector.target_bunches],...
    double(pllpattern));

% Set sweep (SEQ) and its detector (#1) to NOT operate on these and
% guard bunches around, ie only on guardpattern. 
%check or add to any previous config and uses logical AND to insert the
%guardpattern into the existing setup.
sequencer =get_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank1.SEQ.enablewf]);
detector = get_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det0.bunch_selection]);
set_variable([mbf_names.(mbf_axis), mbf_vars.Bunch_bank.bank1.SEQ.enablewf],...
    double(and(guardpattern, sequencer)));
set_variable([mbf_names.(mbf_axis), mbf_vars.Detector.det0.bunch_selection],...
    double(and(guardpattern, detector)));
