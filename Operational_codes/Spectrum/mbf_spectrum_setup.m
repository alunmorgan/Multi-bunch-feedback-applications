function mbf_spectrum_setup(input_settings, pv_names)
% sets up the hardware ready to capture data for a spectrum.
% Args:
%       input_settings(struct): contains all the setup information.
%       pv_names(struct): contains the locations of all the machine parameters.
%
% Example mbf_spectrum_setup(input_settings, pv_names, trigger_inputs)

mbf_tools

mbf_axis = input_settings.mbf_axis;
trigger_inputs = pv_names.trigger_inputs;

% Disarm the sequencer (tune measurement) and memory triggers
set_variable([pv_names.hardware_names.(mbf_axis) pv_names.tails.triggers.SEQ.disarm], 1)
set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.disarm], 1)

for trigger_ind = 1:length(trigger_inputs)
    trigger = trigger_inputs{trigger_ind};
    set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).enable_status], 'Ignore');
    set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.(trigger).blanking_status], 'All');
end %for

% Set the trigger to one shot
set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.mode], 'One Shot');

% Set the triggering to External only
set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.triggers.MEM.('EXT').enable_status], 'Enable')

%  set up the memory buffer to capture ADC data.
set_variable([pv_names.hardware_names.mem.(mbf_axis) pv_names.tails.MEM.channel_select], 'ADC0/ADC1')