function tunes = get_all_tunes(varargin)
% captures the current tune on all MBF systems.
% if the value is NaN the code will try again for up to 20 tries.
%   Args:
%       selected_axes(str): 'xys'
%
%   Returns:
%       tunes(struct): tune and sideband values.
%
% Example: tunes = get_all_tunes('xy')

default_axes = 'xys';

p = inputParser;
addParameter(p, 'axes', default_axes);
parse(p, varargin{:});

[~, ~, pv_names] = mbf_system_config;

n_trys = 20;
% Initialisation and ensuring the datastructure is consistent regardless of the
% number of axes asked for.
tunes.x_tune.tune = NaN;
tunes.x_tune.lower_sideband = NaN;
tunes.x_tune.upper_sideband = NaN;
tunes.y_tune.tune = NaN;
tunes.y_tune.lower_sideband = NaN;
tunes.y_tune.upper_sideband = NaN;
tunes.s_tune.tune = NaN;
tunes.s_tune.lower_sideband = NaN;
tunes.s_tune.upper_sideband = NaN;

% Finding the current tunes for the requested axes.
for bds = 1:length(p.Results.axes)
    temp_axis = p.Results.axes(bds);
    ax_name = [temp_axis, '_tune'];
    for nfs = 1:n_trys
        try
        tunes.(ax_name).tune = get_variable([pv_names.hardware_names.(temp_axis), pv_names.tails.tune.centre]);
        catch
            tunes.(ax_name).tune = NaN;
        end %try
        try
        tunes.(ax_name).lower_sideband = get_variable([pv_names.hardware_names.(temp_axis), pv_names.tails.tune.left]);
        catch
            tunes.(ax_name).lower_sideband = NaN;
        end %try
        try
        tunes.(ax_name).upper_sideband = get_variable([pv_names.hardware_names.(temp_axis), pv_names.tails.tune.right]);
        catch
            tunes.(ax_name).upper_sideband = NaN;
        end %try
        
        if nfs == n_trys && isnan(tunes.(ax_name).tune)
            disp(['Unable to get ', temp_axis, ' axis tune value'])
            continue
        end %if
        if isnan(tunes.(ax_name).tune)
            pause(0.3)
        end %if
    end %for
end %for
