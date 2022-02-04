function mbf_pll_blowup_scan_power(axis)
switch axis
    case 'X'
        emitPV = 'HEMIT';
    case 'Y'
        emitPV = 'VEMIT';
end

p=linspace(-50,-10,50);
lcaPut(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],p(1));
pause(30);
for n=1:length(p)
    lcaPut(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],p(n))
    pause(.6)
    emit(n)=lcaGet(['SR-DI-EMIT-01:' emitPV]);
end
lcaPut(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],-50)


plot(p,emit);

