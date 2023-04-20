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

if ~isempty(modescan_x_files)
    try
        modescan_x = load(modescan_x_files{end},'data');
        [data_magnitude_x, data_phase_x] = mbf_modescan_analysis(modescan_x.data);
        mbf_modescan_plotting(data_magnitude_x, data_phase_x, modescan_x.data)
    catch
        disp('Problem with modescan X axis data')
    end %try
end %if
if ~isempty(modescan_y_files)
    try
        modescan_y = load(modescan_y_files{end},'data');
        [data_magnitude_y, data_phase_y] = mbf_modescan_analysis(modescan_y.data);
        mbf_modescan_plotting(data_magnitude_y, data_phase_y, modescan_y.data)
    catch
        disp('Problem with modescan Y axis data')
    end %try
end %if
if ~isempty(modescan_s_files)
    try
        modescan_s = load(modescan_s_files{end},'data');
        [data_magnitude_s, data_phase_s] = mbf_modescan_analysis(modescan_s.data);
        mbf_modescan_plotting(data_magnitude_s, data_phase_s, modescan_s.data)
    catch
        disp('Problem with modescan S axis data')
    end %try
end %if

if ~isempty(growdamp_x_files)
    try
        growdamp_x = load(growdamp_x_files{end},'data');
        [poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x.data);
        mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, growdamp_x.data,...
            'outputs', 'both')
    catch
        disp('Problem with growdamp X axis data')
    end %try
end %if
if ~isempty(growdamp_y_files)
    try
        growdamp_y = load(growdamp_y_files{end},'data');
        [poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y.data);
        mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, growdamp_y.data,...
            'outputs', 'both')
    catch
        disp('Problem with growdamp Y axis data')
    end %try
end %if
if ~isempty(growdamp_s_files)
    try
        growdamp_s = load(growdamp_s_files{end},'data');
        [poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s.data);
        mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s, growdamp_s.data,...
            'outputs', 'both')
    catch
        disp('Problem with growdamp S axis data')
    end %try
end %if

if ~isempty(spectrum_x_files)
    try
        spectrum_x = load(spectrum_x_files{end},'data');
        analysed_data_x = mbf_spectrum_analysis(spectrum_x.data, fold);
        mbf_spectrum_plotting(analysed_data_x, spectrum_x.data.meta_data)
    catch
        disp('Problem with spectrum X axis data')
    end %try
end %if
if ~isempty(spectrum_y_files)
    try
        spectrum_y = load(spectrum_y_files{end},'data');
        analysed_data_y = mbf_spectrum_analysis(spectrum_y.data, fold);
        mbf_spectrum_plotting(analysed_data_y, spectrum_y.data.meta_data)
    catch
        disp('Problem with spectrum Y axis data')
    end %try
end %if
if ~isempty(spectrum_s_files)
    try
        spectrum_s = load(spectrum_s_files{end},'data');
        analysed_data_s = mbf_spectrum_analysis(spectrum_s.data, fold);
        mbf_spectrum_plotting(analysed_data_s, spectrum_s.data.meta_data)
    catch
        disp('Problem with spectrum S axis data')
    end %try
end %if
