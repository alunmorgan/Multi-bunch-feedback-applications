function save_to_archive(root_string, data)
% Saves the requested variables in the given filename in a location
% detemined by the time_value.
% The relavent folder structure will be generated.
%
% Example: save_to_archive(root_string, what_to_save)

% Generating the required directory structure.
tree_gen(root_string, data.time);

% construct filename and add it to the structure
data.filename = construct_datastamped_filename(data.base_name, data.time);

mth = data.time(2);
dy = data.time(3);
if mth < 10
    mth = ['0' num2str(mth)];
else
    mth = num2str(mth);
end
if dy < 10
    dy = ['0' num2str(dy)];
else
    dy = num2str(dy);
end


save_name = fullfile(root_string, num2str(data.time(1)), mth, dy, ...
    [data.filename '.mat']);
save(save_name, 'data','-v7.3')
% disp(['Data saved simulated:  ',save_name])

disp(['Data saved to:  ',save_name])

index_name = [data.base_name, '_index'];
if exist(fullfile(root_string, [index_name, '.mat']),'file')
    load(fullfile(root_string, [index_name, '.mat']), 'file_index')
    file_index{1, end+1} = save_name;
    file_index{2, end+1} = data.time;
    save(fullfile(root_string, [index_name, '.mat']), 'file_index','-v7.3')
    disp('Index updated')
else
    file_index{1, 1} = save_name;
    file_index{2, 1} = data.time;
    save(fullfile(root_string, [index_name, '.mat']), 'file_index','-v7.3')
    disp('New index file created')
end %if
