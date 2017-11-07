function mbf_make_index(app, ax)

[root_string, ~, ~] = mbf_system_config;

if ~strcmp(app, 'Growdamp') && ~strcmp(app, 'Bunch_motion') ...
        && ~strcmp(app, 'Modescan') && ~strcmp(app, 'Spectrum') ...
        && ~strcmp(app, 'LO_scan') && ~strcmp(app, 'system_phase_scan') ...
        && ~strcmp(app, 'clock_phase_scan')
    error('mbf_make_index: No valid application given (Growdamp, Bunch_motion, Modescan, Spectrum, LO_scan, system_phase_scan, clock_phase_scan)')
end %if
if nargin < 2
    ax = '';
    if strcmp(app, 'Growdamp') || strcmp(app, 'Modescan') || strcmp(app, 'Spectrum')
        error('An axis needs to be specified')
    end %if
end %if


if strcmp(app, 'Bunch_motion') || strcmp(app, 'LO_scan') || ...
        strcmp(app, 'system_phase_scan') || strcmp(app, 'clock_phase_scan')
    index_name = 'index';
    filter_name = app;
else
    if strcmpi(ax, 'x')
        index_name = 'x_axis_index';
        filter_name = [app, '_x_axis'];
    elseif  strcmpi(ax, 'y')
        index_name = 'y_axis_index';
        filter_name = [app, '_y_axis'];
    elseif strcmpi(ax, 's')
        index_name = 's_axis_index';
        filter_name = [app, '_s_axis'];
    else
        error('mbf_make_index: No valid axis given (should be x, y or s)')
    end %if
end %if
tic
datasets = {};
for nes = 1:length(root_string)
    sets_temp = dir_list_gen_tree(root_string{nes}, '.mat', 1);
    datasets = cat(1, datasets, sets_temp);
end %for
datasets = datasets(2:end);
wanted_datasets_type = datasets(find_position_in_cell_lst(strfind(datasets, filter_name)));
disp(['Creating lookup index for ',app, ' ' ax])
if isempty(wanted_datasets_type)
    disp('No files to index')
else
    parfor kse = 1:length(wanted_datasets_type)
        temp = load(wanted_datasets_type{kse});
        data_name = fieldnames(temp);
        % Although the code saves eveything in 'data', older datasets have
        % a variety of names.
        if strcmp(data_name{1}, 'data') || ...
           strcmp(data_name{1}, 'growdamp') || ...
           strcmp(data_name{1}, 'what_to_save')
            file_time{kse} = temp.(data_name{1}).time;
            file_name{kse} = wanted_datasets_type{kse};
            ok(kse) = 1;
         else
%             disp(fieldnames(temp))
            ok(kse) = 0;
        end %if
    end %parfor
    file_index = cat(1, file_name(ok==1), file_time(ok==1));
    toc
    save(fullfile(root_string{1}, [app, '_', index_name]), 'file_index')
end %if