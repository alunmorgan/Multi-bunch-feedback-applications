function output = get_BPM_TbT_data_XY_only(nbpms, capture_length)


for n = 1:length(nbpms)
    bpm_name = fa_id2name(nbpms(n));
    bpm_label = regexprep(bpm_name, '-', '_');
    for tk = 1:10
        try
            BPM_data_temp = get_variable({[bpm_name, ':TT:WFX'];[bpm_name, ':TT:WFY'];});
            output.(bpm_label).X = BPM_data_temp(1, 1:capture_length);
            output.(bpm_label).Y = BPM_data_temp(2, 1:capture_length);
            break
        catch
            disp(['Failed to get BPM TbT data for ', bpm_name])
        end %try
    end %while
end %for
