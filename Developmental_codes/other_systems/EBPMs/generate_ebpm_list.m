function ebpm_list = generate_ebpm_list
ebpm_list ={};
for cell = 1:24
    cell_name = compose("%02u", cell);
    for position = 1:7
        ebpm_list{end +1} = strcat('SR',cell_name,'C-DI-EBPM-0',num2str(position));
    end
end