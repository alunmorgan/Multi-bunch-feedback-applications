function mbf_modescan_plotting(data_magnitude, data_phase, modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       data_magnitude(vector of floats): averaged signal magnitude over modes.
%       data_phase(vector of floats): averaged signal phase over modes.
%       modescan(structure): captured data
%
% Example: mbf_modescan_plotting(data_magnitude, data_phase, modescan)

figure
subplot(2,1,1)
plot(data_magnitude(1:modescan.harmonic_number))
title(['Amplitude (', modescan.ax_label, ' ', num2str(modescan.time(3)),...
    '/', num2str(modescan.time(2)), '/',...
    num2str(modescan.time(1)), ' - ', num2str(modescan.time(4)), ':',...
    num2str(modescan.time(5)), ')'])
xlabel('Modes')
xlim([1,modescan.harmonic_number])
grid on
subplot(2,1,2)
plot(data_phase(1:modescan.harmonic_number), 'DisplayName', 'data', 'LineWidth',2)
p = polyfit(1:modescan.harmonic_number, data_phase(1:modescan.harmonic_number), 1);
y = polyval(p,1:modescan.harmonic_number);
hold on 
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*-90, ':r', 'DisplayName','Limits', 'LineWidth',2)
plot(1:modescan.harmonic_number, ones(modescan.harmonic_number,1)*90, ':r', 'LineWidth',2, 'HandleVisibility','off')
hold off
title('Phase (deg)')
xlabel('Modes')
xlim([1, modescan.harmonic_number])
legend
grid on