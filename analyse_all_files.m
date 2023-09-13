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
for jsf = 1:length(d)
    for hes = 1:size(d{jsf},1)
        this_root = regexprep(roots{jsf}, '\\', '\\\');
        output_message = [this_root,' <strong>',names{jsf}, '</strong> \n',d{jsf}(hes).message, ' at line ', num2str(d{jsf}(hes).line), '\n'];
        fprintf(output_message)
    end %for
end %for