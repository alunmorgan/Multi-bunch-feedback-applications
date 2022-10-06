function out = single_kick_dataset_capture

out.bpm_data = get_BPM_TbT_data;
out.mbf_data_x = lcaGet('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
out.mbf_data_y = lcaGet('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
% out.pinhole_settings = get_pinhole_settings;
% out.pinhole1_image = get_pinhole_image('SR01C-DI-DCAM-04');
% out.pinhole2_image = get_pinhole_image('SR01C-DI-DCAM-05');
% out.beam_sizes = get_beam_sizes;
% out.emittance = get_emittance;