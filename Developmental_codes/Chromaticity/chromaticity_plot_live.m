function chromaticity_plot_live(n_repeats, n_samples, n_trys)
% This only gives valid results if the MBF feedback is off, 
% as it would otherwise supress the central peak 
%
% This takes the ratio of the sidebamd areas vs the central peak area and along 
% with measurements of energy spread and synchrotron tune fit to a theoretical 
% model to return the chromaticity value.
%
% Args:
%       n_repeats(int): Number of repeat sets.
%       n_samples(int): Number of repeat measurements in each set.
%       n_trys(int): Max number of retrys to get complete dataset.
%
% Outputs a graph of n_repeat points for each axis vs time of measurement.
%
% Example: chromaticity_plot_live(100, 10, 5)

chro_time = NaT(n_repeats,1);
chro_x_mean = NaN(n_repeats,1);
chro_x_std = NaN(n_repeats,1);
chro_y_mean = NaN(n_repeats,1);
chro_y_std = NaN(n_repeats,1);
chro_x_temp = NaN(n_samples,1);
chro_y_temp = NaN(n_samples,1);
figure;
for nd = 1:n_repeats
    chro_time(nd) = datetime('now');
    for kw = 1:n_samples
        chro_x_temp(kw) = chromaticity_from_sidebands('x', n_trys);
        chro_y_temp(kw) = chromaticity_from_sidebands('y', n_trys);
        pause(1.2) % make sure there is new data.
    end
    chro_x_mean(nd) = mean(chro_x_temp, 'omitnan');
    chro_x_std(nd) = std(chro_x_temp, 0, 'omitnan');
    chro_y_mean(nd) = mean(chro_y_temp, 'omitnan');
    chro_y_std(nd) = std(chro_y_temp, 0, 'omitnan');
    grid on
    errorbar(chro_time, chro_x_mean, chro_x_std ,'b*')
    hold on
    errorbar(chro_time, chro_y_mean, chro_y_std,'r^')
    hold off
end %for
