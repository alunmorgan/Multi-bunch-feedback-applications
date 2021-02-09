function mbf_growdamp_plot_summary(poly_data, frequency_shifts, varargin)
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
%       outputs (str): 'passive' 'active', or 'both' Determines which traces are
%                      included in the graphs
%
% Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts, 'passive')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'poly_data');
addRequired(p, 'frequency_shifts');
addParameter(p, 'outputs', 'passive', valid_string);
parse(p, mbf_axis, tune, varargin{:});
% Getting the desired system setup parameters.
harmonic_number = size(frequency_shifts, 1);

x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
passive_data = -squeeze(poly_data(:,2,1));
active_data = -squeeze(poly_data(:,3,1));
passive_errors = NaN(length(passive_data),1);
passive_errors(isnan(passive_data)) = 0;
active_errors = NaN(length(active_data),1);
active_errors(isnan(active_data)) = 0;

figure
ax1 = subplot(3,1,1:2);
hold on
if strcmpi(outputs, 'passive') || strcmpi(outputs, 'both')
    plot(x_plt_axis, circshift(passive_data, -harmonic_number/2, 1), 'b', 'DisplayName', 'Passive')
    go1 = plot(x_plt_axis, circshift(passive_errors, -harmonic_number/2, 1), 'c*');
    go1.Annotation.LegendInformation.IconDisplayStyle = 'off';
end %if
if strcmpi(outputs, 'active') || strcmpi(outputs, 'both')
    plot(x_plt_axis, circshift(active_data, -harmonic_number/2, 1), 'g', 'DisplayName', 'Active')
    go2 = plot(x_plt_axis, circshift(active_errors, -harmonic_number/2, 1), 'm*');
    go2.Annotation.LegendInformation.IconDisplayStyle = 'off';
end %if
go3 = plot(x_plt_axis, zeros(length(x_plt_axis),1), 'r:');
go3.Annotation.LegendInformation.IconDisplayStyle = 'off';
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
title('MBF growdamp results')
xlabel('Mode')
ylabel('Damping rates (1/turns)')
legend
grid on

ax2 = subplot(3,1,3);
    hold on
if strcmpi(outputs, 'passive') || strcmpi(outputs, 'both')
    plot(x_plt_axis, circshift(frequency_shifts(:,1), -harmonic_number/2, 1), 'b', 'DisplayName', 'Passive')
end %if
if strcmpi(outputs, 'active') || strcmpi(outputs, 'both')
    plot(x_plt_axis, circshift(frequency_shifts(:,2), -harmonic_number/2, 1), 'g', 'DisplayName', 'Active')
end %if
    hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
xlabel('Mode')
ylabel({'Difference from';'excitation tune'})
legend
grid on

linkaxes([ax1, ax2], 'x')