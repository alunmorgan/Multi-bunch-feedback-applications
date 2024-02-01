function mbf_tunescan_over_modes_plotting(tunescan)
% Plots the effectiveness of correction across all modes.
%
% Args:
%       tunescan (structure): Captured data from a single experiment.
%
% Example: mbf_tunescan_plotting(tunescan)

if ~isfield(tunescan, 'harmonic_number')
    [~, tunescan.harmonic_number, ~, ~] = mbf_system_config;
end %if
harmonic_number = tunescan.harmonic_number;

% reshape the results
fracttune = tunescan.scale(1:tunescan.exp_setup.n_captures);
for n = 1:size(tunescan.data,2)
    result = reshape(abs(tunescan.data(:,n)), tunescan.exp_setup.n_captures, harmonic_number);
    % plot the results
    figure(n)
    imagesc(1:harmonic_number, fracttune, result)
    xlabel('mode number')
    ylabel('fractional tune')
    yy  = colorbar;
    ylabel(yy,'magnitude of response')
end