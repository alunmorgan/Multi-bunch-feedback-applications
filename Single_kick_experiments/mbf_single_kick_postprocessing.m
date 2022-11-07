function single_kick_pp = mbf_single_kick_postprocessing(single_kick)

if isfield(single_kick, 'gain_scan')
    for i = 1:length(single_kick.gain_scan)
        used_bpms = fieldnames(single_kick.gain_scan{i}.bpm_data);
        if i == 1
            single_kick_pp.used_bpms = used_bpms;
        end %if
        for kds = 1:length(used_bpms)
            single_kick_pp.beam_oscillation_x_gain_scan(i, kds) = std(single_kick.gain_scan{i}.bpm_data.(used_bpms{kds}).X);
            single_kick_pp.beam_oscillation_y_gain_scan(i, kds) = std(single_kick.gain_scan{i}.bpm_data.(used_bpms{kds}).Y);
        end %for
    end %for
end %if

if isfield(single_kick, 'f_scan')
    for i = 1:length(single_kick.f_scan)
        used_bpms = fieldnames(single_kick.f_scan{i}.bpm_data);
        if i == 1
            single_kick_pp.used_bpms = used_bpms;
        end %if
        for kds = 1:length(used_bpms)
            single_kick_pp.beam_oscillation_x_f_scan(i, kds) = std(single_kick.f_scan{i}.bpm_data.(used_bpms{kds}).X);
            single_kick_pp.beam_oscillation_y_f_scan(i, kds) = std(single_kick.f_scan{i}.bpm_data.(used_bpms{kds}).Y);
        end %for
    end %for
end %if

if isfield(single_kick, 'bpm_TbT_data')
     used_bpms = fieldnames(single_kick.bpm_TbT_data);
    for kds = 1:length(used_bpms)
        single_kick_pp.beam_oscillation_x(kds) = std(single_kick.bpm_TbT_data.(used_bpms{kds}).X);
        single_kick_pp.beam_oscillation_y(kds) = std(single_kick.bpm_TbT_data.(used_bpms{kds}).Y);
    end %for
end %if

if isfield(single_kick, 'bpm_FT_data')
     used_bpms = fieldnames(single_kick.bpm_FT_data);
    for kds = 1:length(used_bpms)
        single_kick_pp.beam_oscillation_x(kds) = std(single_kick.bpm_FT_data.(used_bpms{kds}).X);
        single_kick_pp.beam_oscillation_y(kds) = std(single_kick.bpm_FT_data.(used_bpms{kds}).Y);
    end %for
end %if