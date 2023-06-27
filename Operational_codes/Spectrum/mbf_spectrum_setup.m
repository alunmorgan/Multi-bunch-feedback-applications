function tunes = mbf_spectrum_setup(mbf_axis)
% sets up the hardware ready to capture data for a spectrum.
% Args:
%       mbf_axis (str): 'x', 'y', 's'. Defines which system you are requesting
%
% Example mbf_spectrum_setup('x')

mbf_tools

[~, ~, pv_names, trigger_inputs] = mbf_system_config;
pv_head = pv_names.hardware_names.(mbf_axis);

% Programatically press the tune only button on each system.
setup_operational_mode(mbf_axis, "TuneOnly")
% Get the tunes
tunes = get_all_tunes('xys');

% Disarm the sequencer and memory triggers
mbf_get_then_put([pv_names.hardware_names.(mbf_axis) pv_names.tails.triggers.SEQ.disarm], 1)
% mbf_get_then_put([system_name pv_names.tails.triggers.MEM.disarm], 1)
mbf_get_then_put([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.disarm], 1)

for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    %     mbf_get_then_put([pv_head pv_names.tails.triggers.MEM.(trigger).enable_status], 'Ignore');
    %     mbf_get_then_put([pv_head pv_names.tails.triggers.MEM.(trigger).blanking_status], 'All');
    mbf_get_then_put([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).enable_status], 'Ignore');
    mbf_get_then_put([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).blanking_status], 'All');

end %for
% Set the trigger to one shot
% mbf_get_then_put([pv_head pv_names.tails.triggers.MEM.mode], 'One Shot');
mbf_get_then_put([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.mode], 'One Shot');

% Set the triggering to External only
% lcaPut([pv_head pv_head pv_names.triggers.MEM.('EXT').enable_status], 'Enable')
lcaPut([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.('EXT').enable_status], 'Enable')

%  set up the memory buffer to capture ADC data.
% mbf_get_then_put([pv_head, pv_head pv_names.MEM.channel_select], 'ADC0/ADC1')
mbf_get_then_put([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.MEM.channel_select], 'ADC0/ADC1')