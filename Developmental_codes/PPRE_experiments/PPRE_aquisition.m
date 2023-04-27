function data_out = PPRE_aquisition(number_of_repeats)
% captures all the required data for a single aquisition
%
% Example:  data_out = PPRE_aquisition

lcaPut('LI-TI-MTGEN-01:BS-DI-MODE', 1);
 while ~strcmp('Fit Forced',lcaGet('SR-DI-EMIT-01:STATUS')) ...
         && ~strcmp('Successful',lcaGet('SR-DI-EMIT-01:STATUS'))
     pause(0.2);
 end
data_out.mbf_data_x = lcaGet('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
data_out.mbf_data_y = lcaGet('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
data_out.pinhole_settings = get_pinhole_settings;

for nds = 1:number_of_repeats
    data_out.pinhole1_images{nds} = get_pinhole_image('SR01C-DI-DCAM-04');
    data_out.pinhole2_images{nds} = get_pinhole_image('SR01C-DI-DCAM-05');
    data_out.beam_sizes{nds}.P1_sigx = lcaGet('SR-DI-EMIT-01:P1:SIGMAX');
    data_out.beam_sizes{nds}.P1_sigy = lcaGet('SR-DI-EMIT-01:P1:SIGMAY');
    data_out.beam_sizes{nds}.P2_sigx = lcaGet('SR-DI-EMIT-01:P2:SIGMAX');
    data_out.beam_sizes{nds}.P2_sigy = lcaGet('SR-DI-EMIT-01:P2:SIGMAY');
    data_out.emittances{nds}.emit = lcaGet('SR-DI-EMIT-01:EMITTANCE');
    data_out.emittances{nds}.coupling = lcaGet('SR-DI-EMIT-01:COUPLING');
    data_out.emittances{nds}.espread = lcaGet('SR-DI-EMIT-01:ESPREAD');
    data_out.emittances{nds}.hemit = lcaGet('SR-DI-EMIT-01:HEMIT');
    data_out.emittances{nds}.veimt = lcaGet('SR-DI-EMIT-01:VEMIT');
    data_out.emittances{nds}.herror = lcaGet('SR-DI-EMIT-01:HERROR');
    data_out.emittances{nds}.verror = lcaGet('SR-DI-EMIT-01:VERROR');
    fprintf([num2str(nds),'. '])
    pause(0.3) % wait for next camera image.
end %for
fprintf('\n')