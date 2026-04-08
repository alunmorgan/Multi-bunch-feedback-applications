function setup_tune_bunch_selection(mbf_axis)
% This allows the setup of the tune to be adjusted from using all bunches to
% using a subset. This is useful if the tune measurement is struggling due to
% distortion of the IQ plot. Defaults to all bunches.
%
% Example: setup_tune_bunch_selection('x', 40, 90, 10)


[~, harmonic_number, pv_names, ~] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);
detector0 =  pv_names.tails.Detector.det0.bunch_selection;
sequencer1 = pv_names.tails.Bunch_bank.bank1.SEQ.enablewf;

expectedAxes = {'x','X', 'y', 'Y'};
valid_positive_number = @(x) isnumeric(x) && isscalar(x) && (x >= 0);

p = inputParser;
addRequired(p,'mbf_axis',@(x) any(validatestring(x,expectedAxes)));
addParameter(p,'start_bunch', 1, valid_positive_number);
addParameter(p,'step_bunch', 1, valid_positive_number);
addParameter(p,'n_bunch', harmonic_number, valid_positive_number);

parse(p, mbf_axis, tune_mode);

det_enable_wfm = zeros(harmonic_number,1);
for js = 1:p.Results.n_bunch
    det_enable_wfm(p.Results.start_bunch + (js - 1) * p.Results.step_bunch) = 1;
end %for
lcaPut([pv_head, detector0 ], det_enable_wfm')
lcaPut([pv_head, sequencer1], det_enable_wfm')
