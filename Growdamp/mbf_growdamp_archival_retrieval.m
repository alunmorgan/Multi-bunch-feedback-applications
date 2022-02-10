function requested_data = mbf_growdamp_archival_retrieval(ax, date_range,...
    bypass_index, metadata_only)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
%
% Args:
%       ax (str): The number of the axis (x, y, s)
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

if nargin < 3
    metadata_only = 0;
elseif nargin == 3
    metadata_only = 0;
end %if


if strcmpi(ax, 'x')
    filter_name = 'Growdamp_x_axis';
elseif  strcmpi(ax, 'y')
    filter_name = 'Growdamp_y_axis';
elseif strcmpi(ax, 's')
    filter_name = 'Growdamp_s_axis';
else
    error('mbf_archival_dataset_retrieval: No valid axis given (should be x, y or s)')
end %if
wanted_datasets = mbf_archival_dataset_retrieval(filter_name, date_range,...
    'bypass_index' ,bypass_index);

requested_data = cell(length(wanted_datasets),1);
for jes = 1:length(wanted_datasets)
    temp = load(wanted_datasets{jes});
    data_name = fieldnames(temp);
    % Although the code saves eveything in 'data', older datasets have
    % a variety of names.
    if strcmp(data_name{1}, 'data') || ...
            strcmp(data_name{1}, 'growdamp') || ...
            strcmp(data_name{1}, 'what_to_save')
        requested_data{jes} = temp.(data_name{1});
    end %if
    if metadata_only ~= 0
        requested_data{jes} = rmfield(requested_data{jes}, 'data');
    end %if
    clear data
end %for