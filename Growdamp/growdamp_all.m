function growdamp_all(x_tune, y_tune, s_tune)

mbf_tools

mbf_growdamp_setup('x', x_tune)
growdamp_x = mbf_growdamp_capture('x');
[poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x);
mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, ...
    'outputs', 'both', 'axis', 'x')

mbf_growdamp_setup('y', y_tune)
growdamp_y = mbf_growdamp_capture('y');
[poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y);
mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, ...
    'outputs', 'both', 'axis', 'y')

mbf_growdamp_setup('s', s_tune)
growdamp_s = mbf_growdamp_capture('s');
[poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s);
mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s,...
    'outputs', 'both', 'axis', 's')

