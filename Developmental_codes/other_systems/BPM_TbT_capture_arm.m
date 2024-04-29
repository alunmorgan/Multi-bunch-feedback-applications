function arm_BPM_TbT_capture(bpm_list)


for n = length(bpm_list):-1:1
    BPM_name = bpm_list{n};
    BPM_names{n, 1} = [BPM_name, ':TT:ARM'];
end %for
set_variable(BPM_names, 1)

