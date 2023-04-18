function mbf_growdamp_plot_summary_multi_f(poly_data, frequency_shifts, list_of_tunes, varargin)
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
addRequired(p, 'list_of_tunes');
addParameter(p, 'outputs', 'passive', valid_string);
addParameter(p, 'axis', '', valid_string);
parse(p, poly_data, frequency_shifts, list_of_tunes, varargin{:});
% Getting the desired system setup parameters.
harmonic_number = size(frequency_shifts{1}, 1);

x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
for jzw = 1:length(poly_data)
passive_data(:,jzw) = -squeeze(poly_data{jzw}(:,2,1));
active_data(:,jzw) = -squeeze(poly_data{jzw}(:,3,1));
end % for
passive_errors = NaN(size(passive_data,1),size(passive_data,2));
passive_errors(isnan(passive_data)) = 0;
active_errors = NaN(size(active_data,1), size(active_data,2));
active_errors(isnan(active_data)) = 0;

figure
ribbon(x_plt_axis, passive_data)
xticks(0:length(list_of_tunes)+1)
for hs = 1:length(list_of_tunes)
    labels{hs} = num2str(list_of_tunes(hs));
end %for
xticklabels(cat(2,' ', labels, ' '))
title(['MBF growdamp results (', p.Results.axis, ')'])
xlabel('Tune')
ylabel('Mode')
zlabel('Damping rates (1/turns)')
figure
ax1 = subplot(3,1,1:2);
hold on
if strcmpi(p.Results.outputs, 'passive') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, circshift(passive_data, -harmonic_number/2, 1), 'b', 'DisplayName', 'Passive')
    go1 = plot(x_plt_axis, circshift(passive_errors, -harmonic_number/2, 1), 'c*');
%     go1.Annotation.LegendInformation.IconDisplayStyle = 'off';
end %if
if strcmpi(p.Results.outputs, 'active') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, circshift(active_data, -harmonic_number/2, 1), 'g', 'DisplayName', 'Active')
    go2 = plot(x_plt_axis, circshift(active_errors, -harmonic_number/2, 1), 'm*');
%     go2.Annotation.LegendInformation.IconDisplayStyle = 'off';
end %if
go3 = plot(x_plt_axis, zeros(length(x_plt_axis),1), 'r:');
go3.Annotation.LegendInformation.IconDisplayStyle = 'off';
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
title(['MBF growdamp results (', p.Results.axis, ')'])
xlabel('Mode')
ylabel('Damping rates (1/turns)')
legend
grid on

ax2 = subplot(3,1,3);
%     hold on
% if strcmpi(p.Results.outputs, 'passive') || strcmpi(p.Results.outputs, 'both')
%     plot(x_plt_axis, circshift(frequency_shifts(:,1), -harmonic_number/2, 1), 'b', 'DisplayName', 'Passive')
% end %if
% if strcmpi(p.Results.outputs, 'active') || strcmpi(p.Results.outputs, 'both')
%     plot(x_plt_axis, circshift(frequency_shifts(:,2), -harmonic_number/2, 1), 'g', 'DisplayName', 'Active')
% end %if
%     hold off
% xlim([x_plt_axis(1) x_plt_axis(end)])
% xlabel('Mode')
% ylabel({'Difference from';'excitation tune'})
% legend
% grid on

linkaxes([ax1, ax2], 'x')