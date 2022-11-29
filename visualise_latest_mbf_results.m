function visualise_latest_mbf_results

[root_path, ~, ~, ~] = mbf_system_config;

files = dir_list_gen_tree(root_path{1}, '.mat', 1);

modescan_x_files = files(contains(files, 'Modescan_x'));
modescan_y_files = files(contains(files, 'Modescan_y'));
modescan_s_files = files(contains(files, 'Modescan_s'));

growdamp_x_files = files(contains(files, 'Growdamp_x'));
growdamp_y_files = files(contains(files, 'Growdamp_y'));
growdamp_s_files = files(contains(files, 'Growdamp_s'));

spectrum_x_files = files(contains(files, 'Spectrum_x'));
spectrum_y_files = files(contains(files, 'Spectrum_y'));
spectrum_s_files = files(contains(files, 'Spectrum_s'));

modescan_x = load(modescan_x_files{end},'data');
modescan_y = load(modescan_y_files{end},'data');
modescan_s = load(modescan_s_files{end},'data');

growdamp_x = load(growdamp_x_files{end},'data');
growdamp_y = load(growdamp_y_files{end},'data');
growdamp_s = load(growdamp_s_files{end},'data');

spectrum_x = load(spectrum_x_files{end},'data');
spectrum_y = load(spectrum_y_files{end},'data');
spectrum_s = load(spectrum_s_files{end},'data');

mbf_modescan_plotting(modescan_x.data)
mbf_modescan_plotting(modescan_y.data)
mbf_modescan_plotting(modescan_s.data)

[poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x.data);
mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, ...
    'outputs', 'both', 'axis', mbf_axis)

[poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y.data);
mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, ...
    'outputs', 'both', 'axis', mbf_axis)

[poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s.data);
mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s, ...
    'outputs', 'both', 'axis', mbf_axis)

analysed_data_x = mbf_spectrum_analysis(spectrum_x.data, fold);
mbf_spectrum_plotting(analysed_data_x, spectrum_x.data.meta_data)

analysed_data_y = mbf_spectrum_analysis(spectrum_y.data, fold);
mbf_spectrum_plotting(analysed_data_y, spectrum_y.data.meta_data)

analysed_data_s = mbf_spectrum_analysis(spectrum_s.data, fold);
mbf_spectrum_plotting(analysed_data_s, spectrum_s.data.meta_data)