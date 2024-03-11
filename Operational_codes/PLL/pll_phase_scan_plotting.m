function varargout = pll_phase_scan_plotting(fll_phase_scan)
% Plots the results of a FLL phase scan on the
%multi binch feedback system
%
%   Args:
%       fll_phase_scan(struct): data captured during the phase scan.
%
%   Returns:
%       f1(figure handle):
%
% Example: f1 = fll_phase_scan_plotting(fll_phase_scan)

[~,mi]=max(abs(fll_phase_scan.mag));
peak=fll_phase_scan.phase(mi);
f1 = figure('Position', [50, 100, 1024, 768]);
subplot(1,3,1)
plot(fll_phase_scan.phase, fll_phase_scan.mag, '*')
hold on
plot([peak peak],[min(fll_phase_scan.mag) max(fll_phase_scan.mag)], ':r')
hold off
xlabel('target phase')
ylabel('PLL detected magnitude')
subplot(1,3,2)
plot(fll_phase_scan.phase, fll_phase_scan.f, '*')
xlabel('target phase')
ylabel('PLL detected frequency')
title({'Phase scan of frequency locked loop'; ...
    ['RF frequency = ', num2str(fll_phase_scan.RF)];...
    ['Current = ', num2str(fll_phase_scan.current)]})
subplot(1,3,3)
plot(fll_phase_scan.iq, '*')
xlabel('i')
ylabel('q')

if nargout == 1
    varargout{1} = f1;
end %if