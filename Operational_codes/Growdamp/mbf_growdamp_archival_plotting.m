function mbf_growdamp_archival_plotting(requested_data, dataset, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%       dataset (struct): containing
%      dr_passive (numeric matrix): Passive damping rate.
%                                   (bunches vs datasets)
%      dr_active (numeric matrix): Active damping rate.
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
% Example: mbf_growdamp_archival_plotting(requested_data, dataset, error_active, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Damping rates for different modes as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
else
    graph_title = 'Damping rates for different modes';
end %if
p = mbf_archival_plotting_setup(requested_data, times, experimental_setup);

[~, harmonic_number, ~, ~] = mbf_system_config;
x_plt_axis = (0:harmonic_number-1);
this_year = year(datetime("now"));

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

t1 = tiledlayout(p, 2, 2,'TileSpacing','compact', 'Padding', 'tight');
title(t1, graph_title)
xlabel(t1, 'Mode')
f_names = fieldnames(dataset);
for jse = 1:length(f_names)
    ax(jse) = nexttile(t1);
    hold on

    if strcmp(experimental_setup.anal_type, 'parameter_sweep')
        graph_labels = cell(1, length(experimental_setup.param));
        for hw = 1:length(experimental_setup.param)
            graph_labels{hw}=num2str(experimental_setup.param(hw));
        end % if
        plot(x_plt_axis, squeeze(dataset.(f_names{jse}).damping_rate), 'LineWidth', 2)
        legend(graph_labels)
    else
        populate_graph(dataset.(f_names{jse}).damping_rate, years_input, times, x_plt_axis)
    end %if
    plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:', 'HandleVisibility', 'off')
    ylabel([f_names{jse},' rates (1/turns)'])
    if jse == 2
        leg = legend('show');
        leg.Layout.Tile = 'east';
    else
        legend('off')
    end %if
    ymin = min(min(dataset.(f_names{jse}).damping_rate,[],2));
    if ymin > 0
        ymin = 0;
    end %if
    ymax = max(max(dataset.(f_names{jse}).damping_rate,[],2));
    ymax = ymax + ymax /10;
    if ymax < 0
        ymax = 0;
    end %if
    ylim([ymin ymax]);
    xlim([min(x_plt_axis), max(x_plt_axis)])
    grid on
    hold off
end %for

% add labels if it is a parameter sweep.
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    for tb = length(experimental_setup.param):-1:1
        labels{tb} = num2str(experimental_setup.param(tb));
    end %for
    legend(labels)
end %if

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    f2 = figure('Position',[50, 50, 1400, 800]);
    t2 = tiledlayout(f2, 2, 2,'TileSpacing','compact', 'Padding', 'tight');
    title(t2, ['Damping rates vs ', experimental_setup.sweep_parameter, ' in the ', experimental_setup.axis, ' axis'])
    xlabel(t2, experimental_setup.sweep_parameter)
    for jse = 1:length(f_names)
        nexttile(t2)
        hold on
        plot(experimental_setup.param, dataset.(f_names{jse}).damping_rate')
        ylabel([f_names{jse},' rates (1/turns)'])
        grid on
        plot([experimental_setup.param(1), experimental_setup.param(end)], [0,0], 'r:', 'HandleVisibility', 'off')

        hold off
    end %for

    if strcmp(experimental_setup.sweep_parameter, 'current')
        f3 = figure('Position',[50, 50, 1400, 800]);
        t3 = tiledlayout(f3, 2, 2,'TileSpacing','compact', 'Padding', 'tight');
        title(t3, 'Extrapolated data')
        xlabel(t3, experimental_setup.sweep_parameter)
        x1 = 0:1:300;
        for jse = 1:length(f_names)
            nexttile(t3)
            hold on;
            passive_mode_rate = zeros(length(dataset.(f_names{jse}).damping_rate), 1);
            for ks = 1:length(dataset.(f_names{jse}).damping_rate)
                P = polyfit(experimental_setup.param',dataset.(f_names{jse}).damping_rate(:,ks),1);
                passive_mode_rate(ks) = P(1);
                P_start = find(x1 < min(experimental_setup.param), 1, 'last');
                P_points = polyval(P,x1);
                % Find the first time after the lowest current that the extrapolation goes negative.
                P_loc = find(sign(P_points(P_start:end))==-1,1, 'first');
                if ~isempty(P_loc)
                    plot(x1, P_points,'DisplayName', ['Mode ', num2str(x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2);
                    plot(experimental_setup.param', dataset.(f_names{jse}).damping_rate(:,ks),'ko', 'HandleVisibility', 'off');
                end %if
            end %for
            xlabel(experimental_setup.sweep_parameter)
            ylabel([f_names{jse},' rates (1/turns)'])

            %         legend('Location', 'eastoutside')
            legend('off')
            grid on
            plot([x1(1), x1(end)], [0,0], 'r:', 'HandleVisibility', 'off')
            hold off
        end %for
    end %if
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