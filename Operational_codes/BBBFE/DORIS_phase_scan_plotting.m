function DORIS_phase_scan_plotting(data)

% plotting
figure;
tiledlayout('flow')
nexttile
hold all
semilogy(data.phase, data.main_x, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1_x, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2_x, 'DisplayName', 'Following bunch')
legend
xlabel('phase (degrees)')
ylabel('Signal')
title('DORIS target phase sweep')
grid on
hold off
% 
% nexttile
% hold all
% semilogy(data.phase, data.main_y, 'DisplayName', 'Excited bunch')
% semilogy(data.phase, data.side1_y, 'DisplayName','Preceeding bunch')
% semilogy(data.phase, data.side2_y, 'DisplayName', 'Following bunch')
% legend
% xlabel('phase (degrees)')
% ylabel('Signal')
% title('DORIS target phase sweep for Y axis')
% grid on
% hold off