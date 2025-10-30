function setup_for_bunch_train(mbf_axis, train_length, tune_mode)
% This allows the setup of the MBF to be adjusted to be suitable for the
% different bunch train lengths. The system will ignore anything not in the
% bunch train
% Inputs:
%        mbf_axis (str): axis to apply the settings to. ('x' or 'y')
%        train_length (int): length of train to apply tune measurement and
%                            feedback to. Starts from first bunch as per the 
%                            master timing generator.
%        tune_mode (str): type of tune setup to use ('all, 'comb'). These
%                         patterns will only be applied for the length of 
%                         the train.
%
% Example: setup_for_bunch_train('x', 686, 'comb')

PV_base = 'SR23C-DI-TMBF-01:';
detector0 =  ':DET:0:BUNCHES_S';
sequencer1 = ':BUN:1:SEQ:ENABLE_S';
excitation = ':SEQ:1:GAIN_DB_S';
feedback0 = ':BUN:0:FIR:ENABLE_S';
feedback1 = ':BUN:1:FIR:ENABLE_S';

expectedAxes = {'x','X', 'y', 'Y'};
expectedTuneModes = {'all', 'comb'};

p = inputParser;
addRequired(p,'mbf_axis',@(x) any(validatestring(x,expectedAxes)));
addRequired(p,'train_length', @isnumeric);
addRequired(p,'tune_mode',@(x) any(validatestring(x,expectedTuneModes)));

parse(p, mbf_axis, train_length, tune_mode);

selected_axis = upper(p.Results.mbf_axis);

enable_wfm = zeros(936,1);
tune_enable_wfm = zeros(936,1);
for js = 1:686
    enable_wfm(js) = 1;
    if strcmpi(p.Results.tune_mode, 'comb') && rem(js +50, 90) == 0
        tune_enable_wfm(js) = 1;
    elseif strcmpi(p.Results.tune_mode, 'all')
        tune_enable_wfm(js) = 1;
    end %if
end %for

% Set up tune measurement
lcaPut([PV_base, selected_axis, detector0], tune_enable_wfm')
lcaPut([PV_base, selected_axis, sequencer1], tune_enable_wfm')
if strcmpi(p.Results.tune_mode, 'comb')
    lcaPut([PV_base, selected_axis, excitation], -36.12)
elseif strcmpi(p.Results.tune_mode, 'all')
    lcaPut([PV_base, selected_axis, excitation], -54.19)
 end %if

%Set up feedback
lcaPut([PV_base, selected_axis, feedback0], enable_wfm')
lcaPut([PV_base, selected_axis, feedback1], enable_wfm')