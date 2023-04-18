function data_out = mbf_PPRE_postprocessing(PPRE_data)

if length(PPRE_data.excitation_gain) == length(PPRE_data.scan)
    data_out.scan_axis = PPRE_data.excitation_gain;
    data_out.scan_label = 'Gain';
elseif length(PPRE_data.excitation_frequency) == length(PPRE_data.scan)
    data_out.scan_axis = PPRE_data.excitation_frequency;
    data_out.scan_label = 'Frequency';
elseif length(PPRE_data.harmonic) == length(PPRE_data.scan)
    data_out.scan_axis = PPRE_data.harmonic;
    data_out.scan_label = 'Harmonic';
else
    data_out.scan_axis = 1:length(PPRE_data.scan);
    data_out.scan_label = 'Undefined';
end %if

for i = 1:length(PPRE_data.scan)
    data_out.emittance_x(i) = PPRE_data.scan{i}.emittance{1}.hemit;
    data_out.emittance_y(i) = PPRE_data.scan{i}.emittance{1}.veimt;
    data_out.beam_sizes_P1(i) = PPRE_data.scan{i}.beam_sizes{1}.P1_sigy;
    data_out.beam_sizes_P1(i) = PPRE_data.scan{i}.beam_sizes{1}.P2_sigy;
    data_out.beam_sizes_P1(i) = PPRE_data.scan{i}.beam_sizes{1}.P3_sigy;
end %for
