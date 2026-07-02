function mbf_frontend_gain_scan_archival_plotting(requested_data, adc_mean, adc_max, adc_min, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      adc_mean (numeric matrix): 
%      adc_max (numeric matrix): 
%      adc_min (numeric matrix): 
%      times (numeric vector): Datetimes of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
% Example: mbf_frontend_gain_scan_archival_plotting(requested_data, data_magnitude, data_phase, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if
graph_title = 'Frontend gain scan';
mbf_archival_plotting_setup(requested_data, times, experimental_setup);

x_plt_axis = requested_data{1}.gain;
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
    plot(x_plt_axis, adc_mean)
%     legend(graph_labels)
    hold off
else
    populate_archive_graph(adc_mean', years_input, times, x_plt_axis)
    legend('off')
end %if
title('ADC min')
xlabel('Gain')
ylabel('Magnitude')
ymin = min([min(min(adc_mean,[],2)),min(min(adc_max,[],2)),min(min(adc_min,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(adc_mean, [],2)), max(max(adc_max, [],2)), max(max(adc_min, [],2))]);
ylim([ymin ymax]);
grid on


ax2 = axes('OuterPosition', [0.42 0.5 0.3 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, adc_max)
%     legend(graph_labels)
else
       populate_archive_graph(adc_max', years_input, times, x_plt_axis)
       legend('off')
end %if
title({graph_title, 'excited bunch'} )
xlabel('Gain')
ylabel('Magnitude')
ymin = min([min(min(adc_mean,[],2)),min(min(adc_max,[],2)),min(min(adc_min,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(adc_mean, [],2)), max(max(adc_max, [],2)), max(max(adc_min, [],2))]);
ylim([ymin ymax]);
grid on
hold off

ax3 = axes('OuterPosition', [0.72 0.5 0.3 0.5]);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, adc_min)
%     legend(graph_labels)
else
          populate_archive_graph(adc_min', years_input, times, x_plt_axis)
          legend('off')
end %if
title('ADC max')
xlabel('Gain')
ylabel('Magnitude')
ymin = min([min(min(adc_mean,[],2)),min(min(adc_max,[],2)),min(min(adc_min,[],2))]);
if ymin > 0
    ymin = 0;
end %if
ymax = max([max(max(adc_mean, [],2)), max(max(adc_max, [],2)), max(max(adc_min, [],2))]);
ylim([ymin ymax]);
grid on

linkaxes([ax1,ax2, ax3],'x')