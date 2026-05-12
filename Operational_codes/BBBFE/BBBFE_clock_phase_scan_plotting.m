function BBBFE_clock_phase_scan_plotting(data)

graph_name = regexprep(data.base_name, '_', ' ');

% plotting
figure('Position', [20, 40, 800, 800])
t = tiledlayout(3, 1,'TileSpacing','compact', 'Padding', 'tight');
title(t, ['BBBFE ',graph_name, ' axis on ', datestr(data.time)])
xlabel(t, 'phase (degrees)')
ax1 = nexttile(1);
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
legend('Location', 'Best')
ylabel('Signal')
grid on
hold off

ax2 = nexttile(2);
hold all
semilogy(data.phase, data.main - data.side1, 'DisplayName', 'Excited bunch - Preceeding bunch')
semilogy(data.phase, data.main - data.side2, 'DisplayName','Excited bunch - Following bunch')
legend('Location', 'Best')
ylabel('Signal differences')
grid on
hold off

ax3 = nexttile(3);
hold all
semilogy(data.phase, data.adc_phase, 'DisplayName', 'ADC phase')
legend('Location', 'Best')
ylabel('ADC phase')
grid on
hold off

linkaxes([ax1, ax2, ax3], 'x')