function BPM_set_switching_on(nbpms)


for n = 1:length(nbpms)
    BPM_name = fa_id2name(nbpms(n));
    set_variable([BPM_name, ':CF:AUTOSW_S'], 'Automatic');
end %for
