function mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, experimental_setup, selections, extents)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      dr_passive (numeric matrix): Passive damping rate.
%                                   (bunches vs datasets)
%      dr_active (numeric matrix): Passive damping rate.
%                                   (bunches vs datasets)
%      error_passive (numeric matrix): Error of the fit for the passive
%                                      damping rate.
%      error_active (numeric matrix): Error of the fit for the active
%                                     damping rate.
%      times (numeric vector): Datenums of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%      extents (structure): Contains the max and min values of the machine operating parameters. 
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors. 
%
% Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)

% Only do somethign if there is data to do something with.
if isempty(times)
    return
end %if
if length(times) < 2
    return
end %if

[~, harmonic_number, ~, ~] = mbf_system_config;
x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
years_input = {2013, 'r'; 2014, 'b'; 2015, 'k'; 2016, 'g'; 2017, 'c'; 2018, 'm'};

graph_text{1} = 'Selection criteria';
for hea = length(selections):-1:1
    graph_text{hea+1} = [selections{hea,1}, ' within ', num2str(selections{hea,2})];
end %for

graph_text_2{1} = 'Data ranges';
for whe = size(selections, 1):-1:1
    if isnumeric(extents.(selections{whe}){1})
        if strcmp(selections{whe}, 'fill_pattern')
        graph_text_2{whe + 1} = [selections{whe}, ' : '];
        fp1 = extents.(selections{whe}){1};
        fp2 = extents.(selections{whe}){2};
        else
        graph_text_2{whe + 1} = [selections{whe}, ' : ', ...
            num2str(extents.(selections{whe}){1}), ' to ', num2str(extents.(selections{whe}){2})];
        end %if
    elseif ischar(extents.(selections{whe}){1})
        graph_text_2{whe + 1} = [selections{whe}, ' : ', extents.(selections{whe}){1}];
    elseif iscell(extents.(selections{whe}){1})
        if ischar(extents.(selections{whe}){1}{1})
         graph_text_2{whe + 1} = [selections{whe}, ' : ', extents.(selections{whe}){1}{1}];
        end %if
    end %if
end %for

graph_title = 'Damping rates for different modes';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {'Damping rates for different modes';...
        ['as a function of', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size)]};
end %if

figure
ax1 = axes('OuterPosition', [0.05 0.5 0.95 0.5]);
populate_graph(dr_passive, years_input, times, x_plt_axis)
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:')
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');
annotation('textbox', [0 0.1 0.3 0.3], 'String', graph_text_2, 'FitBoxToText', 'on', 'Interpreter', 'none');
title(graph_title)
xlabel('Mode')
ylabel('Passive damping rates (1/turns)')
legend show

ax2 =axes('OuterPosition', [0.05 0 0.95 0.5]);
populate_graph(dr_active, years_input, times, x_plt_axis)
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:')
title(graph_title)
xlabel('Mode')
ylabel('Active damping rates (1/turns)')

axfp = axes('OuterPosition', [0 0.45 0.15 0.1]);
area(fp1, 'EdgeColor', 'none');
hold on;
area(fp2, 'EdgeColor', 'None', 'FaceColor', 'w');
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

if nargin == 9
figure
ax3 = subplot(2,1,1);
populate_graph(error_passive, years_input, times, x_plt_axis)
title('Passive damping rate errors')
xlabel('Mode')
ylabel('Passive damping rate errors')
ax4 = subplot(2,1,2);
populate_graph(error_active, years_input, times, x_plt_axis)
title('Active damping rate errors')
xlabel('Mode')
ylabel('Active damping rate errors')

linkaxes([ax3,ax4],'x')
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
for ner = 1:size(input_data, 1)
    sample_year = datevec(times(ner));
    sample_year = sample_year(1);
    years_ind = find(sample_year== years);
    if states(years_ind) == 0
        plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'DisplayName', num2str(sample_year));
        states(years_ind) = 1;
    else
        plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'HandleVisibility', 'off')
    end %if
end %for
xlim([x_plt_axis(1) x_plt_axis(end)])
ylim([y_min y_max])
legend('show')