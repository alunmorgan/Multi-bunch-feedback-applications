function mbf_modescan_archival_plotting(requested_data, data_magnitude, data_phase, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      data_magnitude (numeric matrix): 
%      data_phase (numeric matrix): 
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
graph_title = 'Modescan';
mbf_archival_plotting_setup(requested_data, times, experimental_setup);

harmonic_number = requested_data{1}.harmonic_number;
x_plt_axis = 1:harmonic_number;
this_year = year(datetime("now"));

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Modescan as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

ax1 = axes('OuterPosition', [0.12 0.5 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, data_magnitude)
    legend(graph_labels)
else
    populate_archive_graph(data_magnitude', years_input, times, x_plt_axis)
end %if
title(graph_title)
xlabel('Mode')
ylabel('Magnitude')
legend show
ymin = min(min(data_magnitude,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(data_magnitude, [],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off

ax2 =axes('OuterPosition', [0.12 0 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, data_phase)
    legend(graph_labels)
else
    populate_archive_graph(data_phase', years_input, times, x_plt_axis)
end %if
title(graph_title)
xlabel('Mode')
ylabel('Phase')
ymin = min(min(data_phase,[],2));
ymax = max(max(data_phase,[],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off

linkaxes([ax1,ax2],'x')