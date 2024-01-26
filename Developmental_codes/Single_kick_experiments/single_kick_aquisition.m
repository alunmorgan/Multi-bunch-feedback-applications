function output = single_kick_aquisition(mbf_axis, input_settings)

mbf_name = mbf_axis_to_name(mbf_axis);

for hdr = 1:input_settings.repeat_points
    mbf_single_kick_setup(mbf_axis,...
        'excitation_gain', input_settings.excitation_gain,...
        'excitation_frequency',input_settings.excitation_frequency, ...
        'harmonic', input_settings.harmonic,...
        'delay', input_settings.excitation_delay)
    set_variable([mbf_name, 'TRG:SEQ:ARM_S.PROC'], 1)
    % arm_BPM_TbT_capture(input_settings.BPMs_to_capture)
    BPM_set_switching_off(input_settings.BPMs_to_capture)
    pause(1)
    set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 1);
    % single_kick.bpm_TbT_data = get_BPM_TbT_data_XY_only(input_settings.BPMs_to_capture, bpm_capture_length);
    % single_kick.bpm_FT_data = get_BPM_FT_data_XY_only(input_settings.BPMs_to_capture);
    output.bpm_FR_data{hdr} = get_BPM_FR_data_XY_only(input_settings.BPMs_to_capture);
    BPM_set_switching_on(input_settings.BPMs_to_capture)
end %for