function mbf_tunescan_over_modes_plotting(data_magnitude, data_phase, tunescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       data_magnitude():
%       data_phase():
%       harmonic_number():
%
% Example: mbf_tunescan_plotting(data_magnitude, data_phase, tunescan)
if ~isfield(tunescan, 'harmonic_number')
    tunescan.harmonic_number = 936;
end %if
harmonic_number = tunescan.harmonic_number;
figure
subplot(2,1,1)
plot(data_magnitude(1:harmonic_number))
title(['Amplitude (', tunescan.ax_label, ' ', num2str(tunescan.time(3)),...
    '/', num2str(tunescan.time(2)), '/',...
    num2str(tunescan.time(1)), ' - ', num2str(tunescan.time(4)), ':',...
    num2str(tunescan.time(5)), ')'])
xlabel('Modes')
xlim([1,harmonic_number])
subplot(2,1,2)
plot(data_phase(1:harmonic_number))
title('Phase (deg)')
xlabel('Modes')
xlim([1, harmonic_number])