function data_panel = mbf_archival_plotting_setup(requested_data, times, experimental_setup)
% Plots the data processed by mbf_growdamp_archival_analysis.
% Args:
%      requested_data(structure): data and metatdata.
%      times (numeric vector): Datetimes of the datasets.
%      experimental_setup (structure): The setup parameters for the
%                                      analysis.
%
% Example: mbf_growdamp_archival_plotting(dr_passive, dr_active, error_passive, error_active, times, setup, selections, extents)

[~, harmonic_number, ~, ~] = mbf_system_config;
ranges_to_display = {'RF', 'time','current'};

graph_text{1} = ['Analysis type: ', experimental_setup.anal_type];

if strcmp(experimental_setup.anal_type, 'parameter_sweep')
    graph_labels = cell(1, length(experimental_setup.param));
    for hw = 1:length(experimental_setup.param)
        graph_labels{hw}=num2str(experimental_setup.param(hw));
    end % if
end %if

figure('Position',[50, 50, 1400, 800])
p = uipanel('Position', [0 0.02 0.175 0.93]);
data_panel = uipanel('Position', [0.18 0.02 0.82 0.96]);
t = tiledlayout(p, 3, 1, 'TileSpacing','compact', 'Padding', 'tight');
annotation('textbox', [0 1-0.3 0.3 0.3], 'String', graph_text, 'FitBoxToText', 'on', 'Interpreter', 'none');

% Plot the RF variation from the setpoint.
for hse = 1:length(times)
    requested_data{hse}.RF = requested_data{hse}.RF - 4.99684E8;
end %for

ck = 1;
for hrd = 1:length(ranges_to_display)
    if strcmp(ranges_to_display{hrd}, 'RF')
        graph_label = 'RF variation (Hz)';
    elseif strcmp(ranges_to_display{hrd}, 'current')
        graph_label = 'Current (mA)';
    else
        graph_label = ranges_to_display{hrd};
    end %if
    if isfield(requested_data{1}, ranges_to_display{hrd})
        if strcmp(ranges_to_display{hrd}, 'time')
            continue
        else
            nexttile(t)
            xlabel('Time')
            title(ranges_to_display{hrd})
            data_temp = NaN(length(times),1);
            for hse = 1:length(times)
                data_temp(hse) = requested_data{hse}.(ranges_to_display{hrd});
            end %for
            plot(times, data_temp, 'o:')
            datetick('x', 'dd-mmm-yy')
            ylabel(graph_label)
            if strcmp(ranges_to_display{hrd}, 'RF')
                title('reference 499.684MHz')
            end %if
            clear data_temp
            ck = ck +1;
        end %if
    end %if
end %for

if isfield(requested_data{1}, 'fill_pattern')
    axfp = nexttile(t);
    hold on
    for hkw = 1:length(requested_data)
        plot(1:harmonic_number, requested_data{hkw}.fill_pattern, 'b')
    end %for
    ylim([0 inf])
    xlim([1 harmonic_number])
    set(axfp, 'XTick', [])
    title('Fill pattern variation')
    ylabel('Charge (nC)')
end %if

% add labels if it is a parameter sweep.
if nargin == 4 && strcmp(experimental_setup.anal_type, 'parameter_sweep')
    for tb = length(experimental_setup.param):-1:1
        labels{tb} = num2str(experimental_setup.param(tb));
    end %for
    legend(labels)
end %if
