function mbf_emittance_scan_power(mbf_axis, start_power, stop_power, power_step)
% Scans the excitation across the requested power range
%   Args:
%       axis(str): 'x' or 'y'
%       start_power(float): power in dB. Lowest value of the scan.
%       stop_power(float): power in dB. Highest value of the scan.
%       power_step(float): power in dB. Step size of the scan.
%
% Example: mbf_emittance_scan_power('X', -50, -10, 5)

mbf_axis = lower(mbf_axis);
[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

p=linspace(start_power,stop_power,((stop_power - start_power) / power_step) +1 );
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db],p(1));
pause(30);
emit = NaN(length(p),1);
for n=1:length(p)
    set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db],p(n))
    pause(.6)
    emit(n)=get_variable(pv_names.emittance.(mbf_axis));
end
set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.gain_db],-50)


plot(p,emit);

