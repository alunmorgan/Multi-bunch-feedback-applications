function mbf_growdamp_multi_frequency(mbf_axis, tune, n_samples_per_side, tune_step)
% Runs the growdamp routine at the tune and additional frequency points
% either side of it in order to capture sideband information.
list_of_tunes_upper = NaN(n_samples_per_side, 1);
list_of_tunes_lower = NaN(n_samples_per_side, 1);
for ks = 1:n_samples_per_side
    list_of_tunes_upper(ks,1) = tune - (n_samples_per_side  * tune_step) + tune_step * (ks -1);
    list_of_tunes_lower(ks,1) = tune + tune_step * ks;
end %for
list_of_tunes = cat(1, list_of_tunes_upper, tune, list_of_tunes_lower);
gd_multi_f_temp = cell(length(list_of_tunes),1);
for nd = 1:length(list_of_tunes)
    mbf_growdamp_setup(mbf_axis, list_of_tunes(nd))
    gd_multi_f_temp{nd, 1} = mbf_growdamp_capture(mbf_axis, 'save_to_archive', 'no');
end %for
gd_multi_f = gd_multi_f_temp{1};
gd_multi_f.tunes = list_of_tunes;
gd_multi_f.gddata{1} = gd_multi_f.data;
gd_multi_f.gddata_freq{1} = gd_multi_f.data_freq;
gd_multi_f = rmfield(gd_multi_f, 'data');
gd_multi_f = rmfield(gd_multi_f, 'data_freq');
for ns = 2:length(list_of_tunes)
    gd_multi_f.gddata{ns} = gd_multi_f_temp{ns}.data;
    gd_multi_f.gddata_freq{ns} = gd_multi_f_temp{ns}.data_freq;
end %for

[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};
% FIXME the save won't work with a cell array as it will look for
% data.filename.
save_to_archive(root_string, gd_multi_f)

poly_data_x = cell(length(list_of_tunes),1);
frequency_shifts_x = cell(length(list_of_tunes),1);
for ne = 1:length(list_of_tunes)
    temp = gd_multi_f;
    temp.data = temp.gddata{ne};
    temp.data_freq = temp.gddata_freq{ne};
    temp = rmfield(temp, 'gddata');
    temp = rmfield(temp, 'gddata_freq');
    [poly_data_x{ne}, frequency_shifts_x{ne}] = mbf_growdamp_analysis(temp);
end %for
mbf_growdamp_plot_summary_multi_f(poly_data_x, frequency_shifts_x, list_of_tunes,...
    'outputs', 'both', 'axis', mbf_axis)