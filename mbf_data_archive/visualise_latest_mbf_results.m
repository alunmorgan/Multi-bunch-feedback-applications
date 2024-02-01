function visualise_latest_mbf_results(varargin)

[root_path, harmonic_number, ~, ~] = mbf_system_config;


defaultOverrides = [NaN, NaN];
defaultAnalysisSetting = 0;
defaultLengthAveraging = 20;
defaultDebug = 0;
defaultDebugModes = 1:harmonic_number;
defaultKeepDebugGraphs = 0;
defaultGrowdamp_plotMode = 'neg';
default_result_type = 'standard';

p = inputParser;
validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
addOptional(p,'overrides',defaultOverrides);
addParameter(p,'advanced_fitting',defaultAnalysisSetting, @isnumeric);
addParameter(p,'length_averaging',defaultLengthAveraging, validScalarPosNum);
addParameter(p,'debug',defaultDebug, @isnumeric);
addParameter(p,'debug_modes',defaultDebugModes);
addParameter(p,'keep_debug_graphs',defaultKeepDebugGraphs, @isnumeric);
addParameter(p,'growdamp_plot_mode',defaultGrowdamp_plotMode);
addParameter(p,'result_type',default_result_type);

parse(p,varargin{:});


files = dir_list_gen_tree(root_path{1}, '.mat', 1);

if strcmp(p.Results.result_type, 'standard')
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
            [poly_data_x, frequency_shifts_x] = mbf_growdamp_analysis(growdamp_x.data, ...
                'debug', p.Results.debug, 'debug_modes', p.Results.debug_modes, 'keep_debug_graphs', p.Results.keep_debug_graphs);
            mbf_growdamp_plot_summary(poly_data_x, frequency_shifts_x, growdamp_x.data,...
                'outputs', 'both', 'plot_mode', p.Results.growdamp_plot_mode)
        catch
            disp('Problem with growdamp X axis data')
        end %try
    end %if
    if ~isempty(growdamp_y_files)
        try
            growdamp_y = load(growdamp_y_files{end},'data');
            [poly_data_y, frequency_shifts_y] = mbf_growdamp_analysis(growdamp_y.data,...
                'debug', p.Results.debug, 'debug_modes', p.Results.debug_modes, 'keep_debug_graphs', p.Results.keep_debug_graphs);
            mbf_growdamp_plot_summary(poly_data_y, frequency_shifts_y, growdamp_y.data,...
                'outputs', 'both', 'plot_mode', p.Results.growdamp_plot_mode)
        catch
            disp('Problem with growdamp Y axis data')
        end %try
    end %if
    if ~isempty(growdamp_s_files)
        try
            growdamp_s = load(growdamp_s_files{end},'data');
            [poly_data_s, frequency_shifts_s] = mbf_growdamp_analysis(growdamp_s.data,...
                'debug', p.Results.debug, 'debug_modes', p.Results.debug_modes, 'keep_debug_graphs', p.Results.keep_debug_graphs);
            mbf_growdamp_plot_summary(poly_data_s, frequency_shifts_s, growdamp_s.data,...
                'outputs', 'both', 'plot_mode', p.Results.growdamp_plot_mode)
        catch
            disp('Problem with growdamp S axis data')
        end %try
    end %if

    if ~isempty(spectrum_x_files)
        try
            spectrum_x = load(spectrum_x_files{end},'data');
            analysed_data_x = mbf_spectrum_analysis(spectrum_x.data);
            mbf_spectrum_plotting(analysed_data_x, spectrum_x.data)
        catch
            disp('Problem with spectrum X axis data')
        end %try
    end %if
    if ~isempty(spectrum_y_files)
        try
            spectrum_y = load(spectrum_y_files{end},'data');
            analysed_data_y = mbf_spectrum_analysis(spectrum_y.data);
            mbf_spectrum_plotting(analysed_data_y, spectrum_y.data)
        catch
            disp('Problem with spectrum Y axis data')
        end %try
    end %if
    if ~isempty(spectrum_s_files)
        try
            spectrum_s = load(spectrum_s_files{end},'data');
            analysed_data_s = mbf_spectrum_analysis(spectrum_s.data);
            mbf_spectrum_plotting(analysed_data_s, spectrum_s.data)
        catch
            disp('Problem with spectrum S axis data')
        end %try
    end %if



elseif strcmp(p.Results.result_type, 'frontend')

    frontend_system_phase_x_files = files(contains(files, 'system_phase_scan_X'));
    frontend_system_phase_y_files = files(contains(files, 'system_phase_scan_Y'));
    frontend_system_phase_s_files = files(contains(files, 'system_phase_scan_S'));

    frontend_clock_phase_x_files = files(contains(files, 'clock_phase_scan_X'));
    frontend_clock_phase_y_files = files(contains(files, 'clock_phase_scan_Y'));
    frontend_clock_phase_s_files = files(contains(files, 'clock_phase_scan_S'));

    if ~isempty(frontend_system_phase_x_files)
        try
            frontend_system_phase_x = load(frontend_system_phase_x_files{end},'data');
            BBBFE_system_phase_scan_plotting('x', frontend_system_phase_x.data)
        catch
            disp('Problem with frontend system phase scan data for x axis')
        end %try
    end %if

    if ~isempty(frontend_system_phase_y_files)
        try
            frontend_system_phase_y = load(frontend_system_phase_y_files{end},'data');
            BBBFE_system_phase_scan_plotting('y', frontend_system_phase_y.data)
        catch
            disp('Problem with frontend system phase scan data for y axis')
        end %try
    end %if

    if ~isempty(frontend_system_phase_s_files)
        try
            frontend_system_phase_s = load(frontend_system_phase_s_files{end},'data');
            BBBFE_system_phase_scan_plotting('s', frontend_system_phase_s.data)
        catch
            disp('Problem with frontend system phase scan data for s axis')
        end %try
    end %if
    if ~isempty(frontend_clock_phase_x_files)
        try
            frontend_clock_phase_x = load(frontend_clock_phase_x_files{end},'data');
            BBBFE_clock_phase_scan_plotting('x', frontend_clock_phase_x.data)
        catch
            disp('Problem with frontend clock phase scan data for x axis')
        end %try
    end %if

    if ~isempty(frontend_clock_phase_y_files)
        try
            frontend_clock_phase_y = load(frontend_clock_phase_y_files{end},'data');
            BBBFE_clock_phase_scan_plotting('y', frontend_clock_phase_y.data)
        catch
            disp('Problem with frontend clock phase scan data for y axis')
        end %try
    end %if

    if ~isempty(frontend_clock_phase_s_files)
        try
            frontend_clock_phase_s = load(frontend_clock_phase_s_files{end},'data');
            BBBFE_clock_phase_scan_plotting('s', frontend_clock_phase_s.data)
        catch
            disp('Problem with frontend clock phase scan data for s axis')
        end %try
    end %if
else
    error('Visualise_results:InputError','Please set the result_type to standard or frontend')
end %if
