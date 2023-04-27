function settings = mbf_tunescan_over_modes_config(mbf_axis)
% Contains the axis specific settings desired for the tunescan experiment.
%
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
%                       requesting
%
% Example: settings = mbf_tunescan_config('x')

if strcmpi(mbf_axis, 'x')
    settings.axis_label = 'x';
    settings.axis_number = 1;
    settings.ex_level = -18; % excitation level in dB.
    settings.dwell = 200;
    settings.det_gain = -24; % detector gain in dB.
    settings.seq_gain = -42; % sequencer gain in dB.
elseif strcmpi(mbf_axis, 'y')
    settings.axis_label = 'y';
    settings.axis_number = 2;
    settings.ex_level = -18; % excitation level in dB.
    settings.dwell = 200;
    settings.det_gain = -24; % detector gain in dB.
    settings.seq_gain = -42; % sequencer gain in dB.
elseif strcmpi(mbf_axis, 's')
    settings.axis_label = 's';
    settings.axis_number = 3;
    settings.ex_level = -18; % excitation level in dB.
    settings.dwell = 200;
    settings.det_gain = -24; % detector gain in dB.
    settings.seq_gain = -42; % sequencer gain in dB.
end %if