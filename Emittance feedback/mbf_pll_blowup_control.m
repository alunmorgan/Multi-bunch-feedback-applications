function mbf_pll_blowup_control(hemit_target,vemit_target)
while true
    hemit=lcaGet('SR-DI-EMIT-01:HEMIT');
    vemit=lcaGet('SR-DI-EMIT-01:VEMIT');
    herror=log10(hemit/hemit_target);
    verror=log10(vemit/vemit_target);
    hpower=lcaGet('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S');
    vpower=lcaGet('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S');
    lcaPut('SR23C-DI-TMBF-01:X:NCO2:GAIN_DB_S',hpower-herror);
    lcaPut('SR23C-DI-TMBF-01:Y:NCO2:GAIN_DB_S',vpower-verror);
    pause(.4)
end
    