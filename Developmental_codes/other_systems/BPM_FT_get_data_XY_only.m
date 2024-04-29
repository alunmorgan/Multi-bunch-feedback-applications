function output = BPM_FT_get_data_XY_only(bpm_list)


BPM_FT_data = NaN(length(bpm_list), 2);
for n = 1:length(bpm_list)
    bpm_name = bpm_list{n};
    bpm_label = regexprep(bpm_name, '-', '_');
    for tk = 1:10
        try
            BPM_data_temp = get_variable({...
                [bpm_name, ':FT:WFX'];...
                [bpm_name, ':FT:WFY'];...
                });
            BPM_FT_data(n, 1:size(BPM_data_temp,1), 1:size(BPM_data_temp,2)) = BPM_data_temp;
            output.(bpm_label).X = squeeze(BPM_data_temp(1, :));
            output.(bpm_label).Y = squeeze(BPM_data_temp(2, :));
            fprintf('.')
            break
        catch
            disp(['Failed to get BPM first turn data for ', bpm_name])
        end %try
    end %for
end %for
