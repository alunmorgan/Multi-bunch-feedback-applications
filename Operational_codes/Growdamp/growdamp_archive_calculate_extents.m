function extents = growdamp_archive_calculate_extents(input_data)

extents = struct;
for ke = 1:length (input_data)
    data_field_names = fieldnames(input_data{ke});
    for haw = 1:length(data_field_names)
        if ~isfield(extents, data_field_names{haw})
            % initialisation
            if strcmp(data_field_names{haw}, 'time')
                extents.(data_field_names{haw}){1} = datenum(input_data{ke}.(data_field_names{haw}));
                extents.(data_field_names{haw}){2} = datenum(input_data{ke}.(data_field_names{haw}));
            elseif isnumeric(input_data{ke}.(data_field_names{haw}))
                if length(input_data{ke}.(data_field_names{haw})) ==1
                    extents.(data_field_names{haw}){1} = input_data{ke}.(data_field_names{haw});
                    extents.(data_field_names{haw}){2} = input_data{ke}.(data_field_names{haw});
                end %if
            end %if
        else
            if strcmp(data_field_names{haw}, 'time')
                extents.(data_field_names{haw}){1} = max([extents.(data_field_names{haw}){1},...
                    datenum(input_data{ke}.(data_field_names{haw}))]);
                extents.(data_field_names{haw}){2} = min([extents.(data_field_names{haw}){2},...
                    datenum(input_data{ke}.(data_field_names{haw}))]);
            elseif isnumeric(input_data{ke}.(data_field_names{haw}))
                if length(input_data{ke}.(data_field_names{haw})) ==1
                    extents.(data_field_names{haw}){1} = max([extents.(data_field_names{haw}){1},...
                        input_data{ke}.(data_field_names{haw})]);
                    extents.(data_field_names{haw}){2} = min([extents.(data_field_names{haw}){2},...
                        input_data{ke}.(data_field_names{haw})]);
                end %if
            end %if
        end %if
    end %for
end %for

