function analyse_all_files(root)
% runs static analysis on all m files in the folder tree at and below root.
%
% Example analyse_all_files(pwd)

a = dir_list_gen_tree(root, 'm',1);
b = checkcode(a);
c = cellfun("isempty", b);
d = b(c==0);
fullnames = a(c==0);
[roots, names, ~] = fileparts(fullnames);
roots = regexprep(roots, root, '');
files_of_interest = {};
for jsf = 1:length(d)
    for hes = 1:size(d{jsf},1)
        this_root = regexprep(roots{jsf}, '\\', '\\\');
        output_message = [this_root,' <strong>',names{jsf}, '</strong> \n',d{jsf}(hes).message, ' at line ', num2str(d{jsf}(hes).line), '\n'];
        fprintf(output_message)
        files_of_interest{end +1} = names{jsf};
    end %for
end %for
files_of_interest = unique(files_of_interest);

for jkds = 1:length(files_of_interest)
    open(files_of_interest{jkds})
end %for