function mbf_modescan_plotting(data_magnitude, data_phase, modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       data_magnitude(vector of floats): averaged signal magnitude over modes.
%       data_phase(vector of floats): averaged signal phase over modes.
%       modescan(structure): captured data
%
% Example: mbf_modescan_plotting(data_magnitude, data_phase, modescan)

figure("OuterPosition",[30, 400, 700, 900])
subplot(2,1,1)
plot(data_magnitude(1:modescan.harmonic_number))
title({['MBF modescan results ', modescan.ax_label, ' axis ', datestr(modescan.time)];...
    ['Current: ', num2str(round(modescan.current)), 'mA'];...
    'Amplitude'})
xlabel('Modes')
xlim([1,modescan.harmonic_number])
grid on
subplot(2,1,2)
modes = 1:modescan.harmonic_number;
plot(data_phase(), 'DisplayName', 'data', 'LineWidth',2)
data_end = sum(data_phase(modes))./ modes(end);
target_grad = data_end / modes(end);
y = modes .* target_grad;
hold on 
plot(y, 'DisplayName', ['fit', num2str(round(target_grad*100)/100), ' degrees / mode'], 'LineWidth',2)
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*-90, ':r', 'DisplayName','Limits', 'LineWidth',2)
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*90, ':r', 'LineWidth',2, 'HandleVisibility','off')
hold off
title('Phase (deg)')
xlabel('Modes')
xlim([1, modescan.harmonic_number])
legend('Location','northoutside')
grid on