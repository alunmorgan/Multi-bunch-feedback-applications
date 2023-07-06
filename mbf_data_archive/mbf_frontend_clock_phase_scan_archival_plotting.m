function mbf_frontend_clock_phase_scan_archival_plotting(requested_data, leading, excited, following, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      leading (numeric matrix): 
%      excited (numeric matrix): 
%      following (numeric matrix): 
%      times (numeric vector): Datenums of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors.
%
% Example: mbf_growdamp_archival_plotting(requested_data, data_magnitude, data_phase, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if
graph_title = 'Frontend clock phase scan';
mbf_archival_plotting_setup(requested_data, times, experimental_setup);

x_plt_axis = requested_data{1}.phase;
this_year = year(datetime("now"));

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Frontend clock phase as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

ax1 = axes('OuterPosition', [0.12 0.5 0.3 0.5]);
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
xlabel('Phase')
ylabel('Magnitude')
ymin = min([min(min(leading,[],2)),min(min(excited,[],2)),min(min(following,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(leading, [],2)), max(max(excited, [],2)), max(max(following, [],2))]);
ylim([ymin ymax]);
grid on


ax2 = axes('OuterPosition', [0.42 0.5 0.3 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, excited)
%     legend(graph_labels)
else
       populate_archive_graph(excited', years_input, times, x_plt_axis)
       legend('off')
end %if
title({graph_title, 'excited bunch'} )
xlabel('Phase')
ylabel('Magnitude')
ymin = min([min(min(leading,[],2)),min(min(excited,[],2)),min(min(following,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(leading, [],2)), max(max(excited, [],2)), max(max(following, [],2))]);
ylim([ymin ymax]);
grid on
hold off

ax3 = axes('OuterPosition', [0.72 0.5 0.3 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, following)
%     legend(graph_labels)
else
          populate_archive_graph(following', years_input, times, x_plt_axis)
          legend('off')
end %if
title('following bunch')
xlabel('Phase')
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
ax4 =axes('OuterPosition', [0.12 0 0.3 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, diff1)
%     legend(graph_labels)
else
    populate_archive_graph(diff1', years_input, times, x_plt_axis)
    legend('off')
end %if
title('excited - leading')
xlabel('Phase')
ylabel('Signal differences')
ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on

ax5 =axes('OuterPosition', [0.42 0 0.5 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, diff2)
    legend(graph_labels, 'Location','eastoutside')
else
        populate_archive_graph(diff2', years_input, times, x_plt_axis)
         legend('Location','eastoutside')
end %if
title('excited - following')
xlabel('Phase')
ylabel('Signal differences')
ymin = min([min(min(diff1,[],2)),min(min(diff2,[],2))]);
ymax = max([max(max(diff1,[],2)),max(max(diff1,[],2))]);
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on

linkaxes([ax1,ax2, ax3, ax4, ax5],'x')