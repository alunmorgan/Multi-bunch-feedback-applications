function visualise_latest_bbbfe_results(varargin)

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

files = dir_list_gen_tree(root_path{1}, '.mat', 1);

clock_phase_x_files = files(contains(files, 'clock_phase_scan_X'));
clock_phase_y_files = files(contains(files, 'clock_phase_scan_Y'));
clock_phase_s_files = files(contains(files, 'clock_phase_scan_S'));

system_phase_x_files = files(contains(files, 'system_phase_scan_X'));
system_phase_y_files = files(contains(files, 'system_phase_scan_Y'));
system_phase_s_files = files(contains(files, 'system_phase_scan_S'));

doris_phase_files = files(contains(files, 'doris_phase_scan'));


if ~isempty(clock_phase_x_files)
    try
        clock_phase_x = load(clock_phase_x_files{end},'data');
        BBBFE_clock_phase_scan_plotting( 'X', clock_phase_x.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE clock phase sweep X axis on ', datestr(clock_phase_x.data.time)], 'png')
        end %if
    catch
        disp('Problem with clock_phase X axis data')
    end %try
end %if
if ~isempty(clock_phase_y_files)
    try
        clock_phase_y = load(clock_phase_y_files{end},'data');
        BBBFE_clock_phase_scan_plotting( 'Y', clock_phase_y.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE clock phase sweep Y axis on ', datestr(clock_phase_y.data.time)], 'png')
        end %if
    catch
        disp('Problem with clock_phase Y axis data')
    end %try
end %if
if ~isempty(clock_phase_s_files)
    try
        clock_phase_s = load(clock_phase_s_files{end},'data');
        BBBFE_clock_phase_scan_plotting( 'S', clock_phase_s.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE clock phase sweep S axis on ', datestr(clock_phase_s.data.time)], 'png')
        end %if
    catch
        disp('Problem with clock_phase S axis data')
    end %try
end %if

if ~isempty(system_phase_x_files)
    try
        system_phase_x = load(system_phase_x_files{end},'data');
        BBBFE_system_phase_scan_plotting('X', system_phase_x.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE system phase sweep X axis on ', datestr(system_phase_x.data.time)], 'png')
        end %if
    catch
        disp('Problem with system_phase X axis data')
    end %try
end %if
if ~isempty(system_phase_y_files)
    try
        system_phase_y = load(system_phase_y_files{end},'data');
        BBBFE_system_phase_scan_plotting('Y', system_phase_y.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE system phase sweep Y axis on ', datestr(system_phase_y.data.time)], 'png')
        end %if
    catch
        disp('Problem with system_phase Y axis data')
    end %try
end %if
if ~isempty(system_phase_s_files)
    try
        system_phase_s = load(system_phase_s_files{end},'data');
        BBBFE_system_phase_scan_plotting('S', system_phase_s.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'BBBFE system phase sweep S axis on ', datestr(system_phase_s.data.time)], 'png')
        end %if
    catch
        disp('Problem with system_phase S axis data')
    end %try
end %if
if ~isempty(doris_phase_files)
    try
        doris_phase = load(doris_phase_files{end},'data');
        DORIS_phase_scan_plotting(doris_phase.data)
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'DORIS phase sweep on ', datestr(doris_phase.data.time)], 'png')
        end %if
    catch
        disp('Problem with doris phase data')
    end %try
end %if

