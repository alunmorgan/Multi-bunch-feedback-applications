function tests = test_mbf_pll_start
% Test case for mbf_pll_start function
tests = functiontests(localfunctions);
end

function test_mbf_pll_bank_setup_input_checks(testCase)
% Set up test parameters
mbf_axis = 'x';  % Choose an MBF system (x, y, or s)
pllbunches = 400;  % Specify pllbunches (optional, default: 400)
guardbunches = 2;  % Specify guardbunches (optional, default: 2)
pll_nco_gain = -30;  % Specify pll_nco_gain (optional, default: -30)
target_phase = 180;  % Specify target_phase (optional, default: 180)

% Add assertions to verify the expected behavior
assert(strcmp(mbf_axis, 'x') && pllbunches == 400 && guardbunches == 2, ...
    'mbf_pll_bank_setup was not called correctly');
assert(strcmp(mbf_axis, 'x'), 'mbf_pll_detector_setup was not called correctly');
assert(strcmp(mbf_axis, 'x') && target_phase == 180 && pll_nco_gain == -30, ...
    'pll_initialisation was not called correctly');

%% Test invalid input: Non-numeric coefficients
assertError(@() mbf_pll_start(mbf_axis, 'pllbunches', 'invalid'), ...
    'quadraticSolver:InputMustBeNumeric');

%% Test invalid input: Non-scalar guardbunches
assertError(@() mbf_pll_start(mbf_axis, 'guardbunches', [1 2]), ...
    'quadraticSolver:InputMustBeNumeric');

%% Test invalid input: Non-numeric pll_nco_gain
assertError(@() mbf_pll_start(mbf_axis, 'pll_nco_gain', 'invalid'), ...
    'quadraticSolver:InputMustBeNumeric');

%% Test invalid input: Non-numeric target_phase
assertError(@() mbf_pll_start(mbf_axis, 'target_phase', 'invalid'), ...
    'quadraticSolver:InputMustBeNumeric');


end

