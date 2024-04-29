function BPM_TbT_capture_setup(bpm_list, capture_length)


for n = 1:length(nbpms)
    BPM_name = bpm_list{n};
    set_variable([BPM_name, ':TT:DELAY_S'], 0);
    set_variable([BPM_name, ':TT:OFFSET_S'], 0);
    set_variable([BPM_name, ':TT:CAPLEN_S'], capture_length); % Turns
    set_variable([BPM_name, ':TT:LENGTH_S'], capture_length); % Turns
end %for
