function mbf_growdamp_plot_summary(poly_data, frequency_shifts)
% Plots the driven growth rates, and the active and pasive damping rates
% across all modes.
%
% Args:
%       poly_data (3 by 3 matrix): axis 1 is coupling mode.
%                                  axis 2 is expermental state,
%                                  excitation, natural damping, active damping). 
%                                  axis 3 is damping time, offset and 
%                                  fractional error.
%       frequency_shifts (list of floats): The frequency shift of each mode.
%
% Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts)

% Getting the desired system setup parameters.
harmonic_number = length(frequency_shifts);

x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
passive_data = squeeze(poly_data(:,2,1));
active_data = squeeze(poly_data(:,3,1));
passive_errors = NaN(length(passive_data),1);
passive_errors(isnan(passive_data)) = 0;
active_errors = NaN(length(active_data),1);
active_errors(isnan(active_data)) = 0;

f_shifts = frequency_shifts;
figure
ax1 = subplot(3,1,1:2);
plot(x_plt_axis, circshift(passive_data, -harmonic_number/2, 1), 'b')
hold on
plot(x_plt_axis, circshift(active_data, -harmonic_number/2, 1), 'g')
plot(x_plt_axis, zeros(length(x_plt_axis),1), 'r:')
plot(x_plt_axis, circshift(passive_errors, -harmonic_number/2, 1), 'c*')
plot(x_plt_axis, circshift(active_errors, -harmonic_number/2, 1), 'm*')
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
title('Damping rates for different modes')
xlabel('Mode')
ylabel('Damping rates (1/turns)')
legend('Passive', 'Active')

ax2 = subplot(3,1,3);
plot(x_plt_axis, circshift(f_shifts, -harmonic_number/2, 1))
xlim([x_plt_axis(1) x_plt_axis(end)])
title('Tune shift from excitation')
xlabel('Mode')
ylabel('Difference from excitation tune')

linkaxes([ax1, ax2], 'x')