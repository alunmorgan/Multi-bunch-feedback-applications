function [a ,dir_paths] =dir_list_gen_tree(root_dir, type, quiet)
% finds files of the requested type in current folder and all subfolders
% ignores hidden folders
% if one ouptput is given then the absolute paths are returned.
% if two output are given then the flien names and directory paths are
% returned separately.
%
% Example: [a dir_paths] =dir_list_gen_tree(root_dir, 'png', 1)

a = {};
dir_paths = {};


if nargin < 3
    quiet = 0;
end

if strcmp(root_dir(end), filesep) == 1 & strcmp(root_dir(end-1),':')==0
    root_dir = root_dir(1:end-1);
end %if

% returns a list of files of the requested type in the current directory.
full_names = dir_list_gen(root_dir,type, quiet);
% retruns a list of directories in the current directory.
[sub_dir,~] = dir_list_gen(root_dir, 'dirs', quiet);


if isempty(full_names) == 1 && isempty(sub_dir) == 1
    return
end %if

if isempty(sub_dir) == 0
    for sejh = 1:length(sub_dir)
        sub_dir_path = fullfile(root_dir, sub_dir{sejh});
        % recursively call itself
        full_names_sub = dir_list_gen_tree(sub_dir_path, type, quiet);
        if isempty(full_names_sub) == 0
            if isempty(full_names) == 0
                full_names = cat(1,full_names, full_names_sub);
            else
                full_names = full_names_sub;
            end %if
        end %if
    end %for
end %if

if isempty(full_names) == 1
    return
end %if

dir_paths = cell(size(full_names,1));
f_names = cell(size(full_names,1));
for pao =1:size(full_names,1)
    nmd = full_names{pao};
    ks = find(nmd == filesep,1,'last');
    dir_paths{pao} = nmd(1:ks);
    f_names{pao} = nmd(ks+1:end);
end %for
dir_paths = dir_paths';
f_names = f_names';
if nargout == 1
    % making the file path absolute
    a = full_names;
elseif nargout == 2
    a = f_names;
else
    error('Wrong number of outputs (should be 1 or 2)')
end

