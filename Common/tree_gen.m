function tree_gen(tree_root,c)
% generates a directory structure using the time vector from clock
% tree_root is where you want the subdirectoires to be placed
% cl is the clock vector

% Adapting to windows or linux paths
if ispc == 1
    slash = '\';
else
    slash = '/';
end

yr = num2str(c(1));
mth = num2str(c(2));
dy = num2str(c(3));

if c(2) < 10
mth = ['0' mth];
end
if c(3) < 10
dy = ['0' dy];
end

% generating directory tree
if exist([tree_root yr slash],'dir') == 0
    system(['mkdir ' tree_root  yr slash]);
end
if exist([tree_root yr slash mth slash],'dir') == 0
    system(['mkdir ' tree_root yr slash mth '/']);
end
if exist([tree_root yr slash mth slash dy slash],'dir') == 0
    system(['mkdir ' tree_root yr slash mth slash dy slash]);
end

