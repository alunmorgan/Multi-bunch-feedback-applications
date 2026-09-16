selected_axis = 'y';

I10B_closed8 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
I10B_closed12 = emittance_control_loop(selected_axis, 12, 'continual', 'no');
I10B_closed8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60')

I10B_phase8 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
I10B_phase12 = emittance_control_loop(selected_axis, 12, 'continual', 'no');
I10B_phase8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60')

I10B_open8 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
I10B_open12 = emittance_control_loop(selected_axis, 12, 'continual', 'no');
I10B_open8_2 = emittance_control_loop(selected_axis, 8, 'continual', 'no');
lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S', '-60')



figure(3)
hold on
x1 = linspace(0,300, 600);
y1 = cat(2,I10B_closed8 .u_log, I10B_closed12 .u_log, I10B_closed8_2 .u_log);
y2 = cat(2,I10B_open8 .u_log, I10B_open12 .u_log, I10B_open8_2 .u_log);
y3 = cat(2,I10B_phase8 .u_log, I10B_phase12 .u_log, I10B_phase8_2 .u_log);

plot(x1, y1)
plot(x1, y2)
plot(x1, y3)
plot(x1, y4)
hold off
