function BBBFE_clock_phase_scan_plotting(data, ax, mbf_ax)

% plotting
figure;
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
legend
xlabel('phase (degrees)')
ylabel('Signal')
title(['Clock sweep for clock' num2str(ax), ' ', mbf_ax, 'axis'])
grid on
hold off
