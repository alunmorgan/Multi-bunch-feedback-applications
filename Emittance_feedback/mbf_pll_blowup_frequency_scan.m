function peakfreq = mbf_pll_blowup_frequency_scan(name,f_range)
switch name(end-1)
    case 'X'
        emitPV='HEMIT';
    case 'Y'
        emitPV='VEMIT';
end

f_start = lcaGet([name ':NCO2:FREQ_S']);
f = linspace(f_start - f_range,f_start + f_range, 50);
for n = 1:length(f)
    lcaPut([name ':NCO2:FREQ_S'], f(n))
    pause(.6)
    emit(n) = lcaGet(['SR-DI-EMIT-01:' emitPV]);
end
lcaPut([name ':NCO2:FREQ_S'], f_start)

[~, m_ind] = max(emit);
peakfreq = f(m_ind);
plot(f, emit, peakfreq, emit(m_ind), 'or');

