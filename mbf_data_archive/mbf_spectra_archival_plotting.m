function mbf_spectra_archival_plotting(requested_data, bunch_data, tune_data, times, experimental_setup)
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

% data.mode_modes = sum(bunch_data.^2,1);
% data.mode_tune = sum(mode_data(1:end/2,:).^2, 2);
% 
bunches = size(bunch_data,2);
bunch_tunes = size(bunch_data,3);
% 
% tune_axis = linspace(0,.5,size(tune_data,2));
% data.bunch_axis = 1:raw_data.harmonic_number;
mode_axis = -harmonic_number/2 : (harmonic_number/2 -1) ;

ax1 = axes('OuterPosition', [0.12 0.5 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(mode_axis, tune_data)
    legend(graph_labels)
else
    populate_archive_graph(tune_data, years_input, times, x_plt_axis)
end %if
title(graph_title)
xlabel('Mode?')
ylabel('Magnitude')
legend show
ymin = min(min(tune_data,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(tune_data, [],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off

if bunch_tunes > 1
ax2 =axes('OuterPosition', [0.12 0 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    [X,Y] = meshgrid(1:bunches,1:bunch_tunes);
    contour(X,Y, squeeze(bunch_data(1,:,:))) %ONLY FOR FIRST DATASET NEED A BETTER SOLUTION
    legend(graph_labels)
else
    populate_archive_graph(bunch_data, years_input, times, x_plt_axis)
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
end %if