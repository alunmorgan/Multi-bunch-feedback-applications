function conditioned_data = growdamp_archive_data_conditioning(data_slice)

field_nms = fieldnames(data_slice);
conditioned_data = struct;

for kef = 1:length(field_nms)
    % This section is to deal with variations in data naming
    % and structuring over the years.
    if strcmp(field_nms{kef}, 'I_bpm')
        conditioned_data.('current') = data_slice.('I_bpm');
    elseif strcmp(field_nms{kef}, 'fill')
        conditioned_data.('fill_pattern') = data_slice.('fill');
    elseif strcmp(field_nms{kef}, 'id')
        conditioned_data.('wiggler_field_I12') = data_slice.('id').('i12field');
        conditioned_data.('wiggler_field_I15') = data_slice.('id').('i15field');
    elseif strcmp(field_nms{kef}, 'life')
        conditioned_data.('beam_lifetime') = data_slice.('life').('bpm').('life300sec');
    elseif strcmp(field_nms{kef}, 'RFread')
        conditioned_data.('cavity1_voltage') = data_slice.('RFread');
        conditioned_data.('cavity2_voltage') = data_slice.('RFread');
    else
        conditioned_data.(field_nms{kef})= data_slice.(field_nms{kef});   
    end %if
end %for
