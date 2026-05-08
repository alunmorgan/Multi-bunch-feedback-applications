function visualise_latest_mbf_results(varargin)

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addParameter(p, 'save_graphs', 'no', @(x) any(validatestring(x,boolean_string)));
addParameter(p, 'out_path', NaN);
parse(p, varargin{:});

if strcmp(p.Results.save_graphs, 'yes') && any(isnan(p.Results.out_path))
    error(no_path, 'Please provide a path to store the graphs using the out_paths flag.')
end %if

[root_path, ~, ~, ~] = mbf_system_config;

files = dir_list_gen_tree(root_path, '.mat', 1);

ax = {'x', 'y', 's'};
for ax_num = 1:3
    modescan_files = files(contains(files, ['Modescan_', ax{ax_num}]));
    if ~isempty(modescan_files)
        try
            modescan_data = load(modescan_files{end},'data');
            [data_magnitude, data_phase_x] = mbf_modescan_analysis(modescan_data.data);
            mbf_modescan_plotting(data_magnitude, data_phase_x, modescan_data.data)
            if strcmp(p.Results.save_graphs, 'yes')
                saveas(gcf, [p.Results.out_path, 'MBF modescan ', ax{ax_num}, ...
                    ' axis on ', datestr(modescan_data.data.time)], 'png')
            end %if
        catch me_modescan
            disp(['Problem with modescan ', ax{ax_num}, ' axis data'])
            disp(me_modescan.message)
        end %try
    end %if
    clear modescan_files modescan_data
    growdamp_files = files(contains(files, ['Growdamp_', ax{ax_num}]));
    if ~isempty(growdamp_files)
        try
            growdamp_data = load(growdamp_files{end},'data');
            poly_data = mbf_growdamp_analysis(growdamp_data.data);
            mbf_growdamp_plot_summary(poly_data, growdamp_data.data)
            if strcmp(p.Results.save_graphs, 'yes')
                saveas(gcf, [p.Results.out_path, 'MBF growdamp ', ax{ax_num}, ...
                    ' axis on ', datestr(growdamp_data.data.time)], 'png')
            end %if
        catch me_growdamp
            disp(['Problem with growdamp ', ax{ax_num}, ' axis data'])
            disp(me_growdamp.message)
        end %try
    end %if
    clear growdamp_files growdamp_data
    spectrum_files = files(contains(files, ['Spectrum_', ax{ax_num}]));
    if ~isempty(spectrum_files)
        try
            spectrum_data = load(spectrum_files{end},'data');
            analysed_data = mbf_spectrum_analysis(spectrum_data.data);
            mbf_spectrum_plotting(spectrum_data.data, analysed_data)
            if strcmp(p.Results.save_graphs, 'yes')
                saveas(gcf, [p.Results.out_path, 'MBF spectrum ', ax{ax_num},...
                    ' axis on ', datestr(spectrum_data.data.time)], 'png')
            end %if
        catch me_spectrum
            disp(['Problem with spectrum ', ax{ax_num}, ' axis data'])
            disp(me_spectrum.message)
        end %try
    end %if
    clear spectrum_files spectrum_data
end %for
