function mbf_growdamp_multi_frequency(mbf_axis, tune, n_samples_per_side, tune_step)
% Runs the growdamp routine at the tune and additional frequency points
% either side of it in order to capture sideband information.
for ks = 1:n_samples_per_side
list_of_tunes_upper(ks,1) = tune - (n_samples_per_side  * tune_step) + tune_step * (ks -1);
list_of_tunes_lower(ks,1) = tune + tune_step * ks;
end %for
list_of_tunes = cat(1, list_of_tunes_upper, tune, list_of_tunes_lower);
gd_multi_f = cell(length(list_of_tunes),1);
for nd = 1:length(list_of_tunes)
mbf_growdamp_setup(mbf_axis, list_of_tunes(nd))
gd_multi_f{nd, 1} = mbf_growdamp_capture(mbf_axis, 'save_to_archive', 'no');
end %for

[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};
% START HERE the save won't work with a cell array as it will look for
% data.filename.
 save_to_archive(root_string, gd_multi_f)