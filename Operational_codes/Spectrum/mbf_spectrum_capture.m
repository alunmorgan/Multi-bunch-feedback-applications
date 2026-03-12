function captured_data = mbf_spectrum_capture(n_turns, repeat, pv_names)
% captures a set of data from the mbf system runs the analysis.
%
% Args:
%       n_turns (str): Number of turns to capture at once. Improves
%                      frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
%       pv_names (structure): Allows the construction of the required PVs
%
% Example: data = mbf_spectrum_capture('x')


for k=repeat:-1:1
    % Arm, trigger, read
    % LMBF hardware
    set_variable([pv_names.hardware_names.L pv_names.tails.triggers.MEM.arm],1);
    set_variable([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
    captured_data.s_data{k} = mbf_read_mem(pv_names.hardware_names.L, n_turns,'channel', 0, 'lock', 60);
    % TMBF hardware
    set_variable([pv_names.hardware_names.T pv_names.tails.triggers.MEM.arm],1);
    set_variable([pv_names.hardware_names.T, pv_names.tails.triggers.soft], 1)
    captured_data.x_data{k} = mbf_read_mem(pv_names.hardware_names.T, n_turns,'channel', 0, 'lock', 60);
    captured_data.y_data{k} = mbf_read_mem(pv_names.hardware_names.T, n_turns,'channel', 1, 'lock', 60);
end%for


