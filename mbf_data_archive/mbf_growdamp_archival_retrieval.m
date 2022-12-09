function requested_data = mbf_growdamp_archival_retrieval(ax, date_range, varargin)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
%
% Args:
%       ax (str): The number of the axis (x, y, s)
%       date_range (pair of timestamps): The range of time to extract.
%       bypass_index (int) : 0 for use the pregnerated index (much faster)
%                            1 for work things out from the file metatdata.
%                            the default is 0.
%       metadata_only(
%
% Returns:
%       requested_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_growdamp_archival_retrieval('x', [now-5, now])

p = inputParser;
p.StructExpand = false;
p.CaseSensitive = false;
axis_string = {'x', 'y', 's'};
boolean_string = {'yes', 'no'};

addRequired(p, 'ax', @(x) any(validatestring(x, axis_string)));
addRequired(p, 'date_range');
addParameter(p, 'bypass_index', 'no', @(x) any(validatestring(x, boolean_string)));
addParameter(p, 'metadata_only', 'no', @(x) any(validatestring(x, boolean_string)));

parse(p, ax, date_range, varargin{:});

if strcmp(p.Results.bypass_index, 'yes')
    bypass_index_bool = 1;
else  
    bypass_index_bool = 0;
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
    'bypass_index' ,bypass_index_bool);

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
    if strcmp(metadata_only, 'yes')
        requested_data{jes} = rmfield(requested_data{jes}, 'data');
    end %if
    clear data
end %for