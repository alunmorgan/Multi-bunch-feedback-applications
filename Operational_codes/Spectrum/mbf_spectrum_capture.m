function captured_data = mbf_spectrum_capture(mbf_axis, pv_names, n_turns, repeat)
% captures a set of data from the mbf system runs the analysis.
%
% Args:
%       n_turns (str): Number of turns to capture at once. Improves
%                      frequency resolution.
%       repeat (int): Repeat the capture this many times in order to
%                     improve the power resolution.
%
% Example: data = mbf_spectrum_capture('x', pv_names, 1000, 1)


for k=repeat:-1:1
    % Arm, trigger, read
    if strcmpi(mbf_axis, 's')
        % LMBF hardware
        set_variable([pv_names.hardware_names.L pv_names.tails.triggers.MEM.arm],1);
        set_variable([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
        captured_data.s_data{k} = mbf_read_mem(pv_names.hardware_names.L, n_turns,'channel', 0, 'lock', 60);
    else
        % TMBF hardware
        set_variable([pv_names.hardware_names.T pv_names.tails.triggers.MEM.arm],1);
        set_variable([pv_names.hardware_names.T, pv_names.tails.triggers.soft], 1)
        if strcmpi(mbf_axis, 'x')
            captured_data{k} = mbf_read_mem(pv_names.hardware_names.T, n_turns,'channel', 0, 'lock', 60);
        else
            captured_data{k} = mbf_read_mem(pv_names.hardware_names.T, n_turns,'channel', 1, 'lock', 60);
        end%if
    end %if
end %for


