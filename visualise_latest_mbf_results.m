function visualise_latest_mbf_results(varargin)

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addParameter(p, 'save_graphs', 'no', @(x) any(validatestring(x,boolean_string)));
addParameter(p, 'out_path', NaN);
addParameter(p, 'measurements', {'Growdamp', 'Modescan', 'Spectrum',...
    'system_phase_scan', 'clock_phase_scan'});
addParameter(p, 'axes', {'x', 'y', 's'});
parse(p, varargin{:});

if strcmp(p.Results.save_graphs, 'yes') && any(isnan(p.Results.out_path))
    error(no_path, 'Please provide a path to store the graphs using the out_paths flag.')
end %if

[root_path, ~, ~] = mbf_system_config;
dirs = dir_list_gen_tree(root_path, 'dirs', 1);

%% filter out any directories which don't match the pattern.
t1 = regexp(dirs, '.*[A-Za-z]+/\d\d\d\d/\d\d/\d\d$');
t2 = ones(length(t1), 1);
for hhs = 1:length(t1)
    if isempty(t1{hhs})
        t2(hhs) = 0;
    end %if
end %for
dirs = dirs(t2==1);

test = regexp(dirs, '.*/(\d\d\d\d)/(\d\d)/(\d\d)','tokens');
dates = NaT(length(test),1);
for ks = 1:length(test)
    yr = str2double(test{ks}{1}{1});
    mth = str2double(test{ks}{1}{2});
    dy = str2double(test{ks}{1}{3});
    dates(ks) = datetime(yr, mth, dy);
end %for

% Sort them into most recent first. So as you go through the list the first one
% you find will be the most recent.
[~, I] = sort(dates, 1, 'descend');
dirs = dirs(I);

%% Constructing the list of experiments.
ck = 1;
exp_name = cell(length(p.Results.measurements),1);
for meas_num = 1:length(p.Results.measurements)
    if contains(p.Results.measurements{meas_num}, 'DORIS_phase_scan',...
            'IgnoreCase', true)
        exp_name{ck} = p.Results.measurements{meas_num};
        ck = ck +1;
    else
        for ax_num = 1:length(p.Results.axes)
            ax = p.Results.axes{ax_num};
            exp_name{ck} = [p.Results.measurements{meas_num}, '_', ax];
            ck = ck +1;
        end %for
    end %if
end %for

%% find the most recent of each experiment requested.
files_wanted = struct;
for kse = 1:length(dirs)
    files = dir_list_gen(dirs{kse}, '.mat', 'quiet_flag', 1);
    if isempty(files)
        continue
    end %if
    for bws = 1:length(exp_name)
        if isfield(files_wanted, exp_name{bws})
            continue
        end %if
        temp_files = files(contains(files, exp_name{bws}, 'IgnoreCase', true));
        if isempty(temp_files)
            continue
        end %if
        [~, names, ~] = fileparts(temp_files);
        test = regexp(names, '.*_(\d\d)_(\d\d)_(\d\d\d\d)_(\d\d)-(\d\d)-(\d\d)',...
            'tokens', 'forcecelloutput');
        temp_dates = NaT(length(test),1);
        for jk = 1:length(test)
            yr = str2double(test{jk}{1}{3});
            mth = str2double(test{jk}{1}{2});
            dy = str2double(test{jk}{1}{1});
            hr = str2double(test{jk}{1}{4});
            minit = str2double(test{jk}{1}{5});
            scnd = str2double(test{jk}{1}{6});
            temp_dates(jk) = datetime(yr, mth, dy, hr, minit, scnd);
        end %for
        [~,latest_file_ind] = max(temp_dates);
        files_wanted.(exp_name{bws})  = temp_files{latest_file_ind};
        clear temp_dates names latest_file_ind test temp_files
    end %for
end %for

%% Load and plot each dataset.
for bws = 1:length(exp_name)
    data = load(files_wanted.(exp_name{bws}),'data');
    try
        if contains(exp_name{bws}, 'modescan', 'IgnoreCase',true)
            [data_magnitude, data_phase_x] = mbf_modescan_analysis(data.data);
            mbf_modescan_plotting(data_magnitude, data_phase_x, data.data)
        elseif contains(exp_name{bws}, 'growdamp', 'IgnoreCase',true)
            poly_data = mbf_growdamp_analysis(data.data);
            mbf_growdamp_plot_summary(poly_data, data.data)
        elseif contains(exp_name{bws}, 'spectrum', 'IgnoreCase',true)
            analysed_data = mbf_spectrum_analysis(data.data);
            mbf_spectrum_plotting(data.data, analysed_data)
        elseif contains(exp_name{bws}, 'system_phase_scan', 'IgnoreCase',true)
            BBBFE_system_phase_scan_plotting(data.data)
        elseif contains(exp_name{bws}, 'clock_phase_scan', 'IgnoreCase',true)
            BBBFE_clock_phase_scan_plotting(data.data)
        elseif contains(exp_name{bws}, 'DORIS_phase_scan', 'IgnoreCase',true)
            DORIS_phase_scan_plotting(data.data)
        end %if
        if strcmp(p.Results.save_graphs, 'yes')
            saveas(gcf, [p.Results.out_path, 'MBF ',exp_name{bws}, ...
                ' axis on ', string(data.data.time)], 'png')
        end %if
    catch me
        disp(['Problem with ',exp_name{bws}, ' axis data'])
        disp(me.message)
        disp([me.stack(1).name, ' line ', num2str(me.stack(1).line)])
    end %try
end %if
