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
harmonic_number = length(data.(stages{1}).damping_rate);

%% Adjust the horizontal axis setup
if strcmpi(p.Results.plot_mode, 'pos')
    x_plt_axis = 0:harmonic_number-1;
    labelX = 'Mode';
    for nse = 1:length(stages)
        data.modes.(stages{nse}) = data.(stages{nse});
    end %for
elseif strcmpi(p.Results.plot_mode, 'neg')
    x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
    labelX = 'Mode';
    for nse = 1:length(stages)
        data.modes.(stages{nse}) = circshift(data.(stages{nse}), -harmonic_number/2, 1);
    end %for
end %if

%% Calculate the relative frequency shifts between stages.
ck = 1;
for wnf = 1:length(stages)
    for ntd = 1:length(stages)
        if wnf ~= ntd
            freq_diffs(ck,:) = data.modes.(stages{wnf}).frequency_shift - ...
                data.modes.(stages{ntd}).frequency_shift;
            freq_diff_names{ck} = [stages{wnf}, ' - ', stages{ntd}];
            ck = ck +1;
        end %if
    end %for
end %for

% Convert to frequencies
for nse = 1:length(stages)
    measurements = fieldnames(data.(stages{nse}));
    for bes = 1:length(measurements)
        [x_plt_axis_f, data.f.(stages{nse}).(measurements{bes})] = mode_to_frequency(metadata.RF,...
            harmonic_number,...
            metadata.tunes.([metadata.ax_label,'_tune']).tune,...
            data.(stages{nse}).(measurements{bes}));
    end %for
end %for
x_plt_axis_f = x_plt_axis_f * 1E-6;

labelX_f = 'Frequency (MHz)';

%% Plotting
figure('Position', [20, 40, 800, 800])
t = tiledlayout(4, 3,'TileSpacing','compact', 'Padding', 'tight');
title(t, {['MBF growdamp results ', metadata.ax_label,' axis ', datestr(metadata.time)];...
    ['Current: ', num2str(round(metadata.current)), 'mA']})
% xlabel(t, labelX)

ax1 = nexttile(8);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).error(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Error')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])

ax2 = nexttile(2, [2,1]);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).damping_rate(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Damping rates (1/turns)')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
linkaxes([ax1, ax2], 'x')

ax3 =nexttile(11);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).frequency_shift(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
ylabel({'Difference from';'excitation tune'})
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
xlabel(labelX)

ax4 = nexttile(7);
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).error(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Error')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])

ax5 = nexttile(1, [2,1]);
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).damping_rate(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Growth rates (1/turns)')
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])

ax6 = nexttile(10);
hold on
for ns = 1:length(stages)
    if contains(stages{ns}, 'growth')
        plot(x_plt_axis, data.modes.(stages{ns}).frequency_shift(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
xlim([x_plt_axis(1) x_plt_axis(end)])
ylabel({'Difference from';'excitation tune'})
legend
grid on
xlim([x_plt_axis(1) x_plt_axis(end)])
xlabel(labelX)

linkaxes([ax1, ax2, ax3], 'x')
linkaxes([ax4, ax5, ax6], 'x')

ax7 = nexttile(9);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis_f, data.f.(stages{ns}).error(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Error')
legend
grid on
xlim([x_plt_axis_f(1) x_plt_axis_f(end)])

ax8 = nexttile(3, [2,1]);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis_f, data.f.(stages{ns}).damping_rate(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel('Damping rates (1/turns)')
legend
grid on
xlim([x_plt_axis_f(1) x_plt_axis_f(end)])
linkaxes([ax7, ax8], 'x')

ax9 =nexttile(12);
hold on
for ns = 1:length(stages)
    if ~contains(stages{ns}, 'growth')
        plot(x_plt_axis_f, data.f.(stages{ns}).frequency_shift(:), 'DisplayName', stages{ns})
    end %if
end %for
hold off
ylabel({'Difference from';'excitation tune'})
legend
grid on
xlim([x_plt_axis_f(1) x_plt_axis_f(end)])
xlabel(labelX_f)
