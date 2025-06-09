function BBBFE_clock_phase_scan_plotting( mbf_ax, data)

% plotting
figure;
ax1 =subplot(3,1,1);
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal')
title(['BBBFE clock phase sweep for ', mbf_ax, ' axis on ', datestr(data.time)])
grid on
hold off

ax2 = subplot(3,1,2);
hold all
semilogy(data.phase, data.main - data.side1, 'DisplayName', 'Excited bunch - Preceeding bunch')
semilogy(data.phase, data.main - data.side2, 'DisplayName','Excited bunch - Following bunch')
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal differences')
grid on
hold off

ax3 = subplot(3,1,3);
hold all
semilogy(data.phase, data.adc_phase, 'DisplayName', 'ADC phase')
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('ADC phase')
grid on
hold off

linkaxes([ax1, ax2, ax3], 'x')