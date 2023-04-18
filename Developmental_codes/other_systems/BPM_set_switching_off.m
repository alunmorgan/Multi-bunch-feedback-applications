function BPM_set_switching_off(nbpms)


for n = 1:length(nbpms)
    BPM_name = fa_id2name(nbpms(n));
    lcaPut([BPM_name, ':CF:AUTOSW_S'], 'Manual');
end %for
