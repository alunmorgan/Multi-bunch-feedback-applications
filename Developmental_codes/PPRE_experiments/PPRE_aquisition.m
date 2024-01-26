function data_out = PPRE_aquisition(number_of_repeats)
% captures all the required data for a single aquisition
%
% Example:  data_out = PPRE_aquisition

set_variable('LI-TI-MTGEN-01:BS-DI-MODE', 1);
 while ~strcmp('Fit Forced',get_variable('SR-DI-EMIT-01:STATUS')) ...
         && ~strcmp('Successful',get_variable('SR-DI-EMIT-01:STATUS'))
     pause(0.2);
 end
data_out.mbf_data_x = get_variable('SR23C-DI-TMBF-01:X:ADC:MMS:STD');
data_out.mbf_data_y = get_variable('SR23C-DI-TMBF-01:Y:ADC:MMS:STD');
data_out.pinhole_settings = get_pinhole_settings;

for nds = 1:number_of_repeats
    data_out.pinhole1_images{nds} = get_pinhole_image('SR01C-DI-DCAM-04');
    data_out.pinhole2_images{nds} = get_pinhole_image('SR01C-DI-DCAM-05');
    data_out.beam_sizes{nds}.P1_sigx = get_variable('SR-DI-EMIT-01:P1:SIGMAX');
    data_out.beam_sizes{nds}.P1_sigy = get_variable('SR-DI-EMIT-01:P1:SIGMAY');
    data_out.beam_sizes{nds}.P2_sigx = get_variable('SR-DI-EMIT-01:P2:SIGMAX');
    data_out.beam_sizes{nds}.P2_sigy = get_variable('SR-DI-EMIT-01:P2:SIGMAY');
    data_out.emittances{nds}.emit = get_variable('SR-DI-EMIT-01:EMITTANCE');
    data_out.emittances{nds}.coupling = get_variable('SR-DI-EMIT-01:COUPLING');
    data_out.emittances{nds}.espread = get_variable('SR-DI-EMIT-01:ESPREAD');
    data_out.emittances{nds}.hemit = get_variable('SR-DI-EMIT-01:HEMIT');
    data_out.emittances{nds}.veimt = get_variable('SR-DI-EMIT-01:VEMIT');
    data_out.emittances{nds}.herror = get_variable('SR-DI-EMIT-01:HERROR');
    data_out.emittances{nds}.verror = get_variable('SR-DI-EMIT-01:VERROR');
    fprintf([num2str(nds),'. '])
    pause(0.3) % wait for next camera image.
end %for
fprintf('\n')