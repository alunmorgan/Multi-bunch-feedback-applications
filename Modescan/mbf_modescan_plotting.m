function mbf_modescan_plotting(modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       modescan (structure): The results from modescan capture.
%
% Example: mbf_modescan_plotting(modescan)
harmonic_number = 936;
figure
subplot(2,1,1)
plot(abs(modescan.magnitude(1:harmonic_number)))
title(['Amplitude (', modescan.ax_label, ' ', num2str(modescan.time(3)),...
    '/', num2str(modescan.time(2)), '/',...
    num2str(modescan.time(1)), ' - ', num2str(modescan.time(4)), ':',...
    num2str(modescan.time(5)), ')'])
xlabel('Modes')
xlim([1,harmonic_number])
subplot(2,1,2)
plot(unwrap(modescan.phase(1:harmonic_number)/180*pi)/pi*180 - modescan.phase(1))
title('Phase (deg)')
xlabel('Modes')
xlim([1, harmonic_number])