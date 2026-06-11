function BBBFE_system_phase_scan_plotting(data)

temp = regexp(data.base_name, '.*_([xys])_axis$', 'tokens');
mbf_ax = temp{1}{1};
graph_name = regexprep(data.base_name, '_', ' ');

figure('Position', [20, 40, 800, 800])
t = tiledlayout(4, 1,'TileSpacing','compact', 'Padding', 'tight');
if strcmpi(mbf_ax, 's')
    instructions = 'Q should be placed at ADC amplitude minimum (i.e. the zero crossing).';
else
    instructions = 'The excited bunch signal should be as high as possible while maximising the signal differences.';
end %if
title(t, ['BBBFE ',graph_name, ' axis on ', datestr(data.time)])
subtitle(t, instructions, "FontAngle", "italic", "FontSize", 10)
xlabel(t, 'phase (degrees)')
ax1 = nexttile(1);
hold on
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
add_original_values(mbf_ax, data)
legend('Location', 'Best')
ylabel('Signal')
grid on
hold off

ax2 = nexttile(2);
hold on
semilogy(data.phase, data.main - data.side1, 'DisplayName', 'Excited bunch - Preceeding bunch')
semilogy(data.phase, data.main - data.side2, 'DisplayName','Excited bunch - Following bunch')
add_original_values(mbf_ax, data)
legend('Location', 'Best')
ylabel('Signal differences')
grid on
hold off

ax3 = nexttile(3);
hold on
semilogy(data.phase, data.adc_phase, 'DisplayName', 'ADC phase')
add_original_values(mbf_ax, data)
legend('Location', 'Best')
ylabel('ADC phase')
grid on
hold off

ax4 = nexttile(4);
hold on
% semilogy(data.phase, data.adc_min, 'DisplayName', 'Min')
% semilogy(data.phase, data.adc_max, 'DisplayName', 'Max')
% semilogy(data.phase, data.adc_mean, 'DisplayName', 'Mean')

add_original_values(mbf_ax, data)
legend('Location', 'Best')
ylabel('ADC Amplitude')
grid on
hold off


linkaxes([ax1, ax2, ax3, ax4], 'x')
end %function

function add_original_values(mbf_ax, data)

extents_y = get(gca, 'YLim');
if isfield(data, 'original_setting')
    if strcmpi(mbf_ax, 's')
        plot([data.original_setting, data.original_setting], extents_y,...
            'r:', 'DisplayName', 'Original setting(I)', 'LineWidth', 2)
        plot([data.original_settingQ, data.original_settingQ], extents_y,...
            'c:', 'DisplayName', 'Original setting(Q)', 'LineWidth', 2)
    else
        plot([data.original_setting, data.original_setting], extents_y,...
            'r:', 'DisplayName', 'Original setting', 'LineWidth', 2)
    end %if
end %if
end %function