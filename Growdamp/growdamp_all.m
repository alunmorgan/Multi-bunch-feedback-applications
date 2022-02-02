function growdamp_all
% Top level function to run all growdamp measurements of each plane
% sequentially.

mbf_tools

% Get the tunes
 tunes = get_all_tunes('xys');
x_tune = tunes.x_tune;
y_tune = tunes.y_tunes;
s_tune = tunes_s_tunes;

if isnan(x_tune.tune) || ...
    isnan(y_tune.tune) || ...
    isnan(s_tune.tune)
    disp('Could not get all tune values')
    return
end %if

mbf_growdamp_setup('x', x_tune.tune)
growdamp_x = mbf_growdamp_capture('x');

mbf_growdamp_setup('y', y_tune.tune)
growdamp_y = mbf_growdamp_capture('y');

mbf_growdamp_setup('s', s_tune.tune)
growdamp_s = mbf_growdamp_capture('s');


[poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x);
mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, ...
    'outputs', 'both', 'axis', 'x')

[poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y);
mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, ...
    'outputs', 'both', 'axis', 'y')

[poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s);
mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s,...
    'outputs', 'both', 'axis', 's')

% Programatically press the Feedback and tune button on each system
% and set the feedback gain to 0dB.
setup_operational_mode("x", "Feedback")
lcaPut('SR23C-DI-TMBF-01:X:FIR:GAIN_S', '0dB')
setup_operational_mode("y", "Feedback")
lcaPut('SR23C-DI-TMBF-01:Y:FIR:GAIN_S', '0dB')
setup_operational_mode("s", "Feedback")
lcaPut('SR23C-DI-LMBF-01:IQ:FIR:GAIN_S', '0dB')
