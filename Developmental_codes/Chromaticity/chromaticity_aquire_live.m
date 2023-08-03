function chromaticity_aquire_live(save_loc)
% Measures the live tune waveform for both x and y axis
% and calculates the chromaticity from that.
% Saves data to files at location save_loc every 6 hours.
%
% Example chromaticity_aquire_live(save_loc)
if nargin == 0
    error('Please specify a save location')
elseif nargin > 1
    error('Wrong number of input arguments. Only the save location is needed')
end %if


n_samples =60;
n_per_file = 18000; % about 6 hours of data capture
while 1==1
    start_time  = datetime("now");
    chro_x_mean = nan(n_per_file,1);
    chro_x_std = nan(n_per_file,1);
    chro_y_mean = nan(n_per_file,1);
    chro_y_std = nan(n_per_file,1);
    chro_time =  nan(n_per_file,1);
    for nd = 1:n_per_file
        time_temp = NaN(1:n_samples,1);
        chro_x_temp = NaN(1:n_samples,1);
        chro_y_temp = NaN(1:n_samples,1);
        for kw = 1:n_samples
            time_temp(kw) = datetime("now");
            chro_x_temp(kw) = chromaticity_from_sidebands(1);
            chro_y_temp(kw) = chromaticity_from_sidebands(2);
            pause(1.2) % make sure there is new data.
            % maybe better to use monitors.
        end %for
        clear kw

        chro_x_mean(nd) = nonanmean(chro_x_temp);
        chro_x_std(nd) = nonanstd(chro_x_temp);
        chro_y_mean(nd) = nonanmean(chro_y_temp);
        chro_y_std(nd) = nonanstd(chro_y_temp);
        chro_time(nd) = time_temp(1) + (time_temp(end) - time_temp(1)) / 2;
        clear chro_x_temp chro_y_temp time_temp
    end %for
    save(fullfile(save_loc, ['chromaticity_', start_time]), "chro_time",...
        "chro_y_std", "chro_y_mean","chro_x_std", "chro_x_mean", "start_time")
    clear start_time chro_x_mean chro_x_std chro_y_mean chro_y_std chro_time
end %while
