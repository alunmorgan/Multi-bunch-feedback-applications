function mbf_tunescan_over_modes_plot_summary(tunescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       tunescan (structure): Captured data from a single experiment.
%
% Example: mbf_tunescan_plotting(tunescan)

% reshape the results
fracttune = tunescan.scale(1:tunescan.n_captures);
for n = 1:1%size(tunescan.data,2)
    result = reshape(abs(tunescan.data(:,n)), ...
        tunescan.n_captures, tunescan.harmonic_number);
    for js = 1:size(result, 2)
    [fit_curve,gof2] = tune_fit(fracttune, result(:,js));
    fit_width(js) = fit_curve.a;
    fit_height(js) = fit_curve.c * 2 / pi / fit_width(js);
    fit_centre(js) = fit_curve.n;
    fit_confidence(js) = gof2.sse;
    end %for

    %find zoomed in area.
    lower_tune_limit = mean(fit_centre) - max(fit_width) /2;
    upper_tune_limit = mean(fit_centre) + max(fit_width) /2;
    % plot the results
    f = figure('Position', [20, 40, 1600, 800]);
    gp = tiledlayout(f, 4, 2,'TileSpacing','compact', 'Padding', 'tight');
    title(gp, {['MBF tunescan results ', tunescan.ax_label,...
    ' axis ', datestr(tunescan.time)];...
    ['Current: ', num2str(round(tunescan.current)), 'mA']})

    nexttile(gp, 1, [2 1]);
    imagesc(1:tunescan.harmonic_number, fracttune, result)
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
    
    nexttile(gp, 5, [2 1]);
    imagesc(1:tunescan.harmonic_number, fracttune, result)
    ylim([lower_tune_limit upper_tune_limit])
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
    
    nexttile(gp, 2);
    plot(1:tunescan.harmonic_number, max(result, [], 1, "omitnan"),...
        'DisplayName', 'Raw data', 'LineWidth', 2)
    hold on
    plot(1:tunescan.harmonic_number, fit_height, 'm','DisplayName', 'Fitted data')
    xlabel('mode number')
    ylabel('magnitude of peak')
    legend
    grid on
    
    nexttile(gp, 4);
    plot(1:tunescan.harmonic_number, fit_width, 'm', 'DisplayName', 'Fitted data')
    xlabel('mode number')
    ylabel('width of peak')
    grid on
    
    nexttile(gp, 6);
    plot(1:tunescan.harmonic_number, fit_confidence, 'm', 'DisplayName', 'Fitted data')
    xlabel('mode number')
    ylabel('error of fit')
    grid on
end %for