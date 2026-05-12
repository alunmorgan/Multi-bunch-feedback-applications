function mbf_modescan_plotting(data_magnitude, data_phase, modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       data_magnitude(vector of floats): averaged signal magnitude over modes.
%       data_phase(vector of floats): averaged signal phase over modes.
%       modescan(structure): captured data
%
% Example: mbf_modescan_plotting(data_magnitude, data_phase, modescan)

figure("OuterPosition",[30, 400, 1200, 800])
t = tiledlayout(2, 2,'TileSpacing','compact', 'Padding', 'tight');
title(t, {['MBF modescan results ', modescan.ax_label,...
    ' axis ', datestr(modescan.time)];...
    ['Current: ', num2str(round(modescan.current)), 'mA']})

ax1 = nexttile(1);
plot(data_magnitude(1:modescan.harmonic_number))
xlim([1,modescan.harmonic_number])
title('Amplitude')
xlabel('Modes')
grid on

ax3 = nexttile(3);
plot(data_phase(), 'DisplayName', 'data', 'LineWidth',2)
hold on 
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*-90,...
    ':r', 'DisplayName','Limits', 'LineWidth',2)
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*90,...
    ':r', 'LineWidth',2, 'HandleVisibility','off')
hold off
title('Phase (deg)')
xlim([1, modescan.harmonic_number])
legend('Location','northoutside')
xlabel('Modes')
grid on

x_data_p1 = (modescan.RF ./ modescan.harmonic_number) .*...
    ((0:(modescan.harmonic_number)/2 - 1) +...
    modescan.tunes.([modescan.ax_label,'_tune']).tune);

x_data_p2 = modescan.RF -...
    (modescan.RF ./ modescan.harmonic_number) .*...
    ((modescan.harmonic_number / 2):(modescan.harmonic_number - 1) +...
    modescan.tunes.([modescan.ax_label,'_tune']).tune);

x_data = cat(2, x_data_p1, x_data_p2);
[x_data, I] = sort(x_data);
data_mag = data_magnitude(I);
data_phse = data_phase(I);

ax2 = nexttile(2);
plot(x_data * 1E-6, data_mag)
xlim([0,max(x_data* 1E-6)])
title('Amplitude')
xlabel('Frequency (MHz)')
grid on

ax4 = nexttile(4);
plot(x_data* 1E-6, data_phse, 'DisplayName', 'data', 'LineWidth',2)
% take the mean of an even number of points to make things more robust.
grad_start = mean(data_phse(1:4));
grad_end = mean(data_phse(end-4:end));
target_grad = (grad_end - grad_start) / x_data(end);
phase_offset = x_data .* target_grad;
hold on 
phase_angle = round(phase_offset(end)*10)/10;
delay_time = round(phase_offset(end)./(360 * x_data(end)) * 1E12);
velocity_factor = 0.7;
adjustment_length = round(delay_time .* 1E-12.* velocity_factor * 3E8 .* 1E3);
plot(phase_offset + grad_start, 'DisplayName', ['fit ', num2str(phase_angle),...
    ' degrees total, delay = ', num2str(delay_time),...
    'ps, adjustment length approx ', num2str(adjustment_length), 'mm'],...
    'LineWidth',2)
plot(x_data* 1E-6, ones(length(x_data),1)*-90,...
    ':r', 'DisplayName','Limits', 'LineWidth',2)
plot(x_data* 1E-6, ones(length(x_data),1)*90,...
    ':r', 'LineWidth',2, 'HandleVisibility','off')
hold off
title('Phase (deg)')
xlim([1, max(x_data* 1E-6)])
legend('Location','northoutside')
xlabel('Frequency (MHz)')
grid on

linkaxes([ax1, ax3], 'x')
linkaxes([ax2, ax4], 'x')
linkaxes([ax1, ax2], 'y')
linkaxes([ax3, ax4], 'y')