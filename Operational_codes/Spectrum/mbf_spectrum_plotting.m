function mbf_spectrum_plotting(all_data, current, timestamp)
% Plots the data saved and analysed by the earlier mbf_spectrum functions.
% Args:
%         all_data(structure): analysed data.
%
% Example: mbf_spectrum_plotting(data)
data_names =fieldnames(all_data);% {'x_axis', 'y_axis', 's_axis'};
graph_handle = figure;
graph_handle.Position(3:4) = [1500, 1600];
t = tiledlayout(3,4);
t.TileSpacing = 'compact';
t.Padding = 'compact';
title(t, {['MBF spectrum results ', datestr(timestamp)];...
        ['Current: ', num2str(round(current)), 'mA']})
ck = 0;
for mne = 1:length(data_names)
    data = all_data.(data_names{mne});
    axis_label = data_names{mne};

    if max(max(data.bunch_f_data)) ==0
        disp('No data to plot')
        continue
    end %if

    signal_per_bunch = sum(data.bunch_f_data,2);
    frequency_all_bunches = sum(data.bunch_f_data,1);
    ck = ck +1;
    ax(ck) = nexttile;
    imagesc('Xdata', data.bunch_f_scale * 1E-3,...
        'Ydata', 1:length(data.bunch_f_bunches),...
        'Cdata', data.bunch_f_data,...
        [-3 0]+max(max(data.bunch_f_data)));
    set(ax(ck),'YAxisLocation','right');
    set(ax(ck),'YDir','normal')
    set(ax(ck), 'XTick', [])
    set(ax(ck), 'YTick', [])
    axis tight
    title(axis_label)

    % bunches graph
    ck = ck +1;
    ax(ck) = nexttile;
    plot(signal_per_bunch, 1:length(data.bunch_f_bunches))
    set(ax(ck),'YAxisLocation','right');
    set(ax(ck),'XAxisLocation','top')
    set(ax(ck), 'XTick', [])
    ylabel('Bunch number')
    grid on
    axis tight

    % Frequency graph
    ck = ck +1;
    ax(ck) = nexttile;
    plot(data.bunch_f_scale*1E-3 ,frequency_all_bunches);
    xlabel('Frequency (KHz)')
    grid on
    xlim([min(data.bunch_f_scale*1E-3) max(data.bunch_f_scale*1E-3)])
    ylim([0 max(frequency_all_bunches)])

    % Tune graph
    ck = ck +1;
    ax(ck) = nexttile;
    plot(data.bunch_tune_scale ,frequency_all_bunches);
    xlabel('Tune')
end %for

linkaxes([ax(1), ax(3), ax(5), ax(7), ax(9), ax(11)], 'x')
linkaxes([ax(1), ax(2)], 'y')
linkaxes([ax(5), ax(6)], 'y')
linkaxes([ax(9), ax(10)], 'y')
