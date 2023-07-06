function BBBFE_system_phase_scan_plotting(mbf_ax, data)

figure;
ax1 =subplot(2,1,1);
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
legend
xlabel('phase (degrees)')
ylabel('Signal')
title(['Phase sweep for MBF ', mbf_ax, ' axis on', datestr(data.time)])
grid on
hold off

ax2 = subplot(2,1,1);
hold all
semilogy(data.phase, data.main - data.side1, 'DisplayName', 'Excited bunch - Preceeding bunch')
semilogy(data.phase, data.main - data.side2, 'DisplayName','Excited bunch - Following bunch')
legend
xlabel('phase (degrees)')
ylabel('Signal differences')
grid on
hold off

linkaxes([ax1, ax2], 'x')