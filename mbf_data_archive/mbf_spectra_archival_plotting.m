function mbf_spectra_archival_plotting(requested_data, spec_data, times, experimental_setup)
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
graph_title = 'Spectra';
mbf_archival_plotting_setup(requested_data, times, experimental_setup);

harmonic_number = requested_data{1}.harmonic_number;
x_plt_axis = 1:harmonic_number;
this_year = year(datetime("now"));

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {[graph_title, ' as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

ax1 = axes('OuterPosition', [0.12 0.7 0.95 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    scale_length = size(spec_data.bunch_tune_scale,2);
    for nfd = 1:size(spec_data.bunch_tune_scale,1)
        plot_data_tune = squeeze(mean(spec_data.bunch_f_data(nfd,:,:),2));
        plot(spec_data.bunch_tune_scale(nfd,scale_length/2+1:end), plot_data_tune(scale_length/2+1:end))
    end %for
    legend(graph_labels)
else
    populate_archive_graph(spec_data.tune_data, years_input, times, x_plt_axis)
end %if
title(graph_title)
xlabel('Tune')
ylabel('Magnitude')
legend show
grid on
hold off
axis tight

ax2 = axes('OuterPosition', [0.12 0.4 0.95 0.3]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    for nfd = 1:size(spec_data.bunch_f_scale,1)
        plot_data_f = squeeze(mean(spec_data.bunch_f_data(nfd,:,:),2));
        plot(spec_data.bunch_f_scale(nfd,scale_length/2+1:end) * 1E-3, plot_data_f(scale_length/2+1:end))
    end %for
    legend(graph_labels)

else
    populate_archive_graph(spec_data.tune_data, years_input, times, x_plt_axis)
end %if
xlabel('Frequency (kHz)')
ylabel('Magnitude (Power)')
legend show
grid on
hold off
axis tight

ax3 =axes('OuterPosition', [0.12 0 0.95 0.4]);
bunches = size(spec_data.bunch_f_data,2);
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot_data_2d = squeeze(sum(spec_data.bunch_f_data(1,:,:),1));
    imagesc(squeeze(spec_data.bunch_f_scale(1,scale_length/2+1:end)) * 1E-3, 1:bunches, plot_data_2d(:,scale_length/2+1:end)) % TEMP FIXME
else
    populate_archive_graph(spec_data.bunch_data, years_input, times, x_plt_axis)
end %if
xlabel('Frequency (kHz)')
ylabel('Bunch')
axis tight

linkaxes([ax2, ax3],'x')
