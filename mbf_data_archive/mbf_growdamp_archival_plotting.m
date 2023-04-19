function mbf_growdamp_archival_plotting(requested_data, dr_passive, dr_active, error_passive, error_active, times, experimental_setup)
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
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors.
%
% Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if

[~, harmonic_number, ~, ~] = mbf_system_config;
x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
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

graph_title = 'Damping rates for different modes';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Damping rates for different modes as a function of ', experimental_setup.sweep_parameter];...
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
    plot(x_plt_axis, dr_passive)
    legend(graph_labels)
else
    populate_graph(dr_passive, years_input, times, x_plt_axis)
end %if
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:', 'HandleVisibility', 'off')
title(graph_title)
xlabel('Mode')
ylabel('Passive damping rates (1/turns)')
legend show
ymin = min(min(dr_passive,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(dr_passive,[],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off

ax2 =axes('OuterPosition', [0.12 0 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, dr_active)
    legend(graph_labels)
else
    populate_graph(dr_active, years_input, times, x_plt_axis)
end %if
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:', 'HandleVisibility', 'off')
% title(graph_title)
xlabel('Mode')
ylabel('Active damping rates (1/turns)')
ymin = min(min(dr_active,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(dr_active,[],2));
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

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    figure('Position',[50, 50, 1400, 800])
    if strcmp(experimental_setup.sweep_parameter, 'current')
        axc1 = axes('OuterPosition', [0 0 0.48 0.5]);
    else
        axc1 = axes('OuterPosition', [0 0 1 0.5]);
    end
    hold on
    plot(experimental_setup.param, dr_passive')
    xlabel(experimental_setup.sweep_parameter)
    ylabel('Passive damping rates (1/turns)')
    grid on
    plot([experimental_setup.param(1), experimental_setup.param(end)], [0,0], 'r:', 'HandleVisibility', 'off')
    
    hold off
    if strcmp(experimental_setup.sweep_parameter, 'current')
        axc2 = axes('OuterPosition', [0 0.5 0.48 0.5]);
    else
        axc2 = axes('OuterPosition', [0 0.5 1 0.5]);
    end
    hold on
    plot(experimental_setup.param, dr_active')
    xlabel(experimental_setup.sweep_parameter)
    ylabel('Active damping rates (1/turns)')
    title(['Damping rates vs ', experimental_setup.sweep_parameter, ' in the ', experimental_setup.axis, ' axis'])
    grid on
    plot([experimental_setup.param(1), experimental_setup.param(end)], [0,0], 'r:', 'HandleVisibility', 'off')
    hold off
    
    
    if strcmp(experimental_setup.sweep_parameter, 'current')
        x1 = [0:1:300];
        axc3 = axes('OuterPosition', [0.52 0 0.48 0.5]);
        hold on;
        %find modes which go unstable
        test = sign(dr_passive);
        test(test==1) =0;
        test = sum(test,1);
        unstable_passive_modes = find(test ~=0);
        %find most unstable / least stable mode
        [~, ind] = min(dr_passive(end,:));
        unstable_passive_modes = unique(cat(2, unstable_passive_modes, ind));
        for ks = 1:length(unstable_passive_modes)
            P = polyfit(experimental_setup.param',dr_passive(:,unstable_passive_modes(ks)),1);
            plot(x1, polyval(P,x1),'DisplayName', ['Mode ', num2str(x_plt_axis(unstable_passive_modes(ks)))]);
            plot(experimental_setup.param', dr_passive(:,unstable_passive_modes(ks)),'ko', 'HandleVisibility', 'off');
        end
        xlabel(experimental_setup.sweep_parameter)
        ylabel('Passive damping rates (1/turns)')
        title('Extrapolated data')
        legend
        grid on
        plot([x1(1), x1(end)], [0,0], 'r:', 'HandleVisibility', 'off')
        hold off
        
        axc4 = axes('OuterPosition', [0.52 0.5 0.48 0.5]);
        hold on;
        test = sign(dr_active);
        test(test==1) =0;
        test = sum(test,1);
        unstable_active_modes = find(test ~=0);
        %find most unstable / least stable mode
        [~, ind] = min(dr_active(end,:));
        unstable_active_modes = unique(cat(2, unstable_active_modes, ind));
        for ks = 1:length(unstable_active_modes)
            P = polyfit(experimental_setup.param',dr_active(:,unstable_active_modes(ks)),1);
            plot(x1, polyval(P,x1),'DisplayName', ['Mode ', num2str(x_plt_axis(unstable_active_modes(ks)))]);
            plot(experimental_setup.param', dr_active(:,unstable_active_modes(ks)),'ko', 'HandleVisibility', 'off');
        end
        xlabel(experimental_setup.sweep_parameter)
        ylabel('Active damping rates (1/turns)')
        title('Extrapolated data')
        legend
        grid on
        plot([x1(1), x1(end)], [0,0], 'r:', 'HandleVisibility', 'off')
        hold off
    end %if
    
end %if

figure
plot(times, zeros(length(times),1), 'o:')
xlabel('Time')
datetick
for hrd = 1:length(ranges_to_display)
    if strcmp(ranges_to_display{hrd}, 'time')
        continue
    else
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
sample_year_temp = datevec(times);
year_list = sample_year_temp(:,1);
if length(unique(year_list)) < 2
    for ner = 1:size(input_data, 1)
        sample_time = datevec(times(ner));
        sample_time = datestr(sample_time);
        plot(x_plt_axis, input_data(ner,:), 'DisplayName', sample_time);
    end %for
else
    for ner = 1:size(input_data, 1)
        years_ind = find(year_list(ner)== years);
        if states(years_ind) == 0
            plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'DisplayName', num2str(sample_year));
            states(years_ind) = 1;
        else
            plot(x_plt_axis, input_data(ner,:), cols{years_ind}, 'HandleVisibility', 'off')
        end %if
    end %for
end %if
xlim([x_plt_axis(1) x_plt_axis(end)])
ylim([y_min y_max])
legend('show')