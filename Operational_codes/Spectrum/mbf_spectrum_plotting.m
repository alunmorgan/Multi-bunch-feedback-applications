function mbf_spectrum_plotting(requested_data, analysed_data)
% Plots the data saved and analysed by the earlier mbf_spectrum functions.
% Args:
%         all_data(structure): analysed data.
%
% Example: mbf_spectrum_plotting(data

if max(max(analysed_data.bunch_f_data)) ==0
    disp('No data to plot')
    return
end %if

figure('Position', [20, 40, 1200, 800])
t = tiledlayout(2,2, 'TileSpacing','compact', 'Padding', 'tight');
title(t, {['MBF spectrum results ',requested_data.ax_label, ' axis ', datestr(requested_data.time)];...
    ['Current: ', num2str(round(requested_data.current)), 'mA']})

signal_per_bunch = sum(squeeze(analysed_data.bunch_f_data),2);
frequency_all_bunches = sum(squeeze(analysed_data.bunch_f_data),1);
ax1 = nexttile;
imagesc('Xdata', squeeze(analysed_data.bunch_f_scale) .* 1E-3,...
    'Ydata', 1:length(squeeze(analysed_data.bunch_f_bunches)),...
    'Cdata', squeeze(analysed_data.bunch_f_data),...
    [-3 0]+max(max(squeeze(analysed_data.bunch_f_data))));
colorbar('westoutside')
set(ax1,'YAxisLocation','right');
set(ax1,'YDir','normal')
set(ax1, 'XTick', [])
set(ax1, 'YTick', [])
axis tight
% title(axis_label)

% bunches graph
ax2 = nexttile;
plot(signal_per_bunch, 1:length(squeeze(analysed_data.bunch_f_bunches)))
set(ax2,'YAxisLocation','right');
set(ax2,'XAxisLocation','top')
set(ax2, 'XTick', [])
ylabel('Bunch number')
grid on
axis tight

% Frequency graph
ax3 = nexttile;
plot(squeeze(analysed_data.bunch_f_scale).* 1E-3 ,frequency_all_bunches);
xlabel('Frequency (KHz)')
grid on
xlim([min(squeeze(analysed_data.bunch_f_scale) .* 1E-3)...
    max(squeeze(analysed_data.bunch_f_scale) .* 1E-3)])
ylim([0 max(frequency_all_bunches)])


% Tune graph
ax4 = nexttile;
plot(squeeze(analysed_data.bunch_tune_scale) ,frequency_all_bunches);
ylim([0 max(frequency_all_bunches)])
lims = ylim;
hold on
plot([requested_data.tunes.x_tune.tune requested_data.tunes.x_tune.tune],[0 lims(2)],...
    ':r', 'LineWidth', 2, 'DisplayName', 'Horizontal tune')
plot([requested_data.tunes.y_tune.tune requested_data.tunes.y_tune.tune],[0 lims(2)],...
    ':c', 'LineWidth', 2, 'DisplayName', 'Vertical tune')
plot([requested_data.tunes.s_tune.tune requested_data.tunes.s_tune.tune],[0 lims(2)],...
    ':g', 'LineWidth', 2, 'DisplayName', 'Longitudinal tune')
plot([-requested_data.tunes.x_tune.tune -requested_data.tunes.x_tune.tune],[0 lims(2)],...
    ':r', 'LineWidth', 2, 'DisplayName', 'Horizontal tune', 'HandleVisibility','off')
plot([-requested_data.tunes.y_tune.tune -requested_data.tunes.y_tune.tune],[0 lims(2)],...
    ':c', 'LineWidth', 2, 'DisplayName', 'Vertical tune', 'HandleVisibility','off')
plot([-requested_data.tunes.s_tune.tune -requested_data.tunes.s_tune.tune],[0 lims(2)],...
    ':g', 'LineWidth', 2, 'DisplayName', 'Longitudinal tune', 'HandleVisibility','off')
xlabel('Tune')
hold off
grid on
legend

linkaxes([ax1, ax3], 'x')
linkaxes([ax1, ax2], 'y')
linkaxes([ax3, ax4], 'y')
