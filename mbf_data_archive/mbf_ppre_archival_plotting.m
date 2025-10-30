function mbf_ppre_archival_plotting(requested_data, data, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      emittance_x (numeric matrix): Horizontal emittance.
%                                   (bunches vs datasets)
%      emittance_y (numeric matrix): Vertical emittance.
%                                   (bunches vs datasets)
%      beam_size_p1 (numeric matrix): Beam size at pinhole 1.
%      beam_size_p2 (numeric matrix): Beam size at pinhole 2.
%      times (numeric vector): Datetimes of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%      plot_error_graphs (anything): if present the code will plot the results of the fit errors.
%
% Example: mbf_ppre_archival_plotting(requested_data, emittance_x, emittance_y, beam_size_p1, beam_size_p2, times, experimental_setup)

% Only do something if there is data to do something with.
if isempty(times)
    return
end %if

[~, harmonic_number, ~, ~] = mbf_system_config;
x_plt_axis = (0:harmonic_number-1) - harmonic_number/2;
this_year = year(datetime("now"));
ranges_to_display = {'RF', 'time','current'};

years_input = {this_year-5, 'r'; this_year-4, 'b'; this_year-3, 'k'; this_year-2, 'g'; this_year-1, 'c'; this_year, 'm'};

graph_text{1} = ['Analysis type: ', experimental_setup.anal_type];
graph_title = 'Damping rates for different modes';

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_title = {['Emittance as a function of ', experimental_setup.sweep_parameter];...
        ['Using a step size of ', num2str(experimental_setup.parameter_step_size), ' in the ', experimental_setup.axis, ' axis']};
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

figure('Position',[50, 50, 1400, 800])
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');
emittance_x = squeeze(data.emittance_x(:,1 ,1, 1)); %TEMP
emittance_y = squeeze(data.emittance_y(:,1 ,1, 1)); % FIXME
ax1 = axes('OuterPosition', [0.12 0.5 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    emittance_x = squeeze(emittance_x);
    emittance_y = squeeze(emittance_y);
    plot(x_plt_axis, data.emittance_x, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(emittance_x, years_input, times, x_plt_axis)
end %if
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:', 'HandleVisibility', 'off')
title(graph_title)
xlabel('Mode')
ylabel('Horizontal emittance')
legend show
ymin = min(min(emittance_x,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(emittance_x,[],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off

ax2 =axes('OuterPosition', [0.12 0 0.95 0.5]);
hold on
if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    plot(x_plt_axis, emittance_y, 'LineWidth', 2)
    legend(graph_labels)
else
    populate_graph(emittance_y, years_input, times, x_plt_axis)
end %if
plot([x_plt_axis(1), x_plt_axis(end)], [0,0], 'r:', 'HandleVisibility', 'off')
% title(graph_title)
xlabel('Mode')
ylabel('Vertical emittance')
ymin = min(min(emittance_y,[],2));
if ymin > 0
    ymin = 0;
end %if
ymax = max(max(emittance_y,[],2));
ymax = ymax + ymax /10;
ylim([ymin ymax]);
grid on
hold off
ck = 1;
for hrd = 1:length(ranges_to_display)
    if strcmp(ranges_to_display{hrd}, 'time')
        continue
    else    
        axes('OuterPosition', [0.01 ck/3 0.2 0.3]);
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
    end %if
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

linkaxes([ax1,ax2],'x')

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    figure('Position',[50, 50, 1400, 800])
    if strcmp(experimental_setup.sweep_parameter, 'current')
        axes('OuterPosition', [0 0 0.48 0.5]);
    else
        axes('OuterPosition', [0 0 1 0.5]);
    end
    hold on
    plot(experimental_setup.param, data.emittance_x')
    xlabel(experimental_setup.sweep_parameter)
    ylabel('Passive damping rates (1/turns)')
    grid on
    plot([experimental_setup.param(1), experimental_setup.param(end)], [0,0], 'r:', 'HandleVisibility', 'off')
    
    hold off
    if strcmp(experimental_setup.sweep_parameter, 'current')
        axes('OuterPosition', [0 0.5 0.48 0.5]);
    else
        axes('OuterPosition', [0 0.5 1 0.5]);
    end
    hold on
    plot(experimental_setup.param, data.emittance_y')
    xlabel(experimental_setup.sweep_parameter)
    ylabel('Active damping rates (1/turns)')
    title(['Damping rates vs ', experimental_setup.sweep_parameter, ' in the ', experimental_setup.axis, ' axis'])
    grid on
    plot([experimental_setup.param(1), experimental_setup.param(end)], [0,0], 'r:', 'HandleVisibility', 'off')
    hold off
    
    
%     if strcmp(experimental_setup.sweep_parameter, 'current')
%         x1 = 0:1:300;
%         axes('OuterPosition', [0.52 0 0.48 0.5]);
%         hold on;
%         for ks = 1:length(data.emittance_x)
%             P = polyfit(experimental_setup.param',data.emittance_x(:,ks),1);
%             P_start = find(x1 < min(experimental_setup.param), 1, 'last');
%             P_points = polyval(P,x1);
%             % Find the first time after the lowest current that the extrapolation goes negative. 
%             P_loc = find(sign(P_points(P_start:end))==-1,1, 'first');
%             if ~isempty(P_loc)
%             plot(x1, P_points,'DisplayName', ['Mode ', num2str(x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2);
%             plot(experimental_setup.param', data.emittance_x(:,ks),'ko', 'HandleVisibility', 'off');
%             end %if
%         end %for
%         xlabel(experimental_setup.sweep_parameter)
%         ylabel('Passive damping rates (1/turns)')
%         title('Extrapolated data')
%         legend('Location', 'eastoutside')
%         grid on
%         plot([x1(1), x1(end)], [0,0], 'r:', 'HandleVisibility', 'off')
%         hold off
%         
%         axes('OuterPosition', [0.52 0.5 0.48 0.5]);
%         hold on;
%         for ks = 1:length(data.emittance_y)
%             P = polyfit(experimental_setup.param',data.emittance_y(:,ks),1);
%             P_start = find(x1 < min(experimental_setup.param), 1, 'last');
%              P_points = polyval(P,x1);
%             P_loc = find(sign(P_points(P_start:end))==-1,1, 'first');
%             if ~isempty(P_loc)
%             plot(x1, polyval(P,x1),'DisplayName', ['Mode ', num2str(x_plt_axis(ks)), ': ', num2str(x1(P_loc)), 'mA'], 'LineWidth', 2);
%             plot(experimental_setup.param', data.emittance_y(:,ks),'ko', 'HandleVisibility', 'off');
%             end %if
%         end %for
%         xlabel(experimental_setup.sweep_parameter)
%         ylabel('Active damping rates (1/turns)')
%         title('Extrapolated data')
%         legend('Location', 'eastoutside')
%         grid on
%         plot([x1(1), x1(end)], [0,0], 'r:', 'HandleVisibility', 'off')
%         hold off
%     end %if
    
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