function single_kick_pp = mbf_single_kick_postprocessing(single_kick)

bpm_datatypes = {'bpm_FR_data', 'bpm_FT_data', 'bpm_TbT_data'};
selected_datatype = bpm_datatypes{1};

scan_length = length(single_kick.bpm_data);
used_bpms = fieldnames(single_kick.bpm_data{1}.(selected_datatype){1});
n_repeats = length(single_kick.bpm_data{1}.(selected_datatype));

for nfe = 1:scan_length
    for kds = 1:length(used_bpms)
        x_data_temp = NaN(n_repeats, length(single_kick.bpm_data{nfe}.(selected_datatype){1}.(used_bpms{kds}).X));
        y_data_temp = NaN(n_repeats, length(single_kick.bpm_data{nfe}.(selected_datatype){1}.(used_bpms{kds}).Y));
        for shd = 1:n_repeats
            x_data_temp(shd,:) = single_kick.bpm_data{nfe}.(selected_datatype){shd}.(used_bpms{kds}).X;
            y_data_temp(shd,:) = single_kick.bpm_data{nfe}.(selected_datatype){shd}.(used_bpms{kds}).Y;
        end %for
        x_mean = mean(x_data_temp, 1);
        y_mean = mean(y_data_temp, 1);
        single_kick_pp.beam_signal_x(nfe, kds, :) = x_mean;
        single_kick_pp.beam_signal_y(nfe, kds, :) = y_mean;
        single_kick_pp.beam_oscillation_x(nfe, kds) = std(x_mean);
        single_kick_pp.beam_oscillation_y(nfe, kds) = std(y_mean);
        clear x_data_temp y_data_temp x_mean y_mean
    end %for
end %for
single_kick.used_bpms = used_bpms;
