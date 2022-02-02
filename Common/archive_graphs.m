function archive_graphs(root_string, metadata, graph_handles)
% Saves the requested graphs in the given filename in a location
% detemined by the time_value.
% The relavent folder structure will be generated.
%
%   Args:
%       root_string (str):
%       data (struct): original captured meta data
%       graph_handles
% Example: archive_graphs(root_string, data, graph_handles)

% Generating the required directory structure.
tree_gen(root_string, metadata.time);

% construct filename and add it to the structure
metadata.filename = construct_datastamped_filename(metadata.base_name, metadata.time);

mth = metadata.time(2);
dy = metadata.time(3);
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

if nargin > 3
    for heaq = 1:length(graph_handles)
        if ishandle(graph_handles(heaq))
            graph_save_name = fullfile(root_string, num2str(metadata.time(1)), mth, dy, metadata.filename);
            saveas(graph_handles(heaq), [graph_save_name, '_figure_', num2str(heaq), '.png'])
            saveas(graph_handles(heaq), [graph_save_name, '_figure_', num2str(heaq), '.fig'])
        end %if
    end %for
end %i