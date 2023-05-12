function [data_magnitude, data_phase] = mbf_modescan_analysis(modescan)
% Analyses the captured modescan data.
%     Args:
%         modescan (structure): captured data
%     Returns:
%         data_magnitude (vector of floats): averaged signal magnitude over modes.
%         data_phase (vector of floats): averaged signal phase over modes.
%
% Example [data_magnitude, data_phase] = mbf_modescan_analysis(modescan)



n_repeats = length(modescan.magnitude);
data_magnitude_accumulator = NaN(modescan.harmonic_number, n_repeats);
data_phase_accumulator = NaN(modescan.harmonic_number, n_repeats);
for ks = 1:n_repeats
    data_magnitude_accumulator(:,ks) = squeeze(abs(modescan.magnitude{ks}(1, 1:modescan.harmonic_number)));
    data_phase_accumulator(:,ks) = squeeze(modescan.phase{ks}(1, 1:modescan.harmonic_number));
end %for

data_magnitude = sum(data_magnitude_accumulator,2) ./ n_repeats;
data_phase = sum(data_phase_accumulator,2) ./ n_repeats;
data_phase = unwrap(data_phase/180*pi)/pi*180;
data_phase = data_phase - data_phase(1);

