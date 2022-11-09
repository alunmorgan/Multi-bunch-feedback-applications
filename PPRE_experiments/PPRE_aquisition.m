function data_out = PPRE_aquisition(number_of_repeats)
% captures all the required data for a single aquisition
%
% Example:  data_out = PPRE_aquisition

lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 1);
while ~strcmp('Fit Forced',lcaGet('SR-DI-EMIT-01:STATUS')) && ~strcmp('Successful',lcaGet('SR-DI-EMIT-01:STATUS'))
    pause(0.2);
end
data_out.mbf_data_x = lcaGet('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
data_out.mbf_data_y = lcaGet('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
data_out.pinhole_settings = get_pinhole_settings;
for nds = 1:number_of_repeats
    data_out.pinhole1_images{nds} = get_pinhole_image('SR01C-DI-DCAM-04');
    data_out.pinhole2_images{nds} = get_pinhole_image('SR01C-DI-DCAM-05');
    data_out.beam_sizes{nds} = get_beam_sizes;
    data_out.emittances{nds} = get_emittance;
    pause(0.2) % wait for next camera image.
end %for