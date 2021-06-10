function mbf_spectrum_plotting(data, meta_data)
% Plots the data saved and analysed by the earlier mbf_spectrum functions.
% Args:
%         data(structure): analysed data.
%
% Example: mbf_spectrum_plotting(data)

graph_handles(1) = figure;
ax1 = subplot('position',[.02 .35 .7 .6]);
imagesc(data.bunch_axis,...
    data.tune_axis,...
    log10(data.bunch_data),...
    [-3 0]+log10(max(max(data.bunch_data))));
set(ax1,'YAxisLocation','right');
set(ax1,'YDir','normal')
set(ax1, 'XTick', [])
set(ax1, 'YTick', [])
title(meta_data.axis)

% Frequencies graph
ax2 = subplot('position',[.72 .35 .18 .6]);
plot(data.bunch_tune ,data.tune_axis);
set(ax2,'YAxisLocation','right');
set(ax2,'XAxisLocation','top')
set(ax2, 'XTick', [])
ylabel('Fractional tune')
axis tight

% bunches graph
[~,pi] = max(data.mode_tune);
ax3 = subplot('position',[.02 .11 .7 .24]);
plot(data.bunch_data(pi,:))
xlabel(sprintf('Bunches at peak tune %3.3f',data.tune_axis(pi)))
set(ax3, 'YTick', [])
axis tight

linkaxes([ax1, ax3], 'x')
linkaxes([ax1, ax2], 'y')

graph_handles(2) = figure;
ax4 = subplot('position',[.02 .35 .7 .6]);
imagesc(data.mode_axis,...
    data.tune_axis,...
    log10(data.tune_data(1:end/2,:)),...
    [-3 0]+log10(max(max(data.tune_data(1:end/2,:)))));
set(ax4,'YAxisLocation','right');
set(ax4,'YDir','normal')
set(ax4, 'XTick', [])
set(ax4, 'YTick', [])

ax5 = subplot('position',[.72 .35 .18 .6]);
plot(data.mode_tune,data.tune_axis);
set(gca,'YAxisLocation','right');
set(gca,'XAxisLocation','top')
set(ax5, 'XTick', [])
ylabel('Fractional tune')
axis tight

ax6 = subplot('position',[.02 .11 .7 .24]);
plot(data.mode_axis.',data.tune_data(pi,:))
xlabel(sprintf('Modes at peak tune %3.3f',data.tune_axis(pi)))
set(ax6, 'YTick', [])
axis tight

linkaxes([ax4, ax6], 'x')
linkaxes([ax4, ax5], 'y')

[root_string, ~, ~, ~] = mbf_system_config;
archive_graphs(root_string, meta_data, graph_handles)
