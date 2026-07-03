function mbf_bunch_motion_archival_plotting(requested_data, dataset, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%       dataset (struct): containing
%      dr_passive (numeric matrix): Passive damping rate.
%                                   (bunches vs datasets)
%      dr_active (numeric matrix): Passive damping rate.
%                                   (bunches vs datasets)
%      error_passive (numeric matrix): Error of the fit for the passive
%                                      damping rate.
%      error_active (numeric matrix): Error of the fit for the active
%                                     damping rate.
%      times (numeric vector): Datetimes of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors.
%
% Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if

[~, harmonic_number, ~, ~] = mbf_system_config;
this_year = year(datetime("now"));
for jshe = 1:length(requested_data)
    requested_data{jshe}.turn_of_peak = dataset.turn_of_peak(jshe);
    requested_data{jshe}.bucket_of_peak = dataset.bucket_of_peak(jshe);
end %for
ranges_to_display = {'RF', 'current', 'turn_of_peak', 'bucket_of_peak'};

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

graph_text{1} = ['Analysis type: ', experimental_setup.anal_type];
graph_title = 'Average bunch motion';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Average bunch motion as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

figure('Position',[50, 50, 1800, 800])
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');

ax1 = axes('OuterPosition', [0.18 0.66 0.4 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_bunches_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_bunches_x, years_input, times, 1:harmonic_number)
end %if
title(graph_title)
xlabel('Bunches')
ylabel('Mean centroid motion in x')
legend off
grid on
hold off

ax2 =axes('OuterPosition', [0.18 0.33 0.4 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_bunches_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_bunches_y, years_input, times, 1:harmonic_number)
end %if
xlabel('Bunches')
ylabel('Mean centroid motion in y')
legend off
grid on
hold off

ax3 =axes('OuterPosition', [0.18 0 0.4 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_bunches_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_bunches_z, years_input, times, 1:harmonic_number)
end %if
xlabel('Bunches')
ylabel('Mean centroid motion in s')
legend off
grid on
hold off

linkaxes([ax1, ax2, ax3],'x')

graph_title = 'Average turn motion';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Average turn motion as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
end %if

ax4 = axes('OuterPosition', [0.52 0.66 0.5 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_turns_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_turns_x, years_input, times, 1:length(dataset.mean_turns_x))
end %if
title(graph_title)
xlabel('Turns')
ylabel('Mean centroid motion in x')
legend('Location','eastOutside')
grid on
hold off

ax5 =axes('OuterPosition', [0.52 0.33 0.4 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_turns_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_turns_y, years_input, times, 1:length(dataset.mean_turns_y))
end %if
xlabel('Turns')
ylabel('Mean centroid motion in y')
legend off
grid on
hold off

ax6 =axes('OuterPosition', [0.52 0 0.4 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(experimental_setup.param, dataset.mean_turns_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(dataset.mean_turns_z, years_input, times, 1:length(dataset.mean_turns_z))
end %if
xlabel('Turns')
ylabel('Mean centroid motion in s')
legend off
grid on
hold off

linkaxes([ax4, ax5, ax6],'x')

ck = 0;
n_graphs = length(ranges_to_display);
for hrd = 1:n_graphs

    axes('OuterPosition', [0.01 0.3 + ck * 0.6/n_graphs 0.2 0.6 / n_graphs]);
    xlabel('Time')
    title(ranges_to_display{hrd})
    data_temp = NaN(length(times),1);
    for hse = 1:length(times)
        data_temp(hse) = requested_data{hse}.(ranges_to_display{hrd});
    end %for
    plot(times, data_temp, 'o:')
    datetick
    ylabel(ranges_to_display{hrd})
    clear data_temp
    ck = ck +1;
end %for

axfp = axes('OuterPosition', [0.01 0 0.2 0.3]);
hold on
for hkw = 1:length(requested_data)
    plot(1:harmonic_number, requested_data{hkw}.fill_pattern, 'b')
end %for
ylim([0 inf])
xlim([1 harmonic_number])
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

function populate_graph(input_data, years_input, times, x_plt_axis)
if isempty(input_data)
    return
end %if
hold on
y_max = max(max(input_data));
y_min = min(min(input_data));
for esr = size(years_input,1):-1:1
    years(esr) = years_input{esr,1};
    states(esr) = 0;
    cols{esr} = years_input{esr,2};
end %for
sample_year_temp = datevec(times);
year_list = sample_year_temp(:,1);
if length(unique(year_list)) < 2
    for ner = 1:size(input_data, 1)
        sample_time = datevec(times(ner));
        sample_time = datestr(sample_time);
        plot(x_plt_axis, input_data(ner,:), 'DisplayName', sample_time, 'LineWidth', 2);
    end %for
else
    for ner = 1:size(input_data, 1)
        years_ind = find(year_list(ner)== years);
        if states(years_ind) == 0
            plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'DisplayName', num2str(year_list(ner)), 'LineWidth', 2);
            states(years_ind) = 1;
        else
            plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'HandleVisibility', 'off', 'LineWidth', 2)
        end %if
    end %for
end %if
xlim([x_plt_axis(1) x_plt_axis(end)])
ylim([y_min y_max])
legend('show')