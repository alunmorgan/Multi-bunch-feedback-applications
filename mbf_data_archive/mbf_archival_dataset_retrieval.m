function unpacked_data = mbf_archival_dataset_retrieval(filter_name, date_range,...
    varargin)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
%
% Args:
%       filter_name(str): Name of the file to select for
%                         Growdamp_x_axis, Growdamp_y_axis, Growdamp_s_axis
%
%       date_range (pair of timestamps): The range of time to extract.
%       bypass_index (str) : 'no' for use the pregnerated index (much faster)
%                            'yes' for work things out from the file metatdata.
%                            the default is 'no'.
%
% Returns:
%       unpacked_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_growdamp_archival_retrieval('x', [datetime(2023, 1, 1), datetime("now")])

default_bypass_index = 'no';
default_metadata_only_index = 'no';
boolean_string = {'yes', 'no'};
p = inputParser;
addRequired(p, 'filter_name', @ischar);
addRequired(p, 'date_range');
addParameter(p, 'bypass_index', default_bypass_index, @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', default_metadata_only_index, @(x) any(validatestring(x, boolean_string)));

parse(p,filter_name, date_range, varargin{:});

% Getting the desired system setup parameters.
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};
%TEMP OVERRIDE
root_string = '/home/afdm76/MBF_loopback_test_data/';

index_name = [filter_name, '_index'];

if strcmp(p.Results.bypass_index, 'no')
    load(fullfile(root_string, index_name), 'file_index')
    % Some error in the file index construction this just removes the unwanted
    % empty entries.
    ck1 = 1;
    ck2 = 1;
    for jrs = 1:size(file_index, 2)
        if ~isempty(file_index{1,jrs})
            test{1,ck1} = file_index{1,jrs};
            ck1 = ck1 +1;
        end %if
    end %for
    for jrs = 1:size(file_index, 2)
        if ~isempty(file_index{2,jrs})
            test{2,ck2} = file_index{2,jrs};
            ck2 = ck2 +1;
        end %if
    end %for
    file_index = test;
    capture_times = cellfun(@datetime, file_index(2,:));
    a = find(capture_times > date_range(1));
    b = find(capture_times <= date_range(2));
    wanted_datasets = file_index(1,(intersect(a,b)));
    disp('')
else
    disp('Bypassing index. This will be slower but is useful if the index is damaged and cannot be imediately regenerated.')
    datasets = dir_list_gen_tree(root_string, '.mat', 1);
    wanted_datasets_type = datasets(find_position_in_cell_lst(strfind(datasets, filter_name)));
    % removing the index file
    wanted_datasets_type(find_position_in_cell_lst(strfind(wanted_datasets_type, index_name))) = [];
    % Prefiltering on folder structure so that the code stays fast as more data
    % is added to the data store.
    tunc = regexprep(wanted_datasets_type, root_string, '');
    for ha = length(tunc):-1:1
        ind = strfind(tunc{ha}, filesep);
        year = str2double(tunc{ha}(1:ind(1)-1));
        month = str2double(tunc{ha}(ind(1)+1: ind(2)-1));
        day = str2double(tunc{ha}(ind(2)+1: ind(3)-1));
        folder_dates(ha) = datetime(year, month, day);
    end %for
    a = find(folder_dates >= floor(date_range(1)) & folder_dates <= floor(date_range(2)) + 1);
    b = find(folder_dates <= floor(date_range(2)) + 1);
    wanted_datasets_type_prefiltered = wanted_datasets_type(intersect(a,b));
    in_time = zeros(length(wanted_datasets_type_prefiltered),1);
    for kse = 1:length(wanted_datasets_type_prefiltered)
        temp = load(wanted_datasets_type_prefiltered{kse});
        file_time = temp.data.time;
        clear temp
        if datetime(file_time) >= date_range(1) && datetime(file_time) <= date_range(2)
            in_time(kse) = 1;
        end %if
        fprintf('.')
    end %for
    fprintf('\n')
    wanted_datasets = wanted_datasets_type_prefiltered(in_time == 1);
end %if

requested_data = cell(length(wanted_datasets),1);
for jes = 1:length(wanted_datasets)
    try
    temp = load(wanted_datasets{jes});
    catch
        [~, corrupt_file, ~] = fileparts(wanted_datasets{jes});
        disp(['skipping corrupt file(', corrupt_file, ')'])
        continue
    end %try
    data_name = fieldnames(temp);
    % Although the code saves eveything in 'data', older datasets have
    % a variety of names.
    if strcmp(data_name{1}, 'data') || ...
            strcmp(data_name{1}, 'growdamp') || ...
            strcmp(data_name{1}, 'what_to_save')
        requested_data{jes} = temp.(data_name{1});
    end %if
    clear temp
end %for

%There was some variation in the use of field names. This regularises them to
%the current standard.
metadata_conditioned_data = condition_mbf_metadata(requested_data);
conditioned_data = condition_mbf_data(metadata_conditioned_data);
%expand old data sweeps so that each data entry has only one
%measurement.
if contains(filter_name, 'Growdamp')
unpacked_data = unpack_old_growdamp_sweeps(conditioned_data);
else
    unpacked_data = conditioned_data;
end %if
if strcmp(p.Results.metadata_only, 'yes')
    for nxd = 1:length(unpacked_data)
        unpacked_data{nxd} = rmfield(unpacked_data{nxd}, 'data');
    end %for
end %if