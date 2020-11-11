function peakfreq=mbf_pll_blowup_scan(axis,f_range);
switch axis
    case 'X'
        emitPV='HEMIT'
    case 'Y'
        emitPV='VEMIT'
end

f_start=lcaGet(['SR23C-DI-TMBF-01:' axis ':NCO2:FREQ_S']);
f=linspace(f_start-f_range,f_start+f_range,50);
for n=1:length(f)
    lcaPut(['SR23C-DI-TMBF-01:' axis ':NCO2:FREQ_S'],f(n))
    pause(.6)
    emit(n)=lcaGet(['SR-DI-EMIT-01:' emitPV]);
end
lcaPut(['SR23C-DI-TMBF-01:' axis ':NCO2:FREQ_S'],f_start)

[m,m_ind]=max(emit);
peakfreq=f(m_ind);
plot(f,emit,peakfreq,emit(m_ind),'or');
