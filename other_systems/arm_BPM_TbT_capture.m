function arm_BPM_TbT_capture

nBPMs = 173;

BPM_names = fa_id2name(1:nBPMs);
for n = 1:nBPMs
    BPM_names{n} = [BPM_names{n}, ':TT:ARM'];
end %for
lcaPut(BPM_names', 1)

