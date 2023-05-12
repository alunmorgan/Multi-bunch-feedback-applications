function mbf_modescan_archival_plotting(requested_data, data_magnitude, data_phase, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      data_magnitude (numeric matrix): 
%      data_phase (numeric matrix): 
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
harmonic_number = requested_data{1}.harmonic_number;
x_plt_axis = 1:harmonic_number;
this_year = year(datetime("now"));
ranges_to_display = {'RF', 'time','current'};

extents = growdamp_archive_calculate_extents(requested_data);

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

graph_text{1} = ['Analysis type: ', experimental_setup.anal_type];
graph_text_2 = cell(1, 2 * length(ranges_to_display) + 1);
graph_text_2{1} = 'Data ranges';
for whe = 1:2:length(ranges_to_display)
    graph_text_2{whe + 1} = ranges_to_display{whe};
    graph_text_2{whe + 2} = [num2str(extents.(ranges_to_display{whe}){1}), ' to ', num2str(extents.(ranges_to_display{whe}){2})];
end %for

graph_title = 'Modescan';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Modescan as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

figure('Position',[50, 50, 1400, 800])
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');
annotation('textbox', [0 0.1 0.3 0.3], 'String', graph_text_2, 'FitBoxToText', 'on', 'Interpreter', 'none');

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

axfp = axes('OuterPosition', [0 0.45 0.2 0.3]);
    hold on
for hkw = 1:length(requested_data)
    plot(1:harmonic_number, requested_data{hkw}.fill_pattern, 'b')
end %for
ylim([0 inf])
xlim([1 936])
set(axfp, 'XTick', [])
title('Fill pattern variation')
ylabel('Charge (nC)')

% add labels if it is a parameter sweep.
if nargin == 4 && strcmp(experimental_setup.anal_type, 'parameter_sweep')
    for tb = length(experimental_setup.param):-1:1
        labels{tb} = num2str(experimental_setup.param(tb));
    end %for
    legend(labels)
end %if

linkaxes([ax1,ax2],'x')

figure
plot(times, zeros(length(times),1), 'o:')
xlabel('Time')
datetick
for hrd = 1:length(ranges_to_display)
    if strcmp(ranges_to_display{hrd}, 'time')
        continue
    else
        data_temp = NaN(length(times),1);
        for hse = 1:length(times)
            data_temp(hse) = requested_data{hse}.(ranges_to_display{hrd});
        end %for
        figure
        plot(times, data_temp, 'o:')
        xlabel('Time')
        datetick
        title(ranges_to_display{hrd})
        clear data_temp
    end %if
end %for