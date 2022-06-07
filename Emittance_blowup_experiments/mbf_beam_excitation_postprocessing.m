function emittance_blowup_pp = mbf_beam_excitation_postprocessing(emittance_blowup)

%bpm_number = 163;
%BPM_name = fa_id2name(bpm_number);

for i = 1:length(emittance_blowup.scan)
    used_bpms = fieldnames(emittance_blowup.scan{i}.bpm_data);
    if i == 1
        emittance_blowup_pp.used_bpms = used_bpms;
    end %if
    for kds = 1:length(used_bpms)
        emittance_blowup_pp.beam_oscillation_x(i, kds) = std(emittance_blowup.scan{i}.bpm_data.(used_bpms{kds}).X);
        emittance_blowup_pp.beam_oscillation_y(i, kds) = std(emittance_blowup.scan{i}.bpm_data.(used_bpms{kds}).Y);
    end %for
    emittance_blowup_pp.emittance_x(i) = emittance_blowup.scan{i}.emittance.hemit;
    emittance_blowup_pp.emittance_y(i) = emittance_blowup.scan{i}.emittance.veimt;
end %for
