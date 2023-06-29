function mbf_PPRE_plotting(PPRE_pp)
% Plots the 1D scans of the pulse picking by resonant excitation.

if size(PPRE_pp.emittance_x, 1) >1 && size(PPRE_pp.emittance_x, 2) == 1 && size(PPRE_pp.emittance_x, 3) == 1
    scan_axis = PPRE_pp.excitation_gain_axis;
    scan_label = 'Gain';
elseif size(PPRE_pp.emittance_x, 1) ==1 && size(PPRE_pp.emittance_x, 2) > 1 && size(PPRE_pp.emittance_x, 3) == 1
    scan_axis = PPRE_pp.excitation_frequency_axis;
    scan_label = 'Frequency';
elseif size(PPRE_pp.emittance_x, 1) == 1 && size(PPRE_pp.emittance_x, 2) == 1 && size(PPRE_pp.emittance_x, 3) > 1
    scan_axis = PPRE_pp.harmonic_axis;
    scan_label = 'Harmonic';
elseif size(PPRE_pp.emittance_x, 1) == 1 && size(PPRE_pp.emittance_x, 2) == 1 && size(PPRE_pp.emittance_x, 3) == 1
    disp('singular dataset. Nothing to plot.')
    return
else
    disp('Multidimensional data. Cant plot that yet!')
    return
end %if

tiledlayout('flow')
nexttile
plot(scan_axis, PPRE_pp.emittance_x)
title('Horizontal emittance')
xlabel(scan_label)
nexttile
plot(scan_axis, PPRE_pp.emittance_y)
title('Vertical emittance')
xlabel(scan_label)
nexttile
plot(scan_axis, PPRE_pp.beam_sizes_P1)
title('Pinhole 1 vertical beamsize')
xlabel(scan_label)
nexttile
plot(scan_axis, PPRE_pp.beam_sizes_P2)
title('Pinhole 2 vertical beamsize')
xlabel(scan_label)
nexttile
plot(scan_axis, PPRE_pp.beam_sizes_P3)
title('Pinhole 3 vertical beamsize')
xlabel(scan_label)
