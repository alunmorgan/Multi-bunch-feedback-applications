function out = single_kick_dataset_capture(nbpms)


out.bpm_TbT_data = get_BPM_TbT_data_XY_only(nbpms);
% out.bpm_FT_data = get_BPM_FT_data_XY_only(nbpms);

% out.mbf_data_x = get_variable('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
% out.mbf_data_y = get_variable('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
