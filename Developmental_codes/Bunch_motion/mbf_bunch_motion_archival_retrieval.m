function requested_data = mbf_bunch_motion_archival_retrieval(date_range, varargin)
% Extracts requested data from the data archive between
% the requested times(date_range)
%
% Args:
%       date_range (pair of datetime instances): The range of time to extract.
%       bypass_index (str) : 'no' for use the pregnerated index (much faster)
%                            'yes' for work things out from the file metatdata.
%                            the default is 'no'.
%       metadata_only(str): 'no' return all data
%                            'yes' remove the sample data from the output structure.
%                            the default is 'no'.
% Returns:
%       conditioned_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_bunch_motion_archival_retrieval([now-5, now])


p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
boolean_string = {'yes', 'no'};

addRequired(p, 'date_range');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, date_range, varargin{:});

filter_name = 'Bunch_motion';

requested_data = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index' ,p.Results.bypass_index, 'metadata_only', p.Results.metadata_only);

% if bypass_index == 0
%     load(fullfile(root_string, index_name), 'file_index')
%     datenums = cellfun(@datenum, file_index(2,:));
%     a = find(datenums > date_range(1));
%     b = find(datenums <= date_range(2));
%     wanted_datasets = file_index(1,(intersect(a,b)));
%     disp('')
% else
%     disp('Bypassing index. This will be slower but is useful if the index is damaged and cannot be imediately regenerated.')
%     datasets = dir_list_gen_tree(root_string, '.mat', 1);
%     wanted_datasets_type = datasets(find_position_in_cell_lst(strfind(datasets, filter_name)));
%     % removing the index file
%     wanted_datasets_type(find_position_in_cell_lst(strfind(wanted_datasets_type, index_name))) = [];
%     % Prefiltering on folder structure so that the code stays fast as more data
%     % is added to the data store.
%     tunc = regexprep(wanted_datasets_type, root_string, '');
%     for ha = length(tunc):-1:1
%         ind = strfind(tunc{ha}, filesep);
%         year = str2double(tunc{ha}(1:ind(1)-1));
%         month = str2double(tunc{ha}(ind(1)+1: ind(2)-1));
%         day = str2double(tunc{ha}(ind(2)+1: ind(3)-1));
%         folder_dates(ha) = datenum(year, month, day);
%     end %for
%     a = find(folder_dates >= floor(date_range(1)) & folder_dates <= floor(date_range(2)) + 1);
%     b = find(folder_dates <= floor(date_range(2)) + 1);
%     wanted_datasets_type_prefiltered = wanted_datasets_type(intersect(a,b));
%     in_time = zeros(length(wanted_datasets_type_prefiltered),1);
%     for kse = 1:length(wanted_datasets_type_prefiltered)
%         temp = load(wanted_datasets_type_prefiltered{kse});
%         file_time = temp.data.time;
%         clear temp
%         if datenum(file_time) >= date_range(1) && datenum(file_time) <= date_range(2)
%             in_time(kse) = 1;
%         end %if
%         fprintf('.')
%     end %for
%     fprintf('\n')
%     wanted_datasets = wanted_datasets_type_prefiltered(in_time == 1);
% end %if
% 
% 
% requested_data = cell(length(wanted_datasets),1);
% for jes = 1:length(wanted_datasets)
%     temp = load(wanted_datasets{jes});
%     data_name = fieldnames(temp);
%     if strcmp(data_name{1}, 'data') 
%         requested_data{jes} = temp.(data_name{1});
%     end %if
%     if metadata_only ~= 0
%         requested_data{jes} = rmfield(requested_data{jes}, 'data');
%     end %if
%     clear data
% end %for