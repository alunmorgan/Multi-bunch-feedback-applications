function output = get_BPM_FR_data_XY_only(nbpms)
% Captures 2048 turns of data

for n = 1:length(nbpms)
    bpm_name = fa_id2name(nbpms(n));
    while 1==1
        tk = 1;
        try
            BPM_data_temp = lcaGet({[bpm_name, ':FR:WFX'];[bpm_name, ':FR:WFY'];});
            break
        catch
            if tk >10
                break
            end %if
            tk = tk +1;
        end %try
    end %while
    bpm_label = regexprep(bpm_name, '-', '_');
    output.(bpm_label).X = BPM_data_temp(1, :);
    output.(bpm_label).Y = BPM_data_temp(2, :);
end %for

