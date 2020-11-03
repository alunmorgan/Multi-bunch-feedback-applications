function sub_dir = sub_directories(main_dir)
% outputs a list of sub-directories of the input directory
%
% example: sub_dir = sub_directories(main_dir)

%finding the subdirectories
files = dir(main_dir);
lc =length(files);
tk = 1;
inds = NaN(lc,1);
for rn = 1:lc
    if files(rn).isdir == 1
        inds(tk) = rn;
        tk = tk +1;
    end
end
inds(tk:end) = [];
if tk == 1
    tc = 1;   
    folders = files(inds);
    sub_dir = cell(length(folders));
    for tb = 1:length(folders)
        if strcmp(folders(tb).name,'.') ||  strcmp(folders(tb).name,'..')
            % skip the . and .. found on linux systems.
        else
            sub_dir{tc} = folders(tb).name;
            tc = tc + 1;
        end %if
    end %for
    sub_dir(tc:end) = [];
else %if
    sub_dir = {};
end