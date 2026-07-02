function BBBFE_gain_scan_plotting(data)

graph_name = regexprep(data.base_name, '_', ' ');

% plotting
figure('Position', [20, 40, 800, 800])
t = tiledlayout(1, 1,'TileSpacing','compact', 'Padding', 'tight');
instructions = 'The excited bunch signal should be as high as possible while maximising the signal differences.';
title(t, ['BBBFE ',graph_name, ' axis on ', datestr(data.time)])
subtitle(t, instructions, "FontAngle", "italic", "FontSize", 10)
xlabel(t, 'phase (degrees)')
nexttile(1);
hold on
semilogy(data.gain, data.adc_mean, 'DisplayName', 'ADC mean')
semilogy(data.gain, data.adc_max, 'DisplayName','ADC max')
semilogy(data.gain, data.adc_min, 'DisplayName', 'ADC min')
if isfield(data, 'original_setting')
    extents_y = get(gca, 'YLim');
    plot([data.original_setting, data.original_setting], extents_y,...
        'r:', 'DisplayName', 'Original setting', 'LineWidth', 2)
end %iflegend('Location', 'Best')
ylabel('Signal')
grid on
hold off
