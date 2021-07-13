function growdamp_all
% Top level function to run all growdamp measurements of each plane
% sequentially.

mbf_tools

% Programatiaclly press the tune only button on each system
% then get the tunes
setup_operational_mode("x", "TuneOnly")
x_tune = lcaGet('SR23C-DI-TMBF-01:X:TUNE:TUNE');
if isnan(x_tune)
    x_tune = lcaGet('SR23C-DI-TMBF-01:X:TUNE:TUNE');
end %if
setup_operational_mode("y", "TuneOnly")
y_tune =  lcaGet('SR23C-DI-TMBF-01:Y:TUNE:TUNE');
if isnan(y_tune)
    y_tune = lcaGet('SR23C-DI-TMBF-01:Y:TUNE:TUNE');
end %if
setup_operational_mode("s", "TuneOnly")
s_tune = lcaGet('SR23C-DI-LMBF-01:IQ:TUNE:TUNE');
if isnan(s_tune)
    s_tune = lcaGet('SR23C-DI-LMBF-01:IQ:TUNE:TUNE');
end %if

mbf_growdamp_setup('x', x_tune)
growdamp_x = mbf_growdamp_capture('x');

mbf_growdamp_setup('y', y_tune)
growdamp_y = mbf_growdamp_capture('y');

mbf_growdamp_setup('s', s_tune)
growdamp_s = mbf_growdamp_capture('s');

% Programatiaclly press the tune only button on each system
setup_operational_mode("x", "TuneOnly")
setup_operational_mode("y", "TuneOnly")
setup_operational_mode("s", "TuneOnly")

[poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x);
mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, ...
    'outputs', 'both', 'axis', 'x')

[poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y);
mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, ...
    'outputs', 'both', 'axis', 'y')

[poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s);
mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s,...
    'outputs', 'both', 'axis', 's')

