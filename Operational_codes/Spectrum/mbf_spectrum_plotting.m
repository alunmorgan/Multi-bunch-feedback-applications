function mbf_spectrum_plotting(data, meta_data)
% Plots the data saved and analysed by the earlier mbf_spectrum functions.
% Args:
%         data(structure): analysed data.
%
% Example: mbf_spectrum_plotting(data)

if max(max(data.bunch_f_data)) ==0
    disp('No data to plot')
    return
end %if

signal_per_bunch = sum(data.bunch_f_data,2);
frequency_all_bunches = sum(data.bunch_f_data,1);
graph_handles(1) = figure;
graph_handles(1).Position(3:4) = [800, 650];
ax1 = subplot('position',[.06 .32 .7 .6]);
imagesc('Xdata', data.bunch_f_scale * 1E-3,...
    'Ydata', 1:length(data.bunch_f_bunches),...
    'Cdata', data.bunch_f_data,...
     [-3 0]+max(max(data.bunch_f_data)));
set(ax1,'YAxisLocation','right');
set(ax1,'YDir','normal')
set(ax1, 'XTick', [])
set(ax1, 'YTick', [])
axis tight
title({['MBF spectrum results ', meta_data.axis,' axis ', datestr(meta_data.time)];...
    ['Current: ', num2str(round(meta_data.current)), 'mA']})

% bunches graph
ax2 = subplot('position',[.76 .32 .12 .6]);
plot(signal_per_bunch, 1:length(data.bunch_f_bunches))
set(ax2,'YAxisLocation','right');
set(ax2,'XAxisLocation','top')
set(ax2, 'XTick', [])
ylabel('Bunch number')
grid on
axis tight

% Frequency graph
ax3 = subplot('position',[.06 .12 .7 .20]);
plot(data.bunch_f_scale*1E-3 ,frequency_all_bunches);
xlabel('Frequency (KHz)')
grid on
xlim([min(data.bunch_f_scale*1E-3) max(data.bunch_f_scale*1E-3)])
ylim([0 max(frequency_all_bunches)])

% Tune graph
subplot('position',[.06 .05 .7 .001]);
plot(data.bunch_tune_scale ,frequency_all_bunches);
xlabel('Tune')

 linkaxes([ax1, ax3], 'x')
 linkaxes([ax1, ax2], 'y')
