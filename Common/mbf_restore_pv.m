function mbf_restore_pv(pv_name)
% Finds the file corresponding to the pv_name. Loads this file and sets the
% PV to the value in the file.
%
% Args:
%       pv_name (str): name of the requested process variable.
%
% Example: mbf_restore_pv('SR-DI-MBF-TRIG-01')

[root_string, ~] = mbf_system_config;
load(fullfile(root_string, 'captured_config', pv_name))
lcaPut(pv_name(1:end-4), original_value)


