function output = BPM_FR_get_data_XY_only(bpm_list)
% Captures 2048 turns of data

for n = 1:length(bpm_list)
    bpm_name = bpm_list{n};
    bpm_label = regexprep(bpm_name, '-', '_');
    for tk = 1:10
        try
            BPM_data_temp = get_variable({[bpm_name, ':FR:WFX'];[bpm_name, ':FR:WFY'];});
            output.(bpm_label).X = BPM_data_temp(1, :);
            output.(bpm_label).Y = BPM_data_temp(2, :);
            fprintf('.')
            break
        catch
            disp(['Failed to get BPM Free run data for ', bpm_name])
        end %try
    end %for
end %for

