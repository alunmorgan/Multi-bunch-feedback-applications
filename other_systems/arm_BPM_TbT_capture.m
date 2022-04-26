function arm_BPM_TbT_capture

BPM_names = fa_id2name(1:173);
for n = length(BPM_names)
    lcaput([BPM_names, ':TT:ARM'],1)
end %for
