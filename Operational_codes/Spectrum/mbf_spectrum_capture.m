function captured_data = mbf_spectrum_capture(input_settings, pv_names)
% captures a set of data from the mbf system runs the analysis.
%
% Args:
%       input_settings(struct): contains all the setup information.
%       pv_names(struct): contains the locations of all the machine parameters.
%
% Example: data = mbf_spectrum_capture(input_settings, pv_names)

mbf_axis = input_settings.mbf_axis;
n_turns = input_settings.n_turns;
repeat = input_settings.repeat;

for k=repeat:-1:1
    % Arm, trigger, read
    if strcmpi(mbf_axis, 's')
        % LMBF hardware
        set_variable([pv_names.hardware_names.L pv_names.tails.triggers.MEM.arm],1);
        set_variable([pv_names.hardware_names.L, pv_names.tails.triggers.soft], 1)
        captured_data{k} = mbf_read_mem(pv_names.hardware_names.L, n_turns,'channel', 0, 'lock', 60);
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


