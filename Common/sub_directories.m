function sub_dir = sub_directories(main_dir)
% outputs a list of sub-directories of the input directory
%
% example: sub_dir = sub_directories(main_dir)

sub_dir = {};
%finding the subdirectories
files = dir(main_dir);
lc =length(files);
tk = 1;
for rn = 1:lc
    if files(rn).isdir == 1
        inds(tk) = rn;
        tk = tk +1;
    end
end
if exist('inds','var')
tc = 1;
folders = files(inds);
    for tb = 1:length(folders)
        if strcmp(folders(tb).name,'.') ||  strcmp(folders(tb).name,'..') 
            % skip the . and .. found on linux systems.
        else
        sub_dir{tc} = folders(tb).name;
        tc = tc + 1;
        end
    end
else
    sub_dir = {};
end