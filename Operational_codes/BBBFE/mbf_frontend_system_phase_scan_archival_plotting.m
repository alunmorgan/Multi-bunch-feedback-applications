function mbf_frontend_system_phase_scan_archival_plotting(requested_data, leading, excited, following, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      leading (numeric matrix): 
%      excited (numeric matrix): 
%      following (numeric matrix): 
%      times (numeric vector): Datetimes of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors.
%
% Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude, data_phase, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if
graph_title = 'Frontend system phase scan';
p = mbf_archival_plotting_setup(requested_data, times, experimental_setup);

x_plt_axis = requested_data{1}.phase;
this_year = year(datetime("now"));

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Frontend system phase as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

t = tiledlayout(p, 3, 3,'TileSpacing','compact', 'Padding', 'tight');
title(t, graph_title)
xlabel(t, 'Phase (degrees)')
ax1 = nexttile(t, 1);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    hold on
    plot(x_plt_axis, leading)
%     legend(graph_labels)
    hold off
else
    populate_archive_graph(leading', years_input, times, x_plt_axis)
    legend('off')
end %if
title('leading bunch')
ylabel('Magnitude')
ymin = min([min(min(leading,[],2)),min(min(excited,[],2)),min(min(following,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(leading, [],2)), max(max(excited, [],2)), max(max(following, [],2))]);
ylim([ymin ymax]);
grid on


ax2 = nexttile(t, 2);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, excited)
%     legend(graph_labels)
else
       populate_archive_graph(excited', years_input, times, x_plt_axis)
       legend('off')
end %if
title('excited bunch')
ylabel('Magnitude')
ymin = min([min(min(leading,[],2)),min(min(excited,[],2)),min(min(following,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(leading, [],2)), max(max(excited, [],2)), max(max(following, [],2))]);
ylim([ymin ymax]);
grid on
hold off

ax3 = nexttile(t, 3);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, following)
%     legend(graph_labels)
else
          populate_archive_graph(following', years_input, times, x_plt_axis)
          legend('off')
end %if
title('following bunch')
ylabel('Magnitude')
ymin = min([min(min(leading,[],2)),min(min(excited,[],2)),min(min(following,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(leading, [],2)), max(max(excited, [],2)), max(max(following, [],2))]);
ylim([ymin ymax]);
grid on

diff1 = excited - leading;
diff2 = excited - following;
ax4 = nexttile(t, 4);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, diff1)
%     legend(graph_labels)
else
    populate_archive_graph(diff1', years_input, times, x_plt_axis)
    legend('off')
end %if
title({'difference between'; 'excited and leading bunches'})
ylabel('Signal differences')
ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on

ax5 = nexttile(t, 5);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, diff2)
    leg = legend(graph_labels, 'Location','eastoutside');
else
        populate_archive_graph(diff2', years_input, times, x_plt_axis)
        leg = legend('Location','eastoutside');
end %if
leg.Layout.Tile = 'east';
title({'difference between'; 'excited and following bunches'})
ylabel('Signal differences')
ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on

ax7 = nexttile(t, 7);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
%     plot(x_plt_axis, diff1)
else
%     populate_archive_graph(diff1', years_input, times, x_plt_axis)
    legend('off')
end %if
title('ADC amplitude')
ylabel('Signal differences')
% ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
% ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
% ymax = ymax + ymax /10;
% ylim([ymin ymax]);
grid on

ax8 = nexttile(t, 8);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
%     plot(x_plt_axis, diff1)
else
%     populate_archive_graph(diff1', years_input, times, x_plt_axis)
    legend('off')
end %if
title('ADC phase')
ylabel('Signal differences')
% ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
% ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
% ymax = ymax + ymax /10;
% ylim([ymin ymax]);
grid on


linkaxes([ax1,ax2, ax3, ax4, ax5],'x')