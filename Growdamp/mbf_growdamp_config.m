function settings = mbf_growdamp_config(mbf_axis)
% Contains the axis specific settings desired for the growdamp experiment.
%
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are
%                       requesting
%
% Example: settings = mbf_growdamp_config('x')

if strcmpi(mbf_axis, 'x')
    settings.axis_label = 'x';
    settings.axis_number = 1;
    settings.ex_level = -18; % excitation level in dB.
    settings.tune_offset = 0; % an offset to the PLL tune
    settings.durations = [250, 250, 250, 500]; %[excitation, passive damping, active damping, gap]
    settings.dwell = 1;
    settings.tune_sweep_range = [80.00500, 80.49500];
    settings.det_input = 'FIR';
elseif strcmpi(mbf_axis, 'y')
    settings.axis_label = 'y';
    settings.axis_number = 2;
    settings.ex_level = -18; % excitation level in dB.
    settings.tune_offset = 0; % an offset to the PLL tune
    settings.durations = [250, 250, 250, 500]; %[excitation, passive damping, active damping,gap]
    settings.dwell = 1;
    settings.tune_sweep_range = [80.00500, 80.49500];
    settings.det_input = 'FIR';
elseif strcmpi(mbf_axis, 's')
    settings.axis_label = 's';
    settings.axis_number = 3;
    settings.ex_level = -18; % excitation level in dB.
    settings.tune_offset = 0; % an offset to the PLL tune
    settings.durations = [10, 10, 50, 100]; %[excitation, passive damping, active damping, gap]
    settings.dwell = 480;
    settings.tune_sweep_range = [80.00220, 80.00520];
    settings.det_input = 'FIR';
end %if