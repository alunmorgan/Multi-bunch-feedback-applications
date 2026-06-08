function setup_feedback_for_bunch_train(mbf_axis, train_length, varargin)
% This allows the setup of the MBF to be adjusted to be suitable for the
% different bunch train lengths. The feedback will ignore anything not in the
% bunch train
% Inputs:
%        mbf_axis (str): axis to apply the settings to. ('x' or 'y')
%        train_length (int): length of train to apply tune measurement and
%                            feedback to. Starts from first bunch as per the
%                            master timing generator.
%        clear_previous(str): if yes removes existing enable patterns.
%                            Defaults to yes.
%
% Example: setup_for_bunch_train('x', 686)

[~, harmonic_number, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
% feedback during quiecent mode
feedback0 = pv_names.tails.Bunch_bank.bank0.FIR.enablewf;
% feedback during tune measurement
feedback1 = pv_names.tails.Bunch_bank.bank1.FIR.enablewf';

expectedAxes = @(x) any(validatestring(x,{'x', 'y'}));
boolean_str = @(x) any(validatestring(x,{'yes', 'no'}));
valid_positive_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

p = inputParser;
addRequired(p,'mbf_axis',expectedAxes);
addRequired(p,'train_length', valid_positive_number);
addParameter(p,'clear_previous', 'yes', boolean_str);

parse(p, mbf_axis, train_length, varargin{:});

if strcmpi('yes', p.Results.clear_previous)
    enable_feedback0 = zeros(harmonic_number,1);
    enable_feedback1 = zeros(harmonic_number,1);
else
    enable_feedback0 = get_variable([pv_head, feedback0]);
    enable_feedback1 = get_variable([pv_head, feedback1]);
end %if
for js = 1:train_length
    enable_feedback0(js) = 1;
    enable_feedback1(js) = 1;
end %for

% Apply changes
set_variable([pv_head, feedback0], enable_feedback0')
set_variable([pv_head, feedback1], enable_feedback1')