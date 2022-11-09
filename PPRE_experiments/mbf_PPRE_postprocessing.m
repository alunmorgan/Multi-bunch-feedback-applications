function data_out = mbf_PPRE_postprocessing(PPRE_data)

for i = 1:length(PPRE_data.scan)
    data_out.emittance_x(i) = PPRE_data.scan{i}.emittance.hemit;
    data_out.emittance_y(i) = PPRE_data.scan{i}.emittance.veimt;
end %for
