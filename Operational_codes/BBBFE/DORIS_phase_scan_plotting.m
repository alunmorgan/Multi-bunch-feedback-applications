function DORIS_phase_scan_plotting(data)

% plotting
figure;
tiledlayout('flow')
nexttile
hold all
semilogy(data.phase, data.main_x, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1_x, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2_x, 'DisplayName', 'Following bunch')
extents_y = get(gca, 'YLim');
if isfield(data, 'original_setting')
    plot([data.original_setting, data.original_setting], extents_y,...
        'r:', 'DisplayName', 'Original setting', 'LineWidth', 2)
end %if
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal')
title(['DORIS target phase sweep on ', datestr(data.time)])
grid on
hold off
