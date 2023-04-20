function [data_magnitude, data_phase] = mbf_modescan_analysis(modescan)

if ~isfield(modescan, 'harmonic_number')
    modescan.harmonic_number = 936;
end %if

if iscell(modescan.magnitude)
    n_repeats = length(modescan.magnitude);
    for ks = 1:n_repeats
        data_magnitude(:,ks) = squeeze(abs(modescan.magnitude{ks}(1, 1:modescan.harmonic_number)));
        data_phase(:,ks) = squeeze(modescan.phase{ks}(1, 1:modescan.harmonic_number));
        %     phase(:,ks) = unwrap(modescan.phase{ks}/180*pi)/pi*180;
    end %for
else
    % assume a single result
    n_repeats = 1;
    data_magnitude(:,1) = squeeze(abs(modescan.magnitude(1, 1:modescan.harmonic_number)));
    data_phase(:,1) = squeeze(modescan.phase(1, 1:modescan.harmonic_number));
end %if
data_magnitude = sum(data_magnitude,2) ./ n_repeats;
data_phase = sum(data_phase,2) ./ n_repeats;
data_phase = unwrap(data_phase/180*pi)/pi*180;
data_phase = data_phase - data_phase(1);

