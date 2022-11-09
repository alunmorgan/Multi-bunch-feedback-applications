function mbf_PPRE_plotting(PPRE_pp)

tiledlayout('flow')
nexttile
plot(PPRE_pp.scan_axis, PPRE_pp.emittance_x)
title('Horizontal emittance')
xlabel(PPRE_pp.scan_label)
nexttile
plot(PPRE_pp.scan_axis, PPRE_pp.emittance_y)
title('Vertical emittance')
xlabel(PPRE_pp.scan_label)
nexttile
plot(PPRE_pp.scan_axis, PPRE_pp.beam_sizes_P1)
title('Pinhole 1 vertical beamsize')
xlabel(PPRE_pp.scan_label)
nexttile
plot(PPRE_pp.scan_axis, PPRE_pp.beam_sizes_P2)
title('Pinhole 2 vertical beamsize')
xlabel(PPRE_pp.scan_label)
nexttile
plot(PPRE_pp.scan_axis, PPRE_pp.beam_sizes_P3)
title('Pinhole 3 vertical beamsize')
xlabel(PPRE_pp.scan_label)




