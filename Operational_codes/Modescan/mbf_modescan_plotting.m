function mbf_modescan_plotting(data_magnitude, data_phase, modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       data_magnitude():
%       data_phase():
%       harmonic_number():
%
% Example: mbf_modescan_plotting(data_magnitude, data_phase, harmonic_number)
if ~isfield(modescan, 'harmonic_number')
    modescan.harmonic_number = 936;
end %if
harmonic_number = modescan.harmonic_number;
figure
subplot(2,1,1)
plot(data_magnitude(1:harmonic_number))
title(['Amplitude (', modescan.ax_label, ' ', num2str(modescan.time(3)),...
    '/', num2str(modescan.time(2)), '/',...
    num2str(modescan.time(1)), ' - ', num2str(modescan.time(4)), ':',...
    num2str(modescan.time(5)), ')'])
xlabel('Modes')
xlim([1,harmonic_number])
subplot(2,1,2)
plot(data_phase(1:harmonic_number))
title('Phase (deg)')
xlabel('Modes')
xlim([1, harmonic_number])