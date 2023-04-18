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

start_time  = datetime("now");
nd = 1;
while 1==1
    n_samples =60;
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
    date_mat = datevec(datetime("now") - start_time);
    nd = nd +1;
    if date_mat(4) > 6 % save every 6 hours.    
        save(fullfile(save_loc, ['chromaticity_', start_time]), "chro_time",...
            "chro_y_std", "chro_y_mean","chro_x_std", "chro_x_mean", "start_time")
        start_time = datetime("now");
        nd =1;
    end %if
end %while


