function plot_pll_data(pll_data)


figure(1);
plot(squeeze(pll_data.maxwf(1,1,:)), 'r', 'DisplayName', 'max');
hold all;
plot(squeeze(pll_data.minwf(1,1,:)), 'g','DisplayName', 'min');
plot(squeeze(pll_data.meanwf(1,1,:)), 'b','DisplayName', 'mean');
hold off
legend
title(['FLL I value = ', num2str(pll_data.i_values(1,1,1))])
ylabel('Tune offset from setpoint')
xlabel(['samples (spacing 4096 * ', num2str(pll_data.dwell), ')'])