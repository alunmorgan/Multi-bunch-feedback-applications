function chromaticity_plot_live(n_samples)

chro_time = NaT(n_samples,1);
chro_x_temp = NaN(n_samples,1);
chro_y_temp = NaN(n_samples,1);
figure;
for kw = 1:n_samples
    chro_x_temp(kw) = chromaticity_from_sidebands('x');
    chro_y_temp(kw) = chromaticity_from_sidebands('y');
    chro_time(kw) = datetime('now');
    pause(1.2) % make sure there is new data.
    % maybe better to use monitors.
    if rem(kw, 10) == 0
        plot(chro_time, chro_x_temp, 'b*', chro_time, chro_y_temp, 'r^')
    end
end %for
plot(chro_time, chro_x_temp, 'b*', chro_time, chro_y_temp, 'r^')