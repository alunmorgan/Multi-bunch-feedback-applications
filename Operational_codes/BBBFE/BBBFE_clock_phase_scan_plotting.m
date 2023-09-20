function BBBFE_clock_phase_scan_plotting( mbf_ax, data)

% plotting
figure;
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
legend
xlabel('phase (degrees)')
ylabel('Signal')
title(['Clock sweep for ', mbf_ax, 'axis'])
grid on
hold off
