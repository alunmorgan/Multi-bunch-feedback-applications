function plot_data_from_mbf_memory(data)


% Generating the frequency scales
n_bunches = data.n_turns .* data.harmonic_number;
timescale = (1:n_bunches) ./ data.RF; %sec
timestep = timescale(2) - timescale(1);
% f_scale = 1./timestep .* (-(n_bunches/2)+1:(n_bunches/2)) ./n_bunches; %Hz
f_scale = 1./timestep .* (0:n_bunches-1) ./n_bunches; %Hz

xf1 = abs(fft(data));

figure('Position', [20, 40, 800, 800])
t = tiledlayout(2, 1);
title(t, {['MBF data ', mbf_axis,' axis '];...
    ['Memory location:', target_location, ' ', trgt_extra]})
nexttile;
plot(timescale/timestep, data, 'DisplayName', 'Raw data')
ylabel(' ')
xlabel('Ticks of 2ns')
legend
grid on
% xlim([x_plt_axis(1) x_plt_axis(end)])
nexttile;
plot(f_scale(1:n_bunches/2) * 1E-6, xf1(1:n_bunches/2), 'DisplayName', 'Raw frequency')
ylabel(' ')
xlabel('Frequency (MHz)')
legend
grid on
% xlim([x_plt_axis(1) x_plt_axis(end)])


