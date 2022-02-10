function wanted_datasets = mbf_archival_dataset_retrieval(filter_name, date_range,...
   varargin)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
%
% Args:
%       filter_name(str): Name of the file to select for
%                         Growdamp_x_axis, Growdamp_y_axis, Growdamp_s_axis
%                         
%       date_range (pair of timestamps): The range of time to extract.
%       bypass_index (int) : 0 for use the pregnerated index (much faster)
%                            1 for work things out from the file metatdata.
%                            the default is 0.
%
% Returns:
%       requested_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_growdamp_archival_retrieval('x', [now-5, now])

default_bypass_index = 0;

validScalarPosNum = @(x) isnumeric(x) && isscalar(x) && (x > 0);
p = inputParser;
addRequired(p, 'filter_name', @ischar);
addRequired(p, 'date_range');
addParameter(p, 'bypass_index', default_bypass_index, validScalarPosNum);

parse(p,filter_name, date_range, varargin{:});
bypass_index = p.Results.bypass_index;


% Getting the desired system setup parameters.
[root_string, ~, ~, ~] = mbf_system_config;
root_string = root_string{1};

index_name = [filter_name, '_index'];

if bypass_index == 0
    load(fullfile(root_string, index_name), 'file_index')
    datenums = cellfun(@datenum, file_index(2,:));
    a = find(datenums > date_range(1));
    b = find(datenums <= date_range(2));
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
        folder_dates(ha) = datenum(year, month, day);
    end %for
    a = find(folder_dates >= floor(date_range(1)) & folder_dates <= floor(date_range(2)) + 1);
    b = find(folder_dates <= floor(date_range(2)) + 1);
    wanted_datasets_type_prefiltered = wanted_datasets_type(intersect(a,b));
    in_time = zeros(length(wanted_datasets_type_prefiltered),1);
    for kse = 1:length(wanted_datasets_type_prefiltered)
        temp = load(wanted_datasets_type_prefiltered{kse});
        file_time = temp.data.time;
        clear temp
        if datenum(file_time) >= date_range(1) && datenum(file_time) <= date_range(2)
            in_time(kse) = 1;
        end %if
        fprintf('.')
    end %for
    fprintf('\n')
    wanted_datasets = wanted_datasets_type_prefiltered(in_time == 1);
end %if

