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
t1 = regexp(dirs, '.*[A-Za-z]+/\d\d\d\d/\d\d/\d\d$');
t2 = ones(length(t1), 1);
for hhs = 1:length(t1)
    if isempty(t1{hhs})
        t2(hhs) = 0;
    end %if
end %for
dirs = dirs(t2==1);

test = regexp(dirs, '.*/(\d\d\d\d)/(\d\d)/(\d\d)','tokens');
for jk = 1:length(test)
    dates(jk) = datetime(str2double(test{jk}{1}{1}), str2double(test{jk}{1}{2}),...
        str2double(test{jk}{1}{3}));
end %for
[~, I] = sort(dates, 2, 'descend');
dirs = dirs(I);

ck = 1;
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

files_wanted = struct;
for kse = 1:length(dirs)
    files = dir_list_gen(dirs{kse}, '.mat', 'quiet_flag', 1);
    if isempty(files)
        continue
    end %if
    for bws = 1:length(exp_name)
        if ~isfield(files_wanted, exp_name{bws})
            temp_files = files(contains(files, exp_name{bws}, 'IgnoreCase', true));
            if ~isempty(temp_files)
                [~, names, ~] = fileparts(temp_files);
                test = regexp(names, '.*_(\d\d)_(\d\d)_(\d\d\d\d)_(\d\d)-(\d\d)-(\d\d)',...
                    'tokens', 'forcecelloutput');
                for jk = 1:length(test)
                    temp_dates(jk) = datetime(str2double(test{jk}{1}{3}),...
                        str2double(test{jk}{1}{2}),...
                        str2double(test{jk}{1}{1}), str2double(test{jk}{1}{4}),...
                        str2double(test{jk}{1}{5}), str2double(test{jk}{1}{6}));
                end %for
                [~,latest_file_ind] = max(temp_dates);
                files_wanted.(exp_name{bws})  = temp_files{latest_file_ind};
                clear temp_dates names latest_file_ind test temp_files
            end %if
        end %if
    end %for
end %for

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
                ' axis on ', datestr(data.data.time)], 'png')
        end %if
    catch me
        disp(['Problem with ',exp_name{bws}, ' axis data'])
        disp(me.message)
        disp([me.stack(1).name, ' line ', num2str(me.stack(1).line)])
    end %try
end %if



%    if ~isempty(frontend_system_phase_x_files)
%         try
%             
%         catch
%             disp('Problem with frontend system phase scan data for x axis')
%         end %try
%     end %if
%
%     if ~isempty(frontend_system_phase_y_files)
%         try
%             frontend_system_phase_y = load(frontend_system_phase_y_files{end},'data');
%             BBBFE_system_phase_scan_plotting('y', frontend_system_phase_y.data)
%         catch
%             disp('Problem with frontend system phase scan data for y axis')
%         end %try
%     end %if
%
%     if ~isempty(frontend_system_phase_s_files)
%         try
%             frontend_system_phase_s = load(frontend_system_phase_s_files{end},'data');
%             BBBFE_system_phase_scan_plotting('s', frontend_system_phase_s.data)
%         catch
%             disp('Problem with frontend system phase scan data for s axis')
%         end %try
%     end %if
%     if ~isempty(frontend_clock_phase_x_files)
%         try
%             frontend_clock_phase_x = load(frontend_clock_phase_x_files{end},'data');
%             BBBFE_clock_phase_scan_plotting('x', frontend_clock_phase_x.data)
%         catch
%             disp('Problem with frontend clock phase scan data for x axis')
%         end %try
%     end %if
%
%     if ~isempty(frontend_clock_phase_y_files)
%         try
%             frontend_clock_phase_y = load(frontend_clock_phase_y_files{end},'data');
%             BBBFE_clock_phase_scan_plotting('y', frontend_clock_phase_y.data)
%         catch
%             disp('Problem with frontend clock phase scan data for y axis')
%         end %try
%     end %if
%
%     if ~isempty(frontend_clock_phase_s_files)
%         try
%             frontend_clock_phase_s = load(frontend_clock_phase_s_files{end},'data');
%             BBBFE_clock_phase_scan_plotting('s', frontend_clock_phase_s.data)
%         catch
%             disp('Problem with frontend clock phase scan data for s axis')
%         end %try
%     end %if
% else
%     error('Visualise_results:InputError','Please set the result_type to standard or frontend')
% end %if
