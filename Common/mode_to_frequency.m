function [x_data, data] = mode_to_frequency(RF, harmonic_number, tune, data)
%converts a mode scan into the equivalent frequencies.

x_data_p1 = (RF ./ harmonic_number) .*...
    ((0:(harmonic_number)/2 - 1) + tune);

x_data_p2 = RF - (RF ./ harmonic_number) .*...
    ((harmonic_number / 2):(harmonic_number - 1) + tune);

x_data = cat(2, x_data_p1, x_data_p2);
[x_data, I] = sort(x_data);
data = data(I);
