function BBBFE_system_phase_scan_plotting(mbf_ax, data)

figure;
ax1 =subplot(2,1,1);
hold all
semilogy(data.phase, data.main, 'DisplayName', 'Excited bunch')
semilogy(data.phase, data.side1, 'DisplayName','Preceeding bunch')
semilogy(data.phase, data.side2, 'DisplayName', 'Following bunch')
extents_y = get(gca, 'YLim');
if strcmpi(mbf_ax, 'S')
    plot([data.original_setting, data.original_setting], extents_y, 'r:', 'DisplayName', 'Original setting(I)')
    plot([data.original_setting, data.original_settingQ], extents_y, 'c:', 'DisplayName', 'Original setting(Q)')
else
    plot([data.original_setting, data.original_setting], extents_y, 'r:', 'DisplayName', 'Original setting')
end %if
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal')
title(['BBBFE system phase sweep ', mbf_ax, ' axis on ', datestr(data.time)])
grid on
hold off

ax2 = subplot(2,1,2);
hold all
semilogy(data.phase, data.main - data.side1, 'DisplayName', 'Excited bunch - Preceeding bunch')
semilogy(data.phase, data.main - data.side2, 'DisplayName','Excited bunch - Following bunch')
extents_y = get(gca, 'YLim');
if strcmpi(mbf_ax, 'S')
    plot([data.original_setting, data.original_setting], extents_y, 'r:', 'DisplayName', 'Original setting(I)')
    plot([data.original_setting, data.original_settingQ], extents_y, 'c:', 'DisplayName', 'Original setting(Q)')
else
    plot([data.original_setting, data.original_setting], extents_y, 'r:', 'DisplayName', 'Original setting')
end %if
legend('Location', 'Best')
xlabel('phase (degrees)')
ylabel('Signal differences')
grid on
hold off

linkaxes([ax1, ax2], 'x')