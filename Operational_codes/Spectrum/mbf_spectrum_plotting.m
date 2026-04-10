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

graph_handle = figure;
graph_handle.Position(3:4) = [1500, 1600];
t = tiledlayout(2,2);
t.TileSpacing = 'compact';
t.Padding = 'compact';
title(t, {['MBF spectrum results ',requested_data.ax_label, ' axis ', datestr(requested_data.time)];...
    ['Current: ', num2str(round(requested_data.current)), 'mA']})
ck = 0;

signal_per_bunch = sum(squeeze(analysed_data.bunch_f_data),2);
frequency_all_bunches = sum(squeeze(analysed_data.bunch_f_data),1);
ck = ck +1;
ax(ck) = nexttile;
imagesc('Xdata', squeeze(analysed_data.bunch_f_scale) .* 1E-3,...
    'Ydata', 1:length(squeeze(analysed_data.bunch_f_bunches)),...
    'Cdata', squeeze(analysed_data.bunch_f_data),...
    [-3 0]+max(max(squeeze(analysed_data.bunch_f_data))));
colorbar('westoutside')
set(ax(ck),'YAxisLocation','right');
set(ax(ck),'YDir','normal')
set(ax(ck), 'XTick', [])
set(ax(ck), 'YTick', [])
axis tight
% title(axis_label)

% bunches graph
ck = ck +1;
ax(ck) = nexttile;
plot(signal_per_bunch, 1:length(squeeze(analysed_data.bunch_f_bunches)))
set(ax(ck),'YAxisLocation','right');
set(ax(ck),'XAxisLocation','top')
set(ax(ck), 'XTick', [])
ylabel('Bunch number')
grid on
axis tight

% Frequency graph
ck = ck +1;
ax(ck) = nexttile;
plot(squeeze(analysed_data.bunch_f_scale).* 1E-3 ,frequency_all_bunches);
xlabel('Frequency (KHz)')
grid on
xlim([min(squeeze(analysed_data.bunch_f_scale) .* 1E-3)...
    max(squeeze(analysed_data.bunch_f_scale) .* 1E-3)])
ylim([0 max(frequency_all_bunches)])

% Tune graph
ck = ck +1;
ax(ck) = nexttile;
plot(squeeze(analysed_data.bunch_tune_scale) ,frequency_all_bunches);
lims = ylim;
hold on
plot([requested_data.tune.x_tune.tune requested_data.tune.x_tune.tune],[0 lims(2)] ,':r')
plot([requested_data.tune.y_tune.tune requested_data.tune.y_tune.tune],[0 lims(2)]  ,':c')
plot([requested_data.tune.s_tune.tune requested_data.tune.s_tune.tune],[0 lims(2)]  ,':g')
xlabel('Tune')
hold off
grid on

linkaxes([ax(1), ax(3)], 'x')
linkaxes([ax(1), ax(2)], 'y')

