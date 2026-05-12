function [mag_fit, delta, phase_fit] = get_growth(turns, data)

mag_fit = polyfit(turns, log(abs(data)),1);
c1 = polyval(mag_fit, turns);
delta = mean(abs(c1 - log(abs(data)))./c1);
temp = unwrap(angle(data)) / (2*pi);
phase_fit = polyfit(turns, temp, 1);