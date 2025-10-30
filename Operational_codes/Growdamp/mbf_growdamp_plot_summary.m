function mbf_growdamp_plot_summary(data,  metadata, varargin)
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
%       axis: 'x', 'y' or 's'
%       plot_mode: 'pos' or 'neg'. Determines if plot modes 0:harmonic_number or
%       -harmonic_number/2:harmonic_number/2
%
% Example: mbf_growdamp_plot_summary(poly_data, frequency_shifts, 'passive')

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
valid_string = @(x) ischar(x);
addRequired(p, 'data');
addRequired(p, 'metadata');
addParameter(p, 'plot_mode', 'pos', valid_string);
parse(p, data, metadata, varargin{:});

% Getting the desired system setup parameters.


stages = fieldnames(data);
harmonic_number = length(data.(stages{1}));

%% Adjust the horizontal axis setup
if strcmpi(p.Results.plot_mode, 'pos')
    x_plt_axis = 0:harmonic_number-1;
    labelX = 'Mode';
elseif strcmpi(p.Results.plot_mode, 'neg')
    x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
    labelX = 'Mode';
    for nse = 1:length(stages)
        data.(stages{nse}) = circshift(data.(stages{nse}), -harmonic_number/2, 1);
    end %for
elseif strcmpi(p.Results.plot_mode, 'freq')
    x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
    x_plt_axis = x_plt_axis * metadata.RF / harmonic_number * 1E-6;
    labelX = 'Frequency (MHz)';
    for nse = 1:length(stages)
        data.(stages{nse}) = circshift(data.(stages{nse}), -harmonic_number/2, 1);
    end %for
end %if

%% Calculate the relative frequency shifts between stages.
ck = 1;
for wnf = 1:length(stages)
    for ntd = 1:length(stages)
        if wnf ~= ntd
            freq_diffs(ck,:) = data.(stages{wnf}).frequency_shifts - ...
                data.(stages{ntd}).frequency_shifts;
            freq_diff_names{ck} = [stages{wnf}, ' - ', stages{ntd}];
            ck = ck +1;
        end %if
    end %for
end %for

%% Plotting
figure('Position', [20, 40, 800, 800])
t = tiledlayout(3, 1);
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel(t, labelX)
ax1 = nexttile;
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).error, 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Error')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
ax2 = nexttile([2,1]);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).damping_rate, 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Damping rates (1/turns)')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
linkaxes([ax1, ax2], 'x')

figure('Position', [20, 40, 800, 800])
t = tiledlayout(1, 1);
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel(t, labelX)
nexttile;
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).frequency_shift, 'DisplayName', stages{ns})
    end %if
end %for
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
ylabel({'Difference from';'excitation tune'})
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])

figure('Position', [20, 40, 800, 800])
t = tiledlayout(3, 1);
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel(t, labelX)
ax1 = nexttile;
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).error, 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Error')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
ax2 = nexttile([2,1]);
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).damping_rate, 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Growth rates (1/turns)')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
linkaxes([ax1, ax2], 'x')

figure('Position', [20, 40, 800, 800])
t = tiledlayout(1, 1);
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel(t, labelX)
nexttile;
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.(stages{ns}).frequency_shift, 'DisplayName', stages{ns})
    end %if
end %for
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
ylabel({'Difference from';'excitation tune'})
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])

figure('Position', [20, 40, 800, 800])
t = tiledlayout(1, 1);
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
xlabel(t, labelX)
nexttile;
hold on
for ns = 1:length(freq_diff_names)
    plot(x_plt_axis, squeeze(freq_diffs(ns,:)), 'DisplayName', freq_diff_names{ns})
end %for
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
ylabel({'Difference between';'experiment stages'})
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])


