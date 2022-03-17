function output = get_BPM_SA_data

n_samples = 30;
n_bpms = 173;

BPM_SA_data = NaN(n_bpms, 8, n_samples);
for jsp = 1:n_samples
    for n=1:n_bpms
        BPM_name = fa_id2name(n);
        BPM_data_temp = lcaGet({[BPM_name, ':SA:X']; ...
            [BPM_name, ':SA:Y'];...
            [BPM_name, ':SA:Q'];...
            [BPM_name, ':SA:CURRENT'];...
            [BPM_name, ':SA:A'];...
            [BPM_name, ':SA:B'];...
            [BPM_name, ':SA:C'];...
            [BPM_name, ':SA:D']});
        
        BPM_SA_data(n, 1:size(BPM_data_temp,1),jsp) = BPM_data_temp;
    end %for
end %for

for n=1:n_bpms
    bpm_name = regexprep(fa_id2name(n), '-', '_');
output.(bpm_name).X = squeeze(BPM_SA_data(n, 1, :));
output.(bpm_name).Y = squeeze(BPM_SA_data(n, 2, :));
output.(bpm_name).Q = squeeze(BPM_SA_data(n, 3, :));
output.(bpm_name).CURRENT = squeeze(BPM_SA_data(n, 4, :));
output.(bpm_name).A = squeeze(BPM_SA_data(n, 5, :));
output.(bpm_name).B = squeeze(BPM_SA_data(n, 6, :));
output.(bpm_name).C = squeeze(BPM_SA_data(n, 7, :));
output.(bpm_name).D = squeeze(BPM_SA_data(n, 8, :));
end

