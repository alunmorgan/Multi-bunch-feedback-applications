I_value = lcaGet('SR23C-DI-TMBF-01:Y:PLL:CTRL:KI_S');
dwell = lcaGet('SR23C-DI-TMBF-01:Y:PLL:DET:DWELL_S');

n_repeats = 20;
minwf = NaN(n_repeats,1);
maxwf = NaN(n_repeats,1);
meanwf = NaN(n_repeats,1);
stdwf = NaN(n_repeats,1);
tunewf = NaN(n_repeats,1);
offsetwf = NaN(n_repeats,1);

for ewn = 1:n_repeats
    data = lcaGet({'SR23C-DI-TMBF-01:Y:PLL:NCO:OFFSETWF';...
        'SR23C-DI-TMBF-01:Y:PLL:NCO:MEAN_OFFSET';...
        'SR23C-DI-TMBF-01:Y:PLL:NCO:STD_OFFSET';...
        'SR23C-DI-TMBF-01:Y:PLL:NCO:TUNE';...
        'SR23C-DI-TMBF-01:Y:PLL:NCO:OFFSET'});
    wf = data(1,:);
    minwf(ewn) = min(wf);
    maxwf(ewn) = max(wf);
    meanwf(ewn) = data(2,1);
    stdwf(ewn) = data(3,1);
    tunewf(ewn) = data(4,1);
    offsetwf(ewn) = data(5,1);
    pause(1)
    clear data
end %for
save(['/dls/ops-data/Diagnostics/MBF/FLL_investigation/PI_investigation_KI', ...
    num2str(I_value)], 'minwf', 'maxwf', 'meanwf', 'stdwf', ...
    'tunewf', 'offsetwf', 'I_value', 'dwell')
h = figure(1);
plot(maxwf, 'r', 'DisplayName', 'max');
hold all;
plot(minwf, 'g','DisplayName', 'min');
plot(meanwf, 'b','DisplayName', 'mean');
hold off
legend
title(['FLL I value = ', num2str(I_value)])
ylabel('Tune offset from setpoint')
xlabel(['samples (spacing 4096 * ', num2str(dwell), ')'])
saveas(h, ['/dls/ops-data/Diagnostics/MBF/FLL_investigation/PI_investigation_KI',num2str(I_value)])
clear