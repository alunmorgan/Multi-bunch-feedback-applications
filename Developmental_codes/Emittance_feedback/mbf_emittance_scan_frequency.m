function peakfreq = mbf_emittance_scan_frequency(mbf_axis, f_range)
% Scans the excitation across the requested frequency range, centred on the
% inital frequency the system is set to.
%   Args:
%       axis(str): 'x' or 'y'
%       frange(float): the frequency range away from the centre value.
%
%   Returns:
%       peakfreq(float): the frequency of the highest value of emittance.
%
% Example: peakfreq = mbf_emittance_scan_frequency(axis, f_range)

mbf_axis = lower(mbf_axis);

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

f_start = get_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency]);
f = linspace(f_start - f_range, f_start + f_range, 50);
emit = NaN(length(f),1);
for n = 1:length(f)
    set_variable([mbf_names.(mbf_axis), mbf_vars.NCO2.frequency], f(n))
    pause(.6)
    emit(n) = get_variable(pv_names.emittance.(mbf_axis));
end
set_variable([mbf_names.(mbf_axis) mbf_vars.NCO2.frequency], f_start)

[~, m_ind] = max(emit);
peakfreq = f(m_ind);
plot(f, emit, peakfreq, emit(m_ind), 'or');

