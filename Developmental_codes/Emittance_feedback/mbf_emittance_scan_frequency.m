function peakfreq = mbf_emittance_scan_frequency(axis, f_range)
% Scans the excitation across the requested frequency range, centred on the
% inital frequency the system is set to.
%   Args:
%       axis(str): 'X' or 'Y'
%       frange(float): the frequency range away from the centre value.
%
%   Returns:
%       peakfreq(float): the frequency of the highest value of emittance.
%
% Example: peakfreq = mbf_emittance_scan_frequency(axis, f_range)

switch axis
    case 'X'
        emitPV='HEMIT';
    case 'Y'
        emitPV='VEMIT';
end

f_start = get_variable(['SR23C-DI-TMBF-01:', axis ':NCO2:FREQ_S']);
f = linspace(f_start - f_range, f_start + f_range, 50);
emit = NaN(length(f),1);
for n = 1:length(f)
    set_variable(['SR23C-DI-TMBF-01:', axis ':NCO2:FREQ_S'], f(n))
    pause(.6)
    emit(n) = get_variable(['SR-DI-EMIT-01:' emitPV]);
end
set_variable(['SR23C-DI-TMBF-01:', axis ':NCO2:FREQ_S'], f_start)

[~, m_ind] = max(emit);
peakfreq = f(m_ind);
plot(f, emit, peakfreq, emit(m_ind), 'or');

