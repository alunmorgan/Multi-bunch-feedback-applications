function emittance_blowup_pp = mbf_beam_excitation_postprocessing(emittance_blowup)

%bpm_number = 163;
%BPM_name = fa_id2name(bpm_number);

for i = 1:length(emittance_blowup.scan)
    emittance_blowup_pp.beam_oscillation_x(i) = std(emittance_blowup.scan{i}.bpm_data.SR23C_DI_EBPM_05.X);
    emittance_blowup_pp.beam_oscillation_y(i) = std(emittance_blowup.scan{i}.bpm_data.SR23C_DI_EBPM_05.Y);
    
    emittance_blowup_pp.emittance_x(i) = emittance_blowup.scan{i}.emittance.hemit;
    emittance_blowup_pp.emittance_y(i) = emittance_blowup.scan{i}.emittance.veimt;
end %for
