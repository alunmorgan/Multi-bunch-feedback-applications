function output = get_BPM_TbT_data

n_bpms = 173;

BPM_TbT_data = NaN(n_bpms, 3);
for n=1:n_bpms
    BPM_name = fa_id2name(n);
    BPM_data_temp = lcaGet({[BPM_name, ':TT:WFS']; ...
        [BPM_name, ':TT:WFX'];...
        [BPM_name, ':TT:WFY']});
    
    BPM_TbT_data(n, 1:size(BPM_data_temp,1),1:size(BPM_data_temp,2)) = BPM_data_temp;
end %for

for n=1:n_bpms
    bpm_name = regexprep(fa_id2name(n), '-', '_');
    output.(bpm_name).I = squeeze(BPM_TbT_data(n, 1, :));
    output.(bpm_name).X = squeeze(BPM_TbT_data(n, 2, :));
    output.(bpm_name).Y = squeeze(BPM_TbT_data(n, 3, :));
end

