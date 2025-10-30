function data_out = mbf_PPRE_postprocessing(PPRE_data)

 data_out.excitation_gain_axis = PPRE_data.excitation_gain;
 data_out.excitation_frequency_axis = PPRE_data.excitation_frequency;
 data_out.harmonic_axis = PPRE_data.harmonic;
for gd = 1:size(PPRE_data.scan, 1)
    for hum = 1:size(PPRE_data.scan, 2)
        for snf = 1:size(PPRE_data.scan, 3)
            data_out.emittance_x(gd, hum, snf) = PPRE_data.scan{gd, hum, snf}.emittances{1}.hemit;
            data_out.emittance_y(gd, hum, snf) = PPRE_data.scan{gd, hum, snf}.emittances{1}.veimt;
            data_out.beam_sizes_P1(gd, hum, snf) = PPRE_data.scan{gd, hum, snf}.beam_sizes{1}.P1_sigy;
            data_out.beam_sizes_P2(gd, hum, snf) = PPRE_data.scan{gd, hum, snf}.beam_sizes{1}.P2_sigy;
%             data_out.beam_sizes_P1(gd, hum, snf) = PPRE_data.scan{gd, hum, snf}.beam_sizes{1}.P3_sigy;
        end %for
    end %for
end %for
