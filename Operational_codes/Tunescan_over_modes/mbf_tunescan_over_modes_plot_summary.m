function mbf_tunescan_over_modes_plot_summary(tunescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       tunescan (structure): Captured data from a single experiment.
%
% Example: mbf_tunescan_plotting(tunescan)

% reshape the results
fracttune = tunescan.scale(1:tunescan.n_captures);
for n = 1:size(tunescan.data,2)
    result = reshape(abs(tunescan.data(:,n)), ...
        tunescan.n_captures, tunescan.harmonic_number);
    % plot the results
    figure(n)
    imagesc(1:harmonic_number, fracttune, result)
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
end %for