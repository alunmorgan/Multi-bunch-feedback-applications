function mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)



[~, harmonic_number, ~] = mbf_system_config;
graph_text{1} = 'Selection criteria';
for hea = 1:length (selections)
    graph_text{hea+1} = [selections{hea,1}, ' within ', num2str(selections{hea,2})];
end %for

graph_title = 'Damping rates for different modes';

if strcmp(setup.anal_type, 'parameter_sweep')
    graph_title = {'Damping rates for different modes';...
        ['as a function of', setup.sweep_parameter];...
        ['Using a step size of ', num2str(setup.parameter_step_size)]};
end %if


x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
error_av = nonanmean(error_passive,2);
wanted = find(abs(error_av) < 0.02);

years_input = {2013, 'r'; 2014, 'b'; 2015, 'k'; 2016, 'g'; 2017, 'c'; 2018, 'm'};

figure
ax1 = subplot(2,1,1);
populate_graph(dr_passive(wanted,:), years_input, times, x_plt_axis)
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:')
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');
annotation('textbox', [0 0.1 0.3 0.3], 'String', extents, 'FitBoxToText', 'on', 'Interpreter', 'none');
title(graph_title)
xlabel('Mode')
ylabel('Passive damping rates (1/turns)')
legend show

ax2 = subplot(2,1,2);
populate_graph(dr_active(wanted,:), years_input, times, x_plt_axis)
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:')
title(graph_title)
xlabel('Mode')
ylabel('Active damping rates (1/turns)')


% add labels if it is a parameter sweep.
if nargin == 4 && strcmp(setup.anal_type, 'parameter_sweep')
    for tb = length(setup.param):-1:1
        labels{tb} = num2str(setup.param(tb));
    end %for
    legend(labels)
end %if

linkaxes([ax1,ax2],'x')


figure
ax3 = subplot(2,1,1);
populate_graph(error_passive(wanted,:), years_input, times, x_plt_axis)
title('Passive damping rate errors')
xlabel('Mode')
ylabel('Passive damping rate errors')
ax4 = subplot(2,1,2);
populate_graph(error_active(wanted,:), years_input, times, x_plt_axis)
title('Active damping rate errors')
xlabel('Mode')
ylabel('Active damping rate errors')

linkaxes([ax3,ax4],'x')

function populate_graph(input_data, years_input, times, x_plt_axis)
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
        gh = plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'DisplayName', num2str(sample_year));
        states(years_ind) = 1;
    else
        plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'HandleVisibility', 'off')
    end %if
end %for
xlim([x_plt_axis(1) x_plt_axis(end)])
ylim([y_min y_max])
legend('show')