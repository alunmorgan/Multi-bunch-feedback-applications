function output = get_BPM_TbT_data_XY_only(nbpms, capture_length)


BPM_TbT_data = NaN(length(nbpms), 2);
for n = 1:length(nbpms)
    bpm_name = fa_id2name(nbpms(n));
    while 1==1
        tk = 1;
        try
            BPM_data_temp = lcaGet({[bpm_name, ':TT:WFX'];[bpm_name, ':TT:WFY'];});
            break
        catch
            if tk >10
                break
            end %if
            tk = tk +1;
        end %try
    end %while
    bpm_label = regexprep(bpm_name, '-', '_');
    output.(bpm_label).X = BPM_data_temp(1, 1:capture_length);
    output.(bpm_label).Y = BPM_data_temp(2, 1:capture_length);
end %for
