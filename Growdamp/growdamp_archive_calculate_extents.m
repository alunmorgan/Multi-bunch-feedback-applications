function extents = growdamp_archive_calculate_extents(input_data)

extents = struct;
for ke = 1:length (input_data)
    data_field_names = fieldnames(input_data{ke});
    
    for haw = 1:length(data_field_names)
        if ~isfield(extents, data_field_names{haw})
            % initialisation
            if isnumeric(input_data{ke}.(data_field_names{haw}))
                extents.(data_field_names{haw}){1} = max(input_data{ke}.(data_field_names{haw}), [],  'omitnan');
                extents.(data_field_names{haw}){2} = min(input_data{ke}.(data_field_names{haw}), [], 'omitnan');
            end %if
            %         else
            %             if isnumeric(input_data{ke}.(data_field_names{haw}))
            %                 extents.(data_field_names{haw}){1} = ...
            %                     max(input_data{ke}.(data_field_names{haw}),...
            %                     extents.(data_field_names{haw}){1}, 'omitnan');
            %                 extents.(data_field_names{haw}){2} = ...
            %                     min(input_data{ke}.(data_field_names{haw}),...
            %                     extents.(data_field_names{haw}){2}, 'omitnan');
        end %if
    end %if
end %for
clear extent_field_name data_field_name
end %for
