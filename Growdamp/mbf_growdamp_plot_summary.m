function mbf_growdamp_plot_summary(poly_data, frequency_shifts)
% Plots the driven growth rates, and the active and pasive damping rates
% across all modes.
%
% Args:
%       poly_data ():
%       frequency_shifts ():
% Example: mbf_growdamp_plot_summary(growdamp, poly_data, frequency_shifts)

% Getting the desired system setup parameters.
[~, harmonic_number, ~] = mbf_system_config;

figure
ax1 = subplot(2,1,1);
x_plt_axis = (1:harmonic_number) - harmonic_number/2;
plot(x_plt_axis, circshift(-(squeeze(poly_data(:,2,1))), harmonic_number/2))
xlim([x_plt_axis(1) x_plt_axis(end)])
title('Damping rates for different modes')
xlabel('Mode')
ylabel('Damping rates (1/turns)')

ax2 = subplot(2,1,2);
plot(x_plt_axis, circshift(frequency_shifts, harmonic_number/2))
xlim([x_plt_axis(1) x_plt_axis(end)])
title('Tune shift from excitation')
xlabel('Mode')
ylabel('Difference from excitation tune')

linkaxes([ax1, ax2], 'x')