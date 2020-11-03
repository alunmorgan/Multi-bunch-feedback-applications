function [a ,dir_paths] =dir_list_gen_tree(root_dir, type, quiet)
% finds files of the requested type in current folder and all subfolders
% ignores hidden folders
% if one ouptput is given then the absolute paths are returned.
% if two output are given then the flien names and directory paths are
% returned separately.
%
% Example: [a dir_paths] =dir_list_gen_tree(root_dir, 'png', 1)
    
if nargin < 3
    quiet = 0;
end

% setting the file slash type
slash = filesep;
if strcmp(root_dir(end),slash) == 1 & strcmp(root_dir(end-1),':')==0
    root_dir = root_dir(1:end-1);
end

% returns a list of files in the current directory
[full_name]=dir_list_gen(root_dir,type, quiet);
sub_dir = sub_directories(root_dir);
if isempty(full_name) == 1 && isempty(sub_dir) == 1
    a = {};
    dir_paths = {};
    return
end

if isempty(sub_dir) == 0
    for sejh = 1:length(sub_dir)
        sub_dir_path = [root_dir slash sub_dir{sejh}];
        % check if there is substructure
        if isempty(sub_directories(root_dir))==0
            %         if so recursively call itself
            full_name_sub = dir_list_gen_tree(sub_dir_path,type, quiet);
        end
        if isempty(full_name_sub) == 0 
            if isempty(full_name) == 0 
            full_name = cat(1,full_name,full_name_sub);
            else
                full_name = full_name_sub;
            end
        end
    end
end
if isempty(full_name) == 1
   a = {};
   dir_paths = {};
    return 
end
dir_paths = cell(size(full_name,1));
f_names = cell(size(full_name,1));
for pao =1:size(full_name,1)
    nmd = full_name{pao};
    ks = find(nmd == slash,1,'last');
    dir_paths{pao} = nmd(1:ks);
    f_names{pao} = nmd(ks+1:end);
end
dir_paths = dir_paths';
f_names = f_names';
if nargout == 1
    % making the file path absolute
    a = full_name;
elseif nargout == 2
    a = f_names;
else
    error('Wrong number of outputs (should be 1 or 2)')
end

