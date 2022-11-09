function output = get_BPM_FT_data_XY_only(nbpms)


BPM_FT_data = NaN(length(nbpms), 2);
for n = 1:length(nbpms)
    BPM_name = fa_id2name(nbpms(n));
    BPM_data_temp = lcaGet({...
        [BPM_name, ':FT:WFX'];...
        [BPM_name, ':FT:WFY'];...
        });
    BPM_FT_data(n, 1:size(BPM_data_temp,1), 1:size(BPM_data_temp,2)) = BPM_data_temp;
end %for

for n=1:length(nbpms)
    bpm_name = regexprep(fa_id2name(nbpms(n)), '-', '_');
    output.(bpm_name).X = squeeze(BPM_FT_data(n, 1, :));
    output.(bpm_name).Y = squeeze(BPM_FT_data(n, 2, :));
end