function data_out = PPRE_aquisition(number_of_repeats)
% captures all the required data for a single aquisition
%
% Example:  data_out = PPRE_aquisition

[~, ~, pv_names, ~] = mbf_system_config;
mbf_names = pv_names.hardware_names;
mbf_vars = pv_names.tails;

set_variable(pv_names.Hardware_trigger, 1);
 while ~strcmp('Fit Forced',get_variable(pv_names.emittance.status)) ...
         && ~strcmp('Successful',get_variable(pv_names.emittance.status))
     pause(0.2);
 end
data_out.mbf_data_x = get_variable([mbf_names.x, mbf_vars.adc.std]);
data_out.mbf_data_y = get_variable([mbf_names.y, mbf_vars.adc.std]);
data_out.pinhole_settings = get_pinhole_settings;

for nds = 1:number_of_repeats
    data_out.pinhole1_images{nds} = get_pinhole_image(pv_names.pinhole1);
    data_out.pinhole2_images{nds} = get_pinhole_image(pv_names.pinhole2);
    data_out.beam_sizes{nds}.P1_sigx = get_variable(pv_names.beam_size.pinhole1.sigmax);
    data_out.beam_sizes{nds}.P1_sigy = get_variable(pv_names.beam_size.pinhole1.sigmay);
    data_out.beam_sizes{nds}.P2_sigx = get_variable(pv_names.beam_size.pinhole2.sigmax);
    data_out.beam_sizes{nds}.P2_sigy = get_variable(pv_names.beam_size.pinhole2.sigmay);
    data_out.emittances{nds}.coupling = get_variable(pv_names.coupling.val);
    data_out.emittances{nds}.espread = get_variable(pv_names.energy_spread.val);
    data_out.emittances{nds}.hemit = get_variable(pv_names.emittance.x.val);
    data_out.emittances{nds}.veimt = get_variable(pv_names.emittance.y.val);
    data_out.emittances{nds}.herror = get_variable(pv_names.emittance.x.error);
    data_out.emittances{nds}.verror = get_variable(pv_names.emittance.y.error);
    fprintf([num2str(nds),'. '])
    pause(0.3) % wait for next camera image.
end %for
fprintf('\n')