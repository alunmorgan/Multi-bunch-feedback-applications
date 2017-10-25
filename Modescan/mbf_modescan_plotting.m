function mbf_modescan_plotting(modescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       modescan (structure): The results from modescan capture.
%
% Example: mbf_modescan_plotting(modescan)

figure(1)
subplot(2,1,1)
plot(modescan.f_scale, abs(modescan.iq))
title('Amplitude')
xlabel('Modes')
subplot(2,1,2)
plot(modescan.f_scale, unwrap(angle(modescan.iq))/(2*pi)*360-180)
title('Phase (deg)')
xlabel('Modes')