function requested_data = mbf_growdamp_archival_retrieval(ax, date_range)
% Extracts requested data from the data archive between
% the requested times(date_range), and of the correct type (ax).
%
% Args:
%       ax (str): The number of the axis (x, y, s)
%       date_range (pair of timestamps): The range of time to extract.
%
% Returns:
%       requested_data (cell of structures): The group of requested data
%                                            structures.
%
% Example: mbf_growdamp_archival_archival_retreval('x', [now-5, now])

% Getting the desired system setup parameters.
[root_string, ~, ~] = mbf_system_config;

if strcmpi(ax, 'x')
    filter_name = 'Growdamp_x_axis';
elseif  strcmpi(ax, 'y')
    filter_name = 'Growdamp_y_axis';
elseif strcmpi(ax, 's')
    filter_name = 'Growdamp_s_axis';
else
    error('mbf_growdamp_archival_retrieval: No valid axis given (should be x, y or s)')
end %if

datasets = dir_list_gen_tree(root_string, '.mat', 1);
wanted_datasets_type = datasets(find_position_in_cell_lst(strfind(datasets, filter_name)));

in_time = zeros(length(wanted_datasets_type),1);
for kse = 1:length(wanted_datasets_type)
    load(wanted_datasets_type{kse})
    file_time = data.time;
    if datenum(file_time) >= date_range(1) && datenum(file_time) <= date_range(2)
        in_time(kse) = 1;
    end %if
    fprintf('.')
end %for
fprintf('\n')
wanted_datasets = wanted_datasets_type(in_time == 1);
requested_data = cell(length(wanted_datasets),1);
for jes = 1:length(wanted_datasets)
    load(wanted_datasets{jes})
    requested_data{jes} = data;
    clear data
end %for