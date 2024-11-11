function DORIS_phase_scan_plotting(data)

% plotting
figure;
tiledlayout('flow')
nexttile
hold all
semilogy(data.phase, data.main_x, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1_x, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2_x, 'DisplayName', 'Following bunch')
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal')
title(['DORIS target phase sweep on ', datestr(data.time)])
grid on
hold off
