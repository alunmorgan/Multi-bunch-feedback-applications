function mbf_modescan_plotting(modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       modescan (structure): The results from modescan capture.
%
% Example: mbf_modescan_plotting(modescan)
harmonic_number = modescan.harmonic_number;
n_repeats = length(modescan.magnitude);
for ks = 1:n_repeats
    magnitude(:,ks) = abs(modescan.magnitude{ks});
        phase(:,ks) = modescan.phase{ks};
%     phase(:,ks) = unwrap(modescan.phase{ks}/180*pi)/pi*180;
end %for
magnitude = sum(magnitude,2) ./ n_repeats;
phase = sum(phase,2) ./ n_repeats;
phase = unwrap(phase/180*pi)/pi*180;
phase = phase - phase(1);

figure
subplot(2,1,1)
plot(magnitude(1:harmonic_number))
title(['Amplitude (', modescan.ax_label, ' ', num2str(modescan.time(3)),...
    '/', num2str(modescan.time(2)), '/',...
    num2str(modescan.time(1)), ' - ', num2str(modescan.time(4)), ':',...
    num2str(modescan.time(5)), ')'])
xlabel('Modes')
xlim([1,harmonic_number])
subplot(2,1,2)
plot(phase(1:harmonic_number))
title('Phase (deg)')
xlabel('Modes')
xlim([1, harmonic_number])