function mbf_growdamp_plot_summary(poly_data, frequency_shifts, metadata, varargin)
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
%       metadata (structure): setup information.
%       outputs (str): 'passive' 'active', or 'both' Determines which traces are
%                      included in the graphs
%       axis: 'x', 'y' or 's'
%       plot_mode: 'pos' or 'neg'. Determines if plot modes 0:936 or
%       -468:468
%
% Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts, 'passive')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'poly_data');
addRequired(p, 'frequency_shifts');
addParameter(p, 'outputs', 'passive', valid_string);
addParameter(p, 'plot_mode', 'pos', valid_string);
parse(p, poly_data, frequency_shifts, varargin{:});

% Getting the desired system setup parameters.
harmonic_number = size(frequency_shifts, 1);

passive_data = -squeeze(poly_data(:,2,1));
active_data = -squeeze(poly_data(:,3,1));

if strcmpi(p.Results.plot_mode, 'pos')
    x_plt_axis = 0:harmonic_number-1;
    passive_frequency_shifts = frequency_shifts(:,1);
    active_frequency_shifts = frequency_shifts(:,2);
    
elseif strcmpi(p.Results.plot_mode, 'neg')
    x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
    passive_data = circshift(passive_data, -harmonic_number/2, 1);
    active_data = circshift(active_data, -harmonic_number/2, 1);
    passive_frequency_shifts = circshift(frequency_shifts(:,1), -harmonic_number/2, 1);
    active_frequency_shifts = circshift(frequency_shifts(:,2), -harmonic_number/2, 1);
    
end

figure('Position', [20, 40, 600, 600])
ax1 = subplot(3,1,1:2);
hold on
if strcmpi(p.Results.outputs, 'passive') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, passive_data, 'b', 'DisplayName', 'Passive')
end %if
if strcmpi(p.Results.outputs, 'active') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, active_data, 'g', 'DisplayName', 'Active')
end %if

hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
title({['MBF growdamp results (', metadata.ax_label,' ', datestr(metadata.time),')'];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel('Mode')
ylabel('Damping rates (1/turns)')
legend
grid on

ax2 = subplot(3,1,3);
    hold on
if strcmpi(p.Results.outputs, 'passive') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, passive_frequency_shifts, 'b', 'DisplayName', 'Passive')
end %if
if strcmpi(p.Results.outputs, 'active') || strcmpi(p.Results.outputs, 'both')
    plot(x_plt_axis, active_frequency_shifts, 'g', 'DisplayName', 'Active')
end %if
    hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
xlabel('Mode')
ylabel({'Difference from';'excitation tune'})
legend
grid on

linkaxes([ax1, ax2], 'x')