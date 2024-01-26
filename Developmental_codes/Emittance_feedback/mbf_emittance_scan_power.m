function mbf_emittance_scan_power(axis, start_power, stop_power, power_step)
% Scans the excitation across the requested power range
%   Args:
%       axis(str): 'X' or 'Y'
%       start_power(float): power in dB. Lowest value of the scan.
%       stop_power(float): power in dB. Highest value of the scan.
%       power_step(float): power in dB. Step size of the scan.
%
% Example: mbf_emittance_scan_power('X', -50, -10, 5)


switch axis
    case 'X'
        emitPV = 'HEMIT';
    case 'Y'
        emitPV = 'VEMIT';
end

p=linspace(start_power,stop_power,((stop_power - start_power) / power_step) +1 );
set_variable(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],p(1));
pause(30);
emit = NaN(length(p),1);
for n=1:length(p)
    set_variable(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],p(n))
    pause(.6)
    emit(n)=get_variable(['SR-DI-EMIT-01:' emitPV]);
end
set_variable(['SR23C-DI-TMBF-01:' axis ':NCO2:GAIN_DB_S'],-50)


plot(p,emit);

