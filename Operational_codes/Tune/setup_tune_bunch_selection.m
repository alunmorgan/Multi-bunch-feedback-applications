function setup_tune_bunch_selection(mbf_axis, tune_mode)
% This allows the setup of the tune to be adjusted from using all bunches to
% using a subset. This is useful if the tune measurement is struggling due to
% distortion of the IQ plot.
%
% Example: setup_tune_bunch_selection('x', 'comb')

PV_base = 'SR23C-DI-TMBF-01:';
detector0 =  ':DET:0:BUNCHES_S';
sequencer1 = ':BUN:1:SEQ:ENABLE_S';
excitation = ':SEQ:1:GAIN_DB_S';

expectedAxes = {'x','X', 'y', 'Y'};
expectedModes = {'all', 'comb'};
p = inputParser;
addRequired(p,'mbf_axis',@(x) any(validatestring(x,expectedAxes)));
addRequired(p,'tune_mode',@(x) any(validatestring(x,expectedModes)));
parse(p, mbf_axis, tune_mode);

selected_axis = upper(p.Results.mbf_axis);

if strcmpi(p.Results.tune_mode, 'comb')
    % setup tune using 10 bunches spaced 90 bucket apart.
    det_enable_wfm = zeros(936,1);
    for js = 1:10
        det_enable_wfm(js * 90) = 1;
    end %for
    lcaPut([PV_base, selected_axis, detector0 ], det_enable_wfm')
    lcaPut([PV_base, selected_axis, sequencer1], det_enable_wfm')
    lcaPut([PV_base, selected_axis, excitation], -36.12)
elseif strcmpi(p.Results.tune_mode, 'all')
    % revert back to using all bunches.
    det_enable_wfm = ones(936,1);
    lcaPut([PV_base, selected_axis, detector0], det_enable_wfm')
    lcaPut([PV_base, selected_axis, sequencer1], det_enable_wfm')
    lcaPut([PV_base, selected_axis, excitation], -54.19)
else
    warning('Please select all or comb')
end %if