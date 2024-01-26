function arm_BPM_TbT_capture(nbpms)



BPM_names = fa_id2name(nbpms);
for n = 1:length(nbpms)
    BPM_names{n} = [BPM_names{n}, ':TT:ARM'];
end %for
set_variable(BPM_names', 1)

