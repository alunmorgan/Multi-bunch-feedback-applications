function setup_BPM_TbT_capture(nbpms, capture_length)


for n = 1:length(nbpms)
    BPM_name = fa_id2name(nbpms(n));
    set_variable([BPM_name, ':TT:DELAY_S'], 0);
    set_variable([BPM_name, ':TT:OFFSET_S'], 0);
    set_variable([BPM_name, ':TT:CAPLEN_S'], capture_length); % Turns
    set_variable([BPM_name, ':TT:LENGTH_S'], capture_length); % Turns
end %for
