function setup_tune_bunch_selection(mbf_axis, varargin)
% This allows the setup of the tune to be adjusted from using all bunches to
% using a subset. This is useful if the tune measurement is struggling due to
% distortion of the IQ plot. Defaults to all bunches.
% Inputs:
%       mbf_axis (str): axis to apply the settings to. ('x' or 'y')
%       start_bunch(int): The first position to take the tune measurement.
%       step_bunch(int): The spacing of measurement positions.
%       n_bunch(int): How many positions are used.
%       clear_previous(str): if yes removes existing enable patterns.
%                            Defaults to yes.
%
% Example: setup_tune_bunch_selection('x', 40, 90, 10)

[~, harmonic_number, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
%tune measurement
detector0 =  pv_names.tails.Detector.det0.bunch_selection;
%tune excitation
sequencer1 = pv_names.tails.Bunch_bank.bank1.SEQ.enablewf;

expectedAxes = @(x) any(validatestring(x,{'x', 'y'}));
boolean_str = @(x) any(validatestring(x,{'yes', 'no'}));
valid_positive_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

p = inputParser;
addRequired(p,'mbf_axis',expectedAxes);
addParameter(p,'start_bunch', 1, valid_positive_number);
addParameter(p,'step_bunch', 1, valid_positive_number);
addParameter(p,'n_bunch', harmonic_number, valid_positive_number);
addParameter(p,'clear_previous', 'yes', boolean_str);

parse(p, mbf_axis, varargin{:});

if strcmpi('yes', p.Results.clear_previous)
    det_enable_wfm = zeros(harmonic_number,1);
    seq_enable_wfm = zeros(harmonic_number,1);
else
    det_enable_wfm = get_variable([pv_head, detector0]);
    seq_enable_wfm = get_variable([pv_head, sequencer1]);
end %if
for js = 1:p.Results.n_bunch
    det_enable_wfm(p.Results.start_bunch + (js - 1) * p.Results.step_bunch) = 1;
    seq_enable_wfm(p.Results.start_bunch + (js - 1) * p.Results.step_bunch) = 1;
end %for

% Apply changes
set_variable([pv_head, detector0 ], det_enable_wfm')
set_variable([pv_head, sequencer1], seq_enable_wfm')
