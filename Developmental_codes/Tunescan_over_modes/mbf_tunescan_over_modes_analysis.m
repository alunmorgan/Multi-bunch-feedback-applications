function [data_magnitude, data_phase] = mbf_tunescan_over_modes_analysis(tunescan)

if ~isfield(tunescan, 'harmonic_number')
    tunescan.harmonic_number = 936;
end %if

if iscell(tunescan.magnitude)
    n_repeats = length(tunescan.magnitude);
    for ks = 1:n_repeats
        data_magnitude(:,ks) = squeeze(abs(tunescan.magnitude{ks}(1, 1:tunescan.harmonic_number)));
        data_phase(:,ks) = squeeze(tunescan.phase{ks}(1, 1:tunescan.harmonic_number));
        %     phase(:,ks) = unwrap(tunescan.phase{ks}/180*pi)/pi*180;
    end %for
else
    % assume a single result
    n_repeats = 1;
    data_magnitude(:,1) = squeeze(abs(tunescan.magnitude(1, 1:tunescan.harmonic_number)));
    data_phase(:,1) = squeeze(tunescan.phase(1, 1:tunescan.harmonic_number));
end %if
data_magnitude = sum(data_magnitude,2) ./ n_repeats;
data_phase = sum(data_phase,2) ./ n_repeats;
data_phase = unwrap(data_phase/180*pi)/pi*180;
data_phase = data_phase - data_phase(1);

